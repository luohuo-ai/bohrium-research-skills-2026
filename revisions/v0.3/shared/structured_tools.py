#!/usr/bin/env python3
"""Conservative bibliography grouping, provenance graph queries and assertion linting."""
import argparse
import collections
import json
import re
import sys
from research_tools import load_json, save_json


def normalized(value):
    return re.sub(r'[^\w]+', '', str(value).casefold())


def normalize_doi(value):
    if value is None or not str(value).strip():
        return ''
    return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', str(value).strip(), flags=re.I).casefold().rstrip('.,;')


def deduplicate(records):
    if not isinstance(records, list) or not records or any(not isinstance(r, dict) for r in records):
        return {'valid':False,'records':[],'groups':[],'conflicts':[{'reason':'Provide a nonempty list of reference records'}],'candidates':[],'input_records':records}
    output, groups, conflicts, candidates = [], [], [], []
    members=[]
    for record in records:
        doi = normalize_doi(record.get('doi', ''))
        match = None
        for i, previous in enumerate(output):
            same_title = bool(record.get('title')) and normalized(record['title']) == normalized(previous.get('title', ''))
            if doi and doi == normalize_doi(previous.get('doi', '')):
                agrees = same_title and str(record.get('year', '')) == str(previous.get('year', ''))
                if record.get('authors') and previous.get('authors'):
                    agrees = agrees and normalized(record['authors']) == normalized(previous['authors'])
                for member in members[i]:
                    for key in ('title','year','authors'):
                        if record.get(key) and member.get(key) and normalized(record[key]) != normalized(member[key]):
                            agrees=False
                if agrees:
                    match = i
                else:
                    conflicts.append({'ids': [previous.get('id'), record.get('id')], 'doi': doi,
                                      'reason': 'Same DOI but identity fields conflict or are insufficient; do not auto-merge'})
                break
            if same_title:
                candidates.append({'ids': [previous.get('id'), record.get('id')], 'reason': 'Title match alone is not identity proof'})
        if match is None:
            output.append(dict(record))
            groups.append({'canonical_id': record.get('id'), 'member_ids': [record.get('id')], 'reason': 'original record'})
            members.append([record])
        else:
            groups[match]['member_ids'].append(record.get('id'))
            members[match].append(record)
            groups[match]['reason'] = 'Matching DOI and available title/year/author identity fields'
    ids = [r.get('id') for r in records]
    if None in ids or len(set(ids)) != len(ids):
        conflicts.append({'reason': 'Every input record needs a unique stable id'})
    return {'valid': not conflicts, 'records': output, 'groups': groups, 'conflicts': conflicts,
            'candidates': candidates, 'input_records': records,
            'scope': 'Identity grouping only; DOI existence and claim support still require original-source verification'}


def validate_graph(graph):
    if not isinstance(graph, dict) or 'nodes' not in graph or 'edges' not in graph or not isinstance(graph['nodes'], list) or not isinstance(graph['edges'], list):
        return {'valid':False,'errors':['Explicit nodes and edges lists are required'],'node_count':0,'edge_count':0}
    if not graph['nodes'] or any(not isinstance(n,dict) for n in graph['nodes']) or any(not isinstance(e,dict) for e in graph['edges']):
        return {'valid':False,'errors':['Provide real node objects and edge objects; an empty graph is not a positive verification'],'node_count':len(graph['nodes']),'edge_count':len(graph['edges'])}
    errors = []
    nodes, edges = graph.get('nodes', []), graph.get('edges', [])
    ids = [n.get('id') for n in nodes]
    if any(not isinstance(x, str) or not x for x in ids) or len(ids) != len(set(ids)):
        errors.append('Node IDs must be unique nonempty strings')
    known = {x for x in ids if isinstance(x, str)}
    edge_ids = [e['id'] for e in edges if 'id' in e]
    if len(set(edge_ids)) != len(edge_ids):
        errors.append('Duplicate edge IDs')
    for i, edge in enumerate(edges):
        if edge.get('source') not in known or edge.get('target') not in known:
            errors.append(f'edge {i}: missing endpoint')
        if not edge.get('relation'):
            errors.append(f'edge {i}: missing relation')
        if not edge.get('evidence'):
            errors.append(f'edge {i}: missing evidence')
    return {'valid': not errors, 'errors': errors, 'node_count': len(nodes), 'edge_count': len(edges),
            'scope': 'Topology and evidence presence only; verify entity identity, relation direction and evidence entailment'}


def query_graph(graph, subject, relation=None):
    check = validate_graph(graph)
    if not check['valid']:
        return {'status': 'invalid_graph', 'errors': check['errors'], 'nodes': [], 'edges': []}
    edges = [e for e in graph['edges'] if e['source'] == subject and (relation is None or e['relation'] == relation)]
    ids = {subject} | {e['target'] for e in edges}
    return {'status': 'found' if edges else 'not_found', 'subject': subject, 'relation': relation,
            'nodes': [n for n in graph['nodes'] if n['id'] in ids], 'edges': edges,
            'meaning': 'No matching edge means not established in this graph; it is not proof the relation is false'}


def lint_assertions(assertions):
    if not isinstance(assertions, list) or not assertions or any(not isinstance(a,dict) for a in assertions):
        return {'valid':False,'errors':['Provide a nonempty assertion list'],'review_flags':[]}
    errors, flags = [], []
    ids = [a.get('id') for a in assertions]
    if None in ids or len(set(ids)) != len(ids):
        errors.append('Assertions require unique stable IDs')
    for i, item in enumerate(assertions):
        for key in ('assertion', 'subject', 'relation', 'object', 'evidence'):
            if not item.get(key):
                errors.append(f'{i}: missing {key}')
        if re.search(r'\band\b|\bor\b|并且|且|以及|同时', str(item.get('assertion', '')), re.I):
            flags.append({'id': item.get('id'), 'review': 'Possible compound claim: check independently verifiable assertions; conjunction in an entity name alone need not split'})
        if not item.get('conditions'):
            flags.append({'id': item.get('id'), 'review': 'Check whether population, method conditions or qualifiers are missing; never invent them'})
    return {'valid': not errors, 'errors': errors, 'review_flags': flags,
            'scope': 'Local intermediate-schema lint, not a Nanopublication RDF standards validator'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['deduplicate', 'graph-check', 'graph-query', 'assertion-check'])
    p.add_argument('--input', required=True); p.add_argument('--out', required=True)
    p.add_argument('--subject'); p.add_argument('--relation')
    args = p.parse_args()
    try:
        obj = load_json(args.input)
        if args.command == 'deduplicate':
            if isinstance(obj,dict) and 'records' not in obj:
                raise ValueError('Reference wrapper must contain records')
            report = deduplicate(obj['records'] if isinstance(obj, dict) else obj)
        elif args.command == 'graph-check':
            report = validate_graph(obj)
        elif args.command == 'graph-query':
            if not args.subject:
                p.error('--subject is required for graph-query')
            report = query_graph(obj, args.subject, args.relation)
        else:
            if isinstance(obj,dict) and 'assertions' not in obj:
                raise ValueError('Assertion wrapper must contain assertions')
            report = lint_assertions(obj['assertions'] if isinstance(obj, dict) else obj)
        save_json(args.out, report)
        print(json.dumps({'report': args.out, 'valid': report.get('valid'), 'status': report.get('status')}))
        return 2 if report.get('valid') is False or report.get('status') == 'invalid_graph' else 0
    except Exception as exc:
        save_json(args.out, {'status': 'failed', 'error': str(exc)})
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
