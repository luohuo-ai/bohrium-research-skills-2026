#!/usr/bin/env python3
"""Scripted synthetic worked example, not an official case or Agent benchmark."""
import argparse,json,sys
from pathlib import Path
import research_tools as rt
import document_tools as dt
import structured_tools as st
def work(p,out,doc,add):
    report=st.deduplicate(p['records']);rt.save_json(out/'bibliography.json',report)
    mapping={member:g['canonical_id'] for g in report['groups'] for member in g['member_ids']}
    rt.save_json(out/'citation-map.json',mapping)
    add('All identifiers and references below are invented','No real DOI registration or paper existence is asserted.')
    add('10.99999/synthetic.demo.001','The shared invented identifier is an input field, not proof of real DOI registration.');add('Conflicting invented record','The conflicting identity is retained for review.')
    text='# Synthetic bibliography cleaning\n\nThe exact identity duplicates r1 and r2 form one group. r3 has the same invented DOI with conflicting title/year and remains separate for review. DOI existence is not checked; these are synthetic records.\n'
    (out/'bibliography.md').write_text(text,encoding='utf-8')
    return {'artifact':'bibliography.md','records':'bibliography.json','mapping':'citation-map.json','_partial':bool(report['conflicts'])}, {'duplicates_grouped':mapping['r1']==mapping['r2'],'conflict_retained':bool(report['conflicts']) and len(report['records'])==2},['The conflicting record is unresolved; all DOI strings are fictional examples.']

ROOT=Path(__file__).resolve().parents[1]
documents=[]
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True);a=parser.parse_args()
    out=Path(a.out).resolve()
    if out==ROOT or ROOT in out.parents:raise ValueError('Write demonstration artifacts outside the Skill source directory')
    out.mkdir(parents=True,exist_ok=True)
    payload=rt.load_json(ROOT/'examples/worked/input.json');case=rt.load_json(ROOT/'examples/worked/case.json')
    source=out/'source.md';source.write_text(payload['source'],encoding='utf-8');doc=rt.extract_document(source);documents.append(doc)
    evidence=[]
    def add(quote,claim,source=doc):
        segment=next(s for s in source['segments'] if quote in s['text'])
        ident='e'+str(len(evidence)+1)
        evidence.append({'id':ident,'source_id':source['source_id'],'source_sha256':source['sha256'],'segment_id':segment['id'],'quote':quote,'claim':claim,'support':'direct'})
        return ident
    main_result,checks,uncertainty=work(payload,out,doc,add)
    partial=main_result.pop('_partial',False)
    result={'case_id':case['case_id'],'status':'partial' if partial else 'success','main_result':main_result,'sources':[{'source_id':d['source_id'],'sha256':d['sha256'],'file':Path(d['path']).name} for d in documents],'uncertainty':uncertainty,'changes':['Actual scripted transformation of an explicitly synthetic example; no official task performance is claimed.']}
    contract=rt.check_contract(case['output_contract'],result);checks['original_case_id']=result['case_id']==case['case_id']
    ev=rt.check_evidence(documents,evidence)
    rt.save_json(out/'result.json',result);rt.save_json(out/'evidence.json',{'evidence':evidence})
    rt.save_json(out/'source-index.json',documents)
    report={'valid':contract['valid'] and ev['valid'] and all(checks.values()),'task_checks':checks,'contract':contract,'evidence':ev,'scope':'Scripted synthetic micro-example, not model-based/official-case Skill evaluation.'}
    rt.save_json(out/'selfcheck.json',report)
    print(json.dumps({'valid':report['valid'],'status':result['status'],'result':str(out/'result.json'),'scope':report['scope']}))
    return 0 if report['valid'] else 2
if __name__=='__main__':sys.exit(main())
