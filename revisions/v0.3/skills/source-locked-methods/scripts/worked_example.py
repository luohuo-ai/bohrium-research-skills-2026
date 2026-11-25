#!/usr/bin/env python3
"""Scripted synthetic worked example, not an official case or Agent benchmark."""
import argparse,json,sys
from pathlib import Path
import research_tools as rt
import document_tools as dt
def work(p,out,doc,add):
    cfg=p['config'];log=p['run_log']
    text=f"# Synthetic methods and experiment settings\n\nThe invented dataset contains {cfg['total']} records: {cfg['train']} training and {cfg['test']} testing records. No validation partition is reported. The recorded learning rate is {cfg['learning_rate']}, with {cfg['epochs']} epochs.\n\n## Parameter provenance\n\n| Parameter | Configuration | Run log | Decision |\n|---|---|---|---|\n| seed | {cfg['seed']} | {log['seed']} | Conflict: do not select either as verified |\n| epochs | {cfg['epochs']} | {log['epochs']} | Agreement |\n\nNo accuracy, hardware model, software version or repetition count is supplied; no such values are invented. This is an editable partial draft pending seed confirmation.\n"
    (out/'methods.md').write_text(text,encoding='utf-8')
    add('configuration seed=7','The configuration records seed 7.');add('run log seed=11','The run log conflicts with the configuration.');add('60 training and 20 testing','The partition counts are sourced.')
    add('learning_rate=0.001, epochs=5','The learning rate and epoch count come from the configuration.');add('80 records','The total dataset size comes from the configuration.')
    return {'artifact':'methods.md','seed_candidates':[cfg['seed'],log['seed']],'resolved_seed':None,'_partial':cfg['seed']!=log['seed']}, {'counts_consistent':cfg['train']+cfg['test']==cfg['total'],'seed_conflict_retained':str(cfg['seed']) in text and str(log['seed']) in text,'no_result_claim':'No accuracy' in text},['Seed conflict and unreported software/repetitions prevent a fully reproducible account.']

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
