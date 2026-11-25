#!/usr/bin/env python3
"""Scripted synthetic worked example, not an official case or Agent benchmark."""
import argparse,json,sys
from pathlib import Path
import research_tools as rt
import document_tools as dt
import structured_tools as st
def work(p,out,doc,add):
    from rdflib import Dataset
    eid=add('mean yield was 8.2% at 20 °C across 12 replicates','One qualified observation, not a causal claim.')
    assertions=[{'id':'a1','assertion':'The synthetic sample has a reported mean yield of 8.2%.','subject':'urn:synthetic:sample','relation':'reportedMeanYield','object':'8.2%','conditions':{'temperature':'20 °C','replicates':12,'synthetic':True},'evidence':[eid]}]
    rt.save_json(out/'assertions.json',assertions)
    trig='''@prefix this: <https://example.invalid/synthetic-np/> .
@prefix np: <http://www.nanopub.org/nschema#> .
@prefix ex: <https://example.invalid/demo/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
this:head { this:np a np:Nanopublication; np:hasAssertion this:assertion; np:hasProvenance this:provenance; np:hasPublicationInfo this:pubinfo . }
this:assertion { ex:sample ex:reportedMeanYield "8.2"^^xsd:decimal; ex:temperatureCelsius "20"^^xsd:decimal; ex:replicates "12"^^xsd:integer . }
this:provenance { this:assertion prov:wasDerivedFrom ex:syntheticSource . }
this:pubinfo { this:np prov:wasAttributedTo ex:developmentExample; ex:synthetic true . }
'''
    (out/'nanopublication.trig').write_text(trig,encoding='utf-8')
    ds=Dataset();ds.parse(data=trig,format='trig');count=sum(bool(len(g)) for g in ds.graphs())
    return {'artifact':'nanopublication.trig','assertions':'assertions.json','nonempty_named_graphs':count}, {'local_assertion_lint':st.lint_assertions(assertions)['valid'],'trig_parsed':len(ds)>0,'four_named_graphs':count==4},['RDF syntax and this four-graph structure checked; no external publication, signature or full Nanopublication standards certification claimed.']

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
