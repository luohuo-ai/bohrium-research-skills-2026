#!/usr/bin/env python3
"""Portable source extraction and deterministic checks; no model/API calls."""
import argparse
import collections
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _paragraphs(text, prefix, **locator):
    result, lines, start = [], [], None
    for n, line in enumerate(text.splitlines() + [''], 1):
        if line.strip():
            start = n if start is None else start
            lines.append(line)
        elif lines:
            result.append({'id': f'{prefix}:s{len(result)+1:04d}', 'text': '\n'.join(lines),
                           'line_start': start, 'line_end': n-1, **locator})
            start, lines = None, []
    return result


def extract_document(path):
    path = Path(path).resolve()
    if path.suffix.lower() == '.env' or re.search(r'credential|access.?key|token\.txt', path.name, re.I):
        return {'status': 'refused', 'path': str(path), 'reason': 'credential-like input'}
    data = path.read_bytes()
    sha = digest(data)
    source_id = path.stem + ':' + sha[:12]
    result = {'source_id': source_id, 'path': str(path), 'sha256': sha, 'status': 'success',
              'segments': [], 'limitations': [], 'parser': None}
    suffix = path.suffix.lower()
    if suffix == '.pdf':
        try:
            import document_tools
            layout = document_tools.extract_pdf_layout(path)
            result.update(layout)
            result.update(source_id=source_id, path=str(path), sha256=sha)
            for i, segment in enumerate(result['segments']):
                segment['id'] = f'{source_id}:p{segment["page"]:04d}:s{i+1:05d}'
            return result
        except ImportError:
            pass
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            if reader.is_encrypted and not reader.decrypt(''):
                raise ValueError('encrypted PDF; obtain an authorized readable copy')
            result['parser'] = 'pypdf'
            for page, obj in enumerate(reader.pages, 1):
                text = obj.extract_text() or ''
                result['segments'].extend(_paragraphs(text, f'{source_id}:p{page:04d}', page=page))
                if not text.strip():
                    result['limitations'].append(f'Page {page}: no usable text; OCR needed')
            result['limitations'].append('Reading order, tables and formula fidelity need visual verification')
        except Exception as exc:
            result.update(status='failed', limitations=[str(exc)])
    elif suffix == '.docx':
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        with zipfile.ZipFile(path) as archive:
            root = ET.fromstring(archive.read('word/document.xml'))
            paragraphs = [''.join(t.text or '' for t in p.findall('.//w:t', ns))
                          for p in root.findall('.//w:body//w:p', ns)]
        result['parser'] = 'docx-ooxml'
        for n, text in enumerate(paragraphs, 1):
            if text.strip():
                result['segments'].append({'id': f'{source_id}:p{n:05d}', 'paragraph': n, 'text': text})
        result['limitations'].append('Paragraph IDs are OOXML positions, not rendered page numbers; tables require original-cell inspection')
    elif suffix in {'.txt', '.md', '.tex', '.bib', '.ris', '.csv', '.tsv', '.json', '.yaml', '.yml', '.html', '.xml', '.py', '.toml', '.ini'}:
        try:
            text = data.decode('utf-8-sig')
        except UnicodeDecodeError:
            result.update(status='failed', limitations=['Not UTF-8: determine encoding before conversion; do not silently replace characters'])
            return result
        result['parser'] = 'utf8-text'
        result['segments'] = _paragraphs(text, source_id)
    else:
        result.update(status='unsupported', limitations=['Use an actual compatible parser or OCR; no content inferred'])
    if result['status'] == 'success' and result['limitations'] and not result['segments']:
        result['status'] = 'partial'
    return result


NUMBER = re.compile(r'(?<![A-Za-z0-9_])[-+−]?(?:\d+(?:[.,]\d+)*|\.\d+)(?:[eE][-+]?\d+)?%?')
UNITS = re.compile(r'(?<![A-Za-z0-9_])[-+−]?(?:\d+(?:\.\d+)?|\.\d+)\s*(?:%|kg|mg|[µμu]g|g|mL|µL|L|mm|cm|nm|µm|m|ms|s|h|Hz|kHz|MHz|GHz|K|°C|Pa|kPa|MPa|eV|keV|GeV|W|mW|V|mV|A|mA)(?![A-Za-z])')
CITATION = re.compile(r'\\(?:cite\w*|ref|eqref|autoref)\*?(?:\[[^\]]*\])?\{[^}]*\}|\[\s*\d+(?:\s*[-–,;]\s*\d+)*\s*\]|\([A-Z][A-Za-z -]+,\s*\d{4}[a-z]?\)')
MATH = re.compile(r'\$\$.*?\$\$|(?<!\\)\$[^$\n]+\$|\\\[.*?\\\]|\\\(.*?\\\)', re.S)
SEMANTIC = re.compile(r'\b(?:may|might|could|possibly|suggests?|associated|causes?|causal|significant|not|never|only|all|always|must)\b|可能|提示|相关|因果|显著|不|仅|所有', re.I)


def _counter(pattern, text):
    return collections.Counter(re.sub(r'\s+', '', x.replace('−', '-')) for x in pattern.findall(text))


def _difference(a, b):
    return {'removed': list((a-b).elements()), 'added': list((b-a).elements())} if a != b else {}


def audit_text(before, after):
    report = {
        'numeric_changes': _difference(_counter(NUMBER, before), _counter(NUMBER, after)),
        'unit_changes': _difference(_counter(UNITS, before), _counter(UNITS, after)),
        'citation_changes': _difference(_counter(CITATION, before), _counter(CITATION, after)),
        'math_changes': _difference(_counter(MATH, before), _counter(MATH, after)),
        'semantic_review': _difference(_counter(SEMANTIC, before), _counter(SEMANTIC, after)),
    }
    report['valid'] = not any(report[k] for k in ('numeric_changes', 'unit_changes', 'citation_changes', 'math_changes'))
    report['meaning'] = 'Protected-token check only; semantic_review requires source-based judgment, even when valid=true'
    return report


def audit_edits(document, edits):
    sources = {s['id']: s for s in document['segments']}
    counts = collections.Counter(e.get('id') for e in edits)
    issues, audits = [], []
    missing = sorted(set(sources)-set(counts))
    duplicates = sorted(str(k) for k, v in counts.items() if v > 1)
    for edit in edits:
        sid = edit.get('id')
        if sid not in sources:
            issues.append(f'Unknown segment {sid}')
            continue
        after = edit.get('after')
        if not isinstance(after, str) or not after.strip():
            issues.append(f'{sid}: missing output text')
            continue
        if after != sources[sid]['text'] and not str(edit.get('reason', '')).strip():
            issues.append(f'{sid}: changed text without an explanation')
        report = audit_text(sources[sid]['text'], after)
        audits.append({'id': sid, **report})
        if not report['valid']:
            issues.append(f'{sid}: protected facts changed; inspect source or record an explicitly authorized correction')
    return {'valid': not (issues or missing or duplicates), 'missing_ids': missing,
            'duplicate_ids': duplicates, 'issues': issues, 'audits': audits}


def _json_equal(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(_json_equal(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_json_equal(x, y) for x, y in zip(a, b))
    return a == b and (type(a) is type(b) or isinstance(a, (int, float)) and isinstance(b, (int, float)))


def check_contract(contract, result, _as_schema=False):
    errors, unsupported = [], []
    schema_keys = {'type', 'properties', 'required', '$schema', '$id', 'items', 'allOf', 'anyOf', 'oneOf', '$defs', 'definitions', '$ref'}
    annotations = {'title', 'description', 'default', 'examples', '$schema', '$id', '$comment'}
    supported = annotations | {'type', 'properties', 'required', 'items', 'enum', 'const', 'additionalProperties', 'minItems', 'maxItems', 'minLength', 'maxLength', 'minimum', 'maximum', 'pattern', 'allOf', 'anyOf', 'oneOf'}
    types = {'object': dict, 'array': list, 'string': str, 'number': (int, float), 'integer': int, 'boolean': bool, 'null': type(None)}
    def looks_schema(value):
        if not isinstance(value, dict):
            return False
        strong = {'$schema', '$ref', '$defs', 'definitions', 'const'}
        if set(value) & strong:
            return True
        if isinstance(value.get('type'), list) or value.get('type') in types:
            return True
        for k in ('required','allOf','anyOf','oneOf','enum'):
            if isinstance(value.get(k), list):
                return True
        if isinstance(value.get('properties'), dict) or isinstance(value.get('items'), (dict, bool)):
            return True
        if isinstance(value.get('additionalProperties'), (dict, bool)):
            return True
        return any(k in value for k in ('minItems','maxItems','minLength','maxLength','minimum','maximum','pattern'))
    def collect_unsupported(schema, location):
        if isinstance(schema, bool):
            return
        if not isinstance(schema, dict):
            unsupported.append(f'{location}: unrecognized schema')
            return
        for key in schema:
            if key not in supported:
                unsupported.append(f'{location}: keyword {key} not checked')
        if 'properties' in schema:
            if not isinstance(schema['properties'], dict):
                unsupported.append(f'{location}: malformed properties')
            else:
                for key, child in schema['properties'].items():
                    collect_unsupported(child, f'{location}.{key}')
        if 'items' in schema:
            collect_unsupported(schema['items'], location+'[]')
        for union in ('allOf','anyOf','oneOf'):
            if union in schema:
                if not isinstance(schema[union], list):
                    unsupported.append(f'{location}: malformed {union}')
                else:
                    for n, child in enumerate(schema[union]):
                        collect_unsupported(child, f'{location}.{union}[{n}]')
    def validate(schema, value, location):
        if isinstance(schema, bool):
            if not schema:
                errors.append(f'{location}: schema forbids value')
            return
        if not isinstance(schema, dict):
            unsupported.append(f'{location}: unrecognized schema')
            return
        for key in schema:
            if key not in supported:
                unsupported.append(f'{location}: keyword {key} not checked')
        typ = schema.get('type')
        if typ is not None:
            candidates = typ if isinstance(typ, list) else [typ]
            matched = False
            for t in candidates:
                if t not in types:
                    unsupported.append(f'{location}: unknown type {t}')
                    continue
                ok = isinstance(value, types[t])
                if t in ('number', 'integer') and isinstance(value, bool):
                    ok = False
                matched |= ok
            if not matched:
                errors.append(f'{location}: expected {typ}')
                return
        if 'enum' in schema and not any(_json_equal(value, x) for x in schema['enum']):
            errors.append(f'{location}: value outside enum')
        if 'const' in schema and not _json_equal(value, schema['const']):
            errors.append(f'{location}: const mismatch')
        if isinstance(value, dict):
            for key in schema.get('required', []):
                if key not in value:
                    errors.append(f'{location}.{key}: missing required field')
            properties = schema.get('properties', {})
            for key, child in properties.items():
                if key in value:
                    validate(child, value[key], f'{location}.{key}')
            extras = set(value)-set(properties)
            if schema.get('additionalProperties') is False and extras:
                errors.append(f'{location}: extra fields {sorted(extras)}')
            elif isinstance(schema.get('additionalProperties'), dict):
                for key in extras:
                    validate(schema['additionalProperties'], value[key], f'{location}.{key}')
        if isinstance(value, list):
            if len(value) < schema.get('minItems', 0) or len(value) > schema.get('maxItems', float('inf')):
                errors.append(f'{location}: array length outside bounds')
            if 'items' in schema:
                for n, item in enumerate(value):
                    validate(schema['items'], item, f'{location}[{n}]')
        if isinstance(value, str):
            if len(value) < schema.get('minLength', 0) or len(value) > schema.get('maxLength', float('inf')):
                errors.append(f'{location}: string length outside bounds')
            if 'pattern' in schema and not re.search(schema['pattern'], value):
                errors.append(f'{location}: pattern mismatch')
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if value < schema.get('minimum', -float('inf')) or value > schema.get('maximum', float('inf')):
                errors.append(f'{location}: number outside bounds')
        for child in schema.get('allOf', []):
            validate(child, value, location)
        for union in ('anyOf', 'oneOf'):
            if union in schema:
                outcomes = [check_contract(s, value, _as_schema=True) for s in schema[union]]
                if any(not o['validated'] for o in outcomes):
                    unsupported.append(f'{location}: {union} branch not fully checked')
                count = sum(o['valid'] for o in outcomes)
                if not count or (union == 'oneOf' and count != 1):
                    errors.append(f'{location}: {union} not satisfied')
    if _as_schema or looks_schema(contract):
        collect_unsupported(contract, '$')
        validate(contract, result, '$')
    elif isinstance(contract, list) and all(isinstance(x, str) for x in contract):
        for key in contract:
            if not isinstance(result, dict) or key not in result:
                errors.append(f'$.{key}: missing required field')
    elif isinstance(contract, dict) and contract:
        for key, descriptor in contract.items():
            if not isinstance(result, dict) or key not in result:
                errors.append(f'$.{key}: missing required field')
            elif isinstance(descriptor, dict) and looks_schema(descriptor):
                collect_unsupported(descriptor, '$.'+key)
                validate(descriptor, result[key], '$.'+key)
            elif isinstance(descriptor, str) and descriptor in types:
                validate({'type': descriptor}, result[key], '$.'+key)
            else:
                unsupported.append(f'$.{key}: descriptive contract requires manual review')
    else:
        unsupported.append('Unrecognized or absent output contract; inspect the actual task')
    unsupported = list(dict.fromkeys(unsupported))
    return {'valid': not errors and not unsupported, 'validated': not unsupported,
            'errors': errors, 'unchecked': unsupported,
            'scope': 'Structural checks only; scientific/semantic correctness is not certified'}


def check_evidence(documents, entries):
    if not isinstance(documents, list) or not isinstance(entries, list) or not entries:
        return {'valid': False, 'checked_entries': 0, 'errors': ['Provide a nonempty evidence list and actual source extractions']}
    sources = {d['source_id']: d for d in documents}
    errors, trusted, invalid_sources = [], {}, {}
    for sid, source in sources.items():
        try:
            path = Path(source.get('path', ''))
            if source.get('status') not in {'success','partial'}:
                raise ValueError('Extraction status is not usable')
            if not path.is_file():
                raise ValueError('Original source is missing')
            if digest(path.read_bytes()) != source.get('sha256'):
                raise ValueError('Original source changed after extraction')
            fresh = extract_document(path)
            if fresh.get('status') not in {'success','partial'}:
                raise ValueError('Original source cannot currently be extracted')
            trusted[sid] = {s['id']: s for s in fresh['segments']}
        except Exception as exc:
            invalid_sources[sid] = str(exc)
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f'{i}: evidence entry must be an object'); continue
        source = sources.get(entry.get('source_id'))
        if source is None:
            errors.append(f'{i}: unknown source')
            continue
        if entry['source_id'] in invalid_sources:
            errors.append(f'{i}: {invalid_sources[entry["source_id"]]}'); continue
        if not entry.get('source_sha256') or entry['source_sha256'] != source.get('sha256'):
            errors.append(f'{i}: missing or stale source hash')
        segment = trusted.get(entry['source_id'], {}).get(entry.get('segment_id'))
        cached = next((s for s in source.get('segments', []) if s['id'] == entry.get('segment_id')), None)
        if segment and cached and cached.get('text') != segment.get('text'):
            errors.append(f'{i}: cached segment differs from fresh source extraction')
        quote = entry.get('quote', '')
        if segment is None or not isinstance(quote, str) or not quote.strip():
            errors.append(f'{i}: segment or quote missing')
        elif re.sub(r'\s+', ' ', quote).strip() not in re.sub(r'\s+', ' ', segment['text']).strip():
            errors.append(f'{i}: quote not found in the specified source segment')
    return {'valid': not errors, 'checked_entries': len(entries), 'errors': errors,
            'scope': 'Quote existence/hash checks do not establish entailment; compare the claim and its conditions'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('extract'); p.add_argument('--input', required=True); p.add_argument('--out', required=True)
    p = sub.add_parser('audit-text'); p.add_argument('--before', required=True); p.add_argument('--after', required=True); p.add_argument('--out', required=True)
    p = sub.add_parser('audit-edits'); p.add_argument('--document', required=True); p.add_argument('--edits', required=True); p.add_argument('--out', required=True)
    p = sub.add_parser('check-result'); p.add_argument('--case', required=True); p.add_argument('--result', required=True); p.add_argument('--out', required=True)
    p = sub.add_parser('check-evidence'); p.add_argument('--documents', nargs='+', required=True); p.add_argument('--evidence', required=True); p.add_argument('--out', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'extract':
            report = extract_document(Path(args.input))
        elif args.command == 'audit-text':
            report = audit_text(Path(args.before).read_text(encoding='utf-8-sig'), Path(args.after).read_text(encoding='utf-8-sig'))
        elif args.command == 'audit-edits':
            edits = load_json(args.edits)
            report = audit_edits(load_json(args.document), edits.get('edits', []) if isinstance(edits, dict) else edits)
        elif args.command == 'check-result':
            case, result = load_json(args.case), load_json(args.result)
            report = check_contract(case.get('output_contract'), result)
            if 'case_id' in case and result.get('case_id') != case['case_id']:
                report['errors'].append('case_id does not match original input')
                report['valid'] = False
        else:
            entries = load_json(args.evidence)
            if isinstance(entries, dict) and 'evidence' not in entries:
                raise ValueError('Evidence wrapper must contain evidence; refusing an implicit empty check')
            report = check_evidence([load_json(p) for p in args.documents], entries['evidence'] if isinstance(entries, dict) else entries)
        save_json(args.out, report)
        print(json.dumps({'command': args.command, 'report': args.out, 'valid': report.get('valid'), 'status': report.get('status')}, ensure_ascii=True))
        if report.get('valid') is False or report.get('status') in ('failed', 'unsupported', 'refused'):
            return 2
    except Exception as exc:
        save_json(args.out, {'status': 'failed', 'error': str(exc), 'command': args.command})
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
