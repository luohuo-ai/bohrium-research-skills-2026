#!/usr/bin/env python3
"""Scripted synthetic worked example, not an official case or Agent benchmark."""
import argparse,json,sys
from pathlib import Path
import research_tools as rt
import document_tools as dt
def work(p,out,doc,add):
    text='# Synthetic introduction and related work\n\nThe supplied development notes describe two invented studies. S1 examines material A only at 20 °C [S1], whereas S2 compares A and B only at 25 °C [S2]. These sources support different conditions and should not be treated as a controlled head-to-head comparison.\n\nWithin these two supplied notes, cross-temperature generalization is not reported. This is a limitation of the provided evidence, not proof that the wider research field has no such work. We propose to investigate temperature sensitivity; no completed experiment or superiority result is claimed.\n'
    (out/'introduction.md').write_text(text,encoding='utf-8')
    add('S1: material A was studied only at 20 °C','S1 has a limited temperature scope.');add('S2: materials A and B were compared only at 25 °C','S2 is a comparison under a different condition.')
    return {'artifact':'introduction.md','evidence_scope':'Only two synthetic source notes'}, {'two_conditions_kept':'20 °C' in text and '25 °C' in text,'gap_qualified':'provided evidence' in text,'proposal_not_result':'propose' in text},['No external literature search was performed; these are not real publications.']

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
