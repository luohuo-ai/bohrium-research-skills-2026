#!/usr/bin/env python3
"""Scripted synthetic worked example, not an official case or Agent benchmark."""
import argparse,json,sys
from pathlib import Path
import research_tools as rt
import document_tools as dt
def work(p,out,doc,add):
    add('80 participants','Enrolment is 80, not the analysed count.');add('78 were analysed','The analysed denominator is 78.');add('Table 1 instead states 81 enrolled','The enrolled count conflicts across supplied materials.')
    add('r=0.42 at 20 °C','The result retains its statistic and temperature.');add('software version and random seed are not reported','The missing reproducibility details are explicitly stated.')
    text='# Synthetic paper card\n\nQuestion: describe an invented observational pilot.\n\nPopulation: 80 enrolled in the methods prose; Table 1 says 81. Keep both and request resolution. Two exclusions leave 78 analysed according to the results prose; do not silently reconcile this with Table 1.\n\nResult: reported correlation r=0.42 at 20 °C; this observational result does not establish causality.\n\nMissing: randomization method, software version and seed are not reported.\n'
    (out/'notes.md').write_text(text,encoding='utf-8')
    return {'artifact':'notes.md','enrolled_prose':80,'enrolled_table':81,'analysed':78,'_partial':True}, {'conflict_retained':'81' in text and '80' in text,'analysed_count_retained':'78' in text},['Enrolled count conflicts; seed and software are not reported.']

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
