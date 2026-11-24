#!/usr/bin/env python3
"""PDF layout extraction and auditable TeX builds with explicit limitations."""
import argparse
import collections
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path
from research_tools import save_json


def _pdf_lines(words):
    rows = []
    for word in sorted(words, key=lambda w: (w['top'], w['x0'])):
        row = next((r for r in rows[-3:] if abs(r['top']-word['top']) <= 3), None)
        if row is None:
            row = {'top': word['top'], 'words': []}; rows.append(row)
        row['words'].append(word)
    groups = []
    for row in rows:
        current = []
        for word in sorted(row['words'], key=lambda w: w['x0']):
            if current and word['x0']-current[-1]['x1'] > 20:
                groups.append(current); current = []
            current.append(word)
        if current:
            groups.append(current)
    return [{'text': ' '.join(w['text'] for w in group),
             'bbox': [min(w['x0'] for w in group), min(w['top'] for w in group),
                      max(w['x1'] for w in group), max(w['bottom'] for w in group)]} for group in groups]


def _order_lines(lines, width):
    gaps = []
    for left in lines:
        for right in lines:
            if abs(left['bbox'][1]-right['bbox'][1]) <= 3 and right['bbox'][0]-left['bbox'][2] > 24:
                cut = (right['bbox'][0]+left['bbox'][2])/2
                if width*.3 < cut < width*.7:
                    gaps.append(cut)
    if len(gaps) < 3:
        return sorted(lines, key=lambda x: (x['bbox'][1], x['bbox'][0])), 'single_or_undetermined'
    cut = statistics.median(gaps)
    full = sorted([l for l in lines if l['bbox'][0] < cut-5 and l['bbox'][2] > cut+5], key=lambda l:l['bbox'][1])
    remaining = [l for l in lines if l not in full]
    ordered = []
    for divider in full + [None]:
        bottom = divider['bbox'][1] if divider else float('inf')
        band = [l for l in remaining if l['bbox'][1] < bottom]
        for side in (0, 1):
            ordered.extend(sorted([l for l in band if int((l['bbox'][0]+l['bbox'][2])/2 >= cut) == side], key=lambda l:(l['bbox'][1],l['bbox'][0])))
        remaining = [l for l in remaining if l not in band]
        if divider:
            ordered.append(divider)
    return ordered, 'two_column_heuristic'


def extract_pdf_layout(path, max_pages=None):
    try:
        import pdfplumber
    except ImportError:
        from pypdf import PdfReader
        reader = PdfReader(str(path)); segments = []; limits = []
        for n, page in enumerate(reader.pages, 1):
            if max_pages and n > max_pages:
                limits.append(f'Pages after {max_pages} not extracted'); break
            text = page.extract_text() or ''
            if not text.strip():
                limits.append(f'Page {n}: no text layer; OCR required')
            segments.append({'id': f'p{n}', 'page': n, 'text': text, 'bbox': None})
        return {'status': 'partial', 'parser': 'pypdf', 'segments': segments,
                'tables': [], 'limitations': limits+['Geometry, table structure and reading order unverified']}
    segments, tables, limits, page_info = [], [], [], []
    with pdfplumber.open(path) as pdf:
        for n, page in enumerate(pdf.pages, 1):
            if max_pages and n > max_pages:
                limits.append(f'Pages after {max_pages} not extracted'); break
            words = page.extract_words(keep_blank_chars=False, use_text_flow=False)
            if not words:
                limits.append(f'Page {n}: no usable text; render and use a real OCR engine')
                page_info.append({'page': n, 'width': page.width, 'height': page.height, 'words': 0})
                continue
            ordered, method = _order_lines(_pdf_lines(words), page.width)
            for i, line in enumerate(ordered):
                segments.append({'id': f'p{n}:l{i+1}', 'page': n, **line})
            page_info.append({'page': n, 'width': page.width, 'height': page.height, 'words': len(words), 'order': method})
            try:
                for i, table in enumerate(page.find_tables()):
                    tables.append({'id': f'p{n}:table{i+1}', 'page': n, 'bbox': list(table.bbox),
                                   'cells': table.extract(), 'structure_review_required': True})
            except Exception as exc:
                limits.append(f'Page {n}: table extraction failed: {exc}')
    return {'status': 'partial' if limits else 'success', 'parser': 'pdfplumber',
            'segments': segments, 'tables': tables, 'pages': page_info,
            'limitations': limits,
            'review_required': ['Two-column ordering is heuristic; compare rendered pages',
                                'Repeated headers/footers remain in raw segments; classify rather than silently delete',
                                'Merged/continued tables, equation structure and OCR are not certified by extraction success']}


def _tex_without_comments(text):
    return re.sub(r'(?<!\\)%[^\n]*', '', text)


def audit_tex(project):
    labels, refs, cites, includes, errors = [], [], [], [], []
    texfiles=sorted(Path(project).rglob('*.tex')) if Path(project).is_dir() else []
    if not texfiles:
        return {'valid':False,'errors':['Project is missing or has no TeX source files'],'undefined_references':[]}
    for path in texfiles:
        text = _tex_without_comments(path.read_text(encoding='utf-8-sig'))
        labels += re.findall(r'\\label\{([^}]+)\}', text)
        refs += re.findall(r'\\(?:ref|eqref|autoref|pageref)\{([^}]+)\}', text)
        cites += [key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',text) for key in group.split(',')]
        for name in re.findall(r'\\(?:input|include)\{([^}]+)\}', text):
            if not (path.parent/name).exists() and not (path.parent/(name+'.tex')).exists():
                includes.append({'file': str(path), 'input': name})
    duplicate = [k for k,v in collections.Counter(labels).items() if v>1]
    undefined = sorted(set(refs)-set(labels))
    bibkeys = []
    for p in Path(project).rglob('*.bib'):
        bibkeys += re.findall(r'@\w+\s*\{\s*([^,\s]+)\s*,',p.read_text(encoding='utf-8-sig'))
    missing_cites = sorted(set(cites)-set(bibkeys))
    return {'valid': not (duplicate or undefined or includes or missing_cites),
            'duplicate_labels': duplicate, 'undefined_references': undefined,
            'missing_includes': includes, 'unmatched_bib_keys': missing_cites,
            'scope': 'Static heuristics only; macros, generated bibliography and auxiliary files need actual compilation'}


def build_tex(project, main, out, engine=None, timeout=120):
    project, out = Path(project).resolve(), Path(out).resolve()
    main_path = (project/main).resolve()
    if not main_path.is_relative_to(project) or not main_path.is_file():
        return {'status': 'failed', 'reason': 'Main file missing or outside project'}
    chosen = engine or next((e for e in ('latexmk','xelatex','pdflatex','lualatex') if shutil.which(e)), None)
    executable = shutil.which(chosen) if chosen else None
    if not executable:
        return {'status': 'missing_tool', 'requested_engine': chosen,
                'reason': 'No actual TeX compiler found; no PDF claimed'}
    basename = Path(executable).stem.lower()
    if basename not in {'latexmk','pdflatex','xelatex','lualatex'}:
        return {'status': 'unsupported_engine', 'engine': executable, 'reason': 'Use the actual documented compiler invocation manually and retain its logs'}
    out.mkdir(parents=True, exist_ok=True)
    build = Path(tempfile.mkdtemp(prefix='tex-build-', dir=out))
    source = build/'src'; products = build/'products'; products.mkdir()
    def ignore(directory, names):
        return [n for n in names if n in {'.git','__pycache__'} or (Path(directory)/n).resolve().is_relative_to(build)]
    shutil.copytree(project, source, ignore=ignore)
    command = [executable]
    if basename == 'latexmk':
        command += ['-pdf','-latexoption=-no-shell-escape','-interaction=nonstopmode','-halt-on-error',f'-outdir={products}',main]
        passes = 1
    else:
        command += ['-no-shell-escape','-interaction=nonstopmode','-halt-on-error',f'-output-directory={products}',main]
        passes = 2
    runs = []
    for n in range(passes):
        try:
            run = subprocess.run(command,cwd=source,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout,check=False)
            log = build/f'pass-{n+1}.log';log.write_text(run.stdout+'\n'+run.stderr,encoding='utf-8')
            runs.append({'command':command,'exit_code':run.returncode,'log':str(log)})
            if run.returncode:
                return {'status':'failed','runs':runs,'workspace':str(build)}
        except subprocess.TimeoutExpired:
            return {'status':'timeout','runs':runs,'workspace':str(build),'reason':'Actual compiler exceeded the per-pass limit'}
    pdf = products/(Path(main).stem+'.pdf')
    if not pdf.is_file() or pdf.stat().st_size == 0:
        return {'status':'failed','runs':runs,'reason':'Compiler did not produce a new nonempty PDF','workspace':str(build)}
    logs='\n'.join(Path(r['log']).read_text(encoding='utf-8') for r in runs)
    warnings=[s for s in logs.splitlines() if re.search(r'undefined|Overfull|Missing character|Rerun to get',s,re.I)]
    return {'status':'partial' if warnings else 'success','pdf':str(pdf),'runs':runs,'warnings':warnings,
            'workspace':str(build),'review_required':'Render this actual PDF and inspect layout; successful compilation alone does not certify fidelity'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    s=p.add_subparsers(dest='command',required=True)
    q=s.add_parser('pdf');q.add_argument('--input',required=True);q.add_argument('--max-pages',type=int);q.add_argument('--out',required=True)
    q=s.add_parser('tex-audit');q.add_argument('--project',required=True);q.add_argument('--out',required=True)
    q=s.add_parser('tex-build');q.add_argument('--project',required=True);q.add_argument('--main',required=True);q.add_argument('--output-dir',required=True);q.add_argument('--engine');q.add_argument('--timeout',type=int,default=120);q.add_argument('--out',required=True)
    a=p.parse_args()
    try:
        if a.command=='pdf':r=extract_pdf_layout(Path(a.input),a.max_pages)
        elif a.command=='tex-audit':r=audit_tex(Path(a.project))
        else:r=build_tex(Path(a.project),a.main,Path(a.output_dir),a.engine,a.timeout)
        save_json(a.out,r);print({'report':a.out,'status':r.get('status'),'valid':r.get('valid')})
        return 2 if r.get('valid') is False or r.get('status') in {'failed','missing_tool','unsupported_engine','timeout'} else 0
    except Exception as exc:
        save_json(a.out,{'status':'failed','error':str(exc)});print(str(exc),file=sys.stderr);return 2


if __name__=='__main__':sys.exit(main())
