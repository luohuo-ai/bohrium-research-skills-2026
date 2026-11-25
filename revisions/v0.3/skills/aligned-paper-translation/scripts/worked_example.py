#!/usr/bin/env python3
"""Scripted synthetic worked example, not an official case or Agent benchmark."""
import argparse,json,sys
from pathlib import Path
import research_tools as rt
import document_tools as dt
def work(p,out,doc,add):
    translated='在20 °C下，12次重复试验的平均产率为8.2% [1]。这一观察可能与处理条件有关，但不能确立因果关系。'
    text='## Original\n\n'+p['source']+'\n\n## Translation\n\n'+translated+'\n\n## Terminology\n\nmean yield：平均产率；replicates：重复试验；associated：有关。\n'
    (out/'translation.md').write_text(text,encoding='utf-8')
    add('mean yield of 8.2%','The measured quantity is translated as mean yield.');add('does not establish causality','The causal limitation is preserved.')
    return {'artifact':'translation.md','translated_span':translated}, {'protected_tokens':rt.audit_text(p['source'],translated)['valid'],'negation_and_hedge_manually_checked':True},['[1] is an explicitly fictional development citation.']

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
