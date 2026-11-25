#!/usr/bin/env python3
"""Scripted synthetic worked example, not an official case or Agent benchmark."""
import argparse,json,sys
from pathlib import Path
import research_tools as rt
import document_tools as dt
import structured_tools as st
def work(p,out,doc,add):
    e1=add('Study S1 uses material A','The usage edge is sourced.');e2=add('Material A has a mean yield of 8.2% at 20 °C','The yield edge retains its condition.')
    graph={'nodes':[{'id':'S1','label':'Synthetic study S1'},{'id':'A','label':'Material A'},{'id':'Y','label':'Mean yield 8.2%'}],'edges':[{'id':'e1','source':'S1','target':'A','relation':'uses','evidence':[e1]},{'id':'e2','source':'A','target':'Y','relation':'reported_mean_yield','conditions':{'temperature':'20 °C'},'evidence':[e2]}]}
    q1=st.query_graph(graph,'A','reported_mean_yield')
    first=st.query_graph(graph,'S1','uses');targets={e['target'] for e in first['edges']}
    second=[e for e in graph['edges'] if e['source'] in targets]
    q2={'path_edges':first['edges']+second,'description':'Two-hop provenance-preserving traversal, not causal inference.'}
    q3=[{'edge':e['id'],'evidence':e['evidence']} for e in graph['edges'] if e.get('conditions',{}).get('temperature')=='20 °C']
    rt.save_json(out/'graph.json',graph);rt.save_json(out/'queries.json',{'relation_query':q1,'two_hop_query':q2,'condition_provenance_query':q3})
    return {'artifact':'graph.json','queries':'queries.json','query_types':3}, {'topology':st.validate_graph(graph)['valid'],'relation_query_has_source':bool(q1['edges']),'two_hop':len(q2['path_edges'])==2,'condition_query':len(q3)==1},['This tiny synthetic graph does not establish real-world entity identity or query recall.']

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
