#!/usr/bin/env python3
"""Scripted synthetic worked example, not an official case or Agent benchmark."""
import argparse,json,sys
from pathlib import Path
import research_tools as rt
import document_tools as dt
def work(p,out,doc,add):
    from reportlab.pdfgen import canvas
    actual=out/'synthetic-input.pdf';c=canvas.Canvas(str(actual),pagesize=(600,800))
    c.setFont('Helvetica',14);c.drawCentredString(300,760,'SYNTHETIC TWO-COLUMN DEMO')
    c.setFont('Helvetica',11)
    for i,line in enumerate(p['left']):c.drawString(45,700-i*28,line)
    for i,line in enumerate(p['right']):c.drawString(335,700-i*28,line)
    c.save();extracted=rt.extract_document(actual);documents.append(extracted)
    rt.save_json(out/'layout.json',extracted)
    lines=[s['text'] for s in extracted['segments']];text='\n\n'.join(lines)
    (out/'parsed.md').write_text('# Actual extraction of synthetic PDF\n\n'+text,encoding='utf-8')
    add('LEFT A: 12 replicates','The parsed count is anchored in the actual generated PDF.',extracted)
    add('RIGHT A: yield 8.2 percent','The parsed yield is anchored in the actual generated PDF.',extracted)
    left=next(i for i,s in enumerate(lines) if 'LEFT D:' in s);right=next(i for i,s in enumerate(lines) if 'RIGHT A:' in s)
    return {'artifact':'parsed.md','layout':'layout.json','input':'synthetic-input.pdf','parser':extracted['parser'],'segments':len(lines)}, {'left_before_right':left<right,'page_anchors':all(s.get('page')==1 for s in extracted['segments']),'real_bboxes':all(s.get('bbox') for s in extracted['segments'])},['Only this synthetic two-column layout is tested; OCR, cross-page tables and formula transcription are outside this example.']

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
