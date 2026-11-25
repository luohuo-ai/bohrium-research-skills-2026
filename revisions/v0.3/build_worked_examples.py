"""Build an isolated candidate; never alter frozen submissions or call a model/service."""
import argparse,hashlib,inspect,json,shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
DEST=HERE
ORIGINAL=HERE

def polish(p,out,doc,add):
    edits=[]
    for segment in doc['segments']:
        after=segment['text'].replace('The catalyst were','The catalyst was').replace('The observations suggests','The observations suggest')
        edits.append({'id':segment['id'],'after':after,'change_type':'grammar' if after!=segment['text'] else 'unchanged','reason':'Correct subject-verb agreement; retain quantities and qualifiers.' if after!=segment['text'] else 'No change needed.'})
    text='\n\n'.join(x['after'] for x in edits);(out/'polished.md').write_text(text,encoding='utf-8')
    rt.save_json(out/'edits.json',edits)
    add('8.2%','The numerical observation is retained.');add('may be associated','The association remains qualified.')
    return {'artifact':'polished.md','edits':'edits.json'}, {'alignment':rt.audit_edits(doc,edits)['valid'],'protected_tokens':rt.audit_text(p['source'],text)['valid']},[]

def notes(p,out,doc,add):
    add('80 participants','Enrolment is 80, not the analysed count.');add('78 were analysed','The analysed denominator is 78.');add('Table 1 instead states 81 enrolled','The enrolled count conflicts across supplied materials.')
    add('r=0.42 at 20 °C','The result retains its statistic and temperature.');add('software version and random seed are not reported','The missing reproducibility details are explicitly stated.')
    text='# Synthetic paper card\n\nQuestion: describe an invented observational pilot.\n\nPopulation: 80 enrolled in the methods prose; Table 1 says 81. Keep both and request resolution. Two exclusions leave 78 analysed according to the results prose; do not silently reconcile this with Table 1.\n\nResult: reported correlation r=0.42 at 20 °C; this observational result does not establish causality.\n\nMissing: randomization method, software version and seed are not reported.\n'
    (out/'notes.md').write_text(text,encoding='utf-8')
    return {'artifact':'notes.md','enrolled_prose':80,'enrolled_table':81,'analysed':78,'_partial':True}, {'conflict_retained':'81' in text and '80' in text,'analysed_count_retained':'78' in text},['Enrolled count conflicts; seed and software are not reported.']

def translation(p,out,doc,add):
    translated='在20 °C下，12次重复试验的平均产率为8.2% [1]。这一观察可能与处理条件有关，但不能确立因果关系。'
    text='## Original\n\n'+p['source']+'\n\n## Translation\n\n'+translated+'\n\n## Terminology\n\nmean yield：平均产率；replicates：重复试验；associated：有关。\n'
    (out/'translation.md').write_text(text,encoding='utf-8')
    add('mean yield of 8.2%','The measured quantity is translated as mean yield.');add('does not establish causality','The causal limitation is preserved.')
    return {'artifact':'translation.md','translated_span':translated}, {'protected_tokens':rt.audit_text(p['source'],translated)['valid'],'negation_and_hedge_manually_checked':True},['[1] is an explicitly fictional development citation.']

def citations(p,out,doc,add):
    report=st.deduplicate(p['records']);rt.save_json(out/'bibliography.json',report)
    mapping={member:g['canonical_id'] for g in report['groups'] for member in g['member_ids']}
    rt.save_json(out/'citation-map.json',mapping)
    add('All identifiers and references below are invented','No real DOI registration or paper existence is asserted.')
    add('10.99999/synthetic.demo.001','The shared invented identifier is an input field, not proof of real DOI registration.');add('Conflicting invented record','The conflicting identity is retained for review.')
    text='# Synthetic bibliography cleaning\n\nThe exact identity duplicates r1 and r2 form one group. r3 has the same invented DOI with conflicting title/year and remains separate for review. DOI existence is not checked; these are synthetic records.\n'
    (out/'bibliography.md').write_text(text,encoding='utf-8')
    return {'artifact':'bibliography.md','records':'bibliography.json','mapping':'citation-map.json','_partial':bool(report['conflicts'])}, {'duplicates_grouped':mapping['r1']==mapping['r2'],'conflict_retained':bool(report['conflicts']) and len(report['records'])==2},['The conflicting record is unresolved; all DOI strings are fictional examples.']

def methods(p,out,doc,add):
    cfg=p['config'];log=p['run_log']
    text=f"# Synthetic methods and experiment settings\n\nThe invented dataset contains {cfg['total']} records: {cfg['train']} training and {cfg['test']} testing records. No validation partition is reported. The recorded learning rate is {cfg['learning_rate']}, with {cfg['epochs']} epochs.\n\n## Parameter provenance\n\n| Parameter | Configuration | Run log | Decision |\n|---|---|---|---|\n| seed | {cfg['seed']} | {log['seed']} | Conflict: do not select either as verified |\n| epochs | {cfg['epochs']} | {log['epochs']} | Agreement |\n\nNo accuracy, hardware model, software version or repetition count is supplied; no such values are invented. This is an editable partial draft pending seed confirmation.\n"
    (out/'methods.md').write_text(text,encoding='utf-8')
    add('configuration seed=7','The configuration records seed 7.');add('run log seed=11','The run log conflicts with the configuration.');add('60 training and 20 testing','The partition counts are sourced.')
    add('learning_rate=0.001, epochs=5','The learning rate and epoch count come from the configuration.');add('80 records','The total dataset size comes from the configuration.')
    return {'artifact':'methods.md','seed_candidates':[cfg['seed'],log['seed']],'resolved_seed':None,'_partial':cfg['seed']!=log['seed']}, {'counts_consistent':cfg['train']+cfg['test']==cfg['total'],'seed_conflict_retained':str(cfg['seed']) in text and str(log['seed']) in text,'no_result_claim':'No accuracy' in text},['Seed conflict and unreported software/repetitions prevent a fully reproducible account.']

def introduction(p,out,doc,add):
    text='# Synthetic introduction and related work\n\nThe supplied development notes describe two invented studies. S1 examines material A only at 20 °C [S1], whereas S2 compares A and B only at 25 °C [S2]. These sources support different conditions and should not be treated as a controlled head-to-head comparison.\n\nWithin these two supplied notes, cross-temperature generalization is not reported. This is a limitation of the provided evidence, not proof that the wider research field has no such work. We propose to investigate temperature sensitivity; no completed experiment or superiority result is claimed.\n'
    (out/'introduction.md').write_text(text,encoding='utf-8')
    add('S1: material A was studied only at 20 °C','S1 has a limited temperature scope.');add('S2: materials A and B were compared only at 25 °C','S2 is a comparison under a different condition.')
    return {'artifact':'introduction.md','evidence_scope':'Only two synthetic source notes'}, {'two_conditions_kept':'20 °C' in text and '25 °C' in text,'gap_qualified':'provided evidence' in text,'proposal_not_result':'propose' in text},['No external literature search was performed; these are not real publications.']

def pdf(p,out,doc,add):
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

def nanopub(p,out,doc,add):
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

def graph(p,out,doc,add):
    e1=add('Study S1 uses material A','The usage edge is sourced.');e2=add('Material A has a mean yield of 8.2% at 20 °C','The yield edge retains its condition.')
    graph={'nodes':[{'id':'S1','label':'Synthetic study S1'},{'id':'A','label':'Material A'},{'id':'Y','label':'Mean yield 8.2%'}],'edges':[{'id':'e1','source':'S1','target':'A','relation':'uses','evidence':[e1]},{'id':'e2','source':'A','target':'Y','relation':'reported_mean_yield','conditions':{'temperature':'20 °C'},'evidence':[e2]}]}
    q1=st.query_graph(graph,'A','reported_mean_yield')
    first=st.query_graph(graph,'S1','uses');targets={e['target'] for e in first['edges']}
    second=[e for e in graph['edges'] if e['source'] in targets]
    q2={'path_edges':first['edges']+second,'description':'Two-hop provenance-preserving traversal, not causal inference.'}
    q3=[{'edge':e['id'],'evidence':e['evidence']} for e in graph['edges'] if e.get('conditions',{}).get('temperature')=='20 °C']
    rt.save_json(out/'graph.json',graph);rt.save_json(out/'queries.json',{'relation_query':q1,'two_hop_query':q2,'condition_provenance_query':q3})
    return {'artifact':'graph.json','queries':'queries.json','query_types':3}, {'topology':st.validate_graph(graph)['valid'],'relation_query_has_source':bool(q1['edges']),'two_hop':len(q2['path_edges'])==2,'condition_query':len(q3)==1},['This tiny synthetic graph does not establish real-world entity identity or query recall.']

def latex(p,out,doc,add):
    project=out/'tex-project';project.mkdir(exist_ok=True);main=project/'main.tex'
    main.write_text(p['tex'],encoding='utf-8');before=dt.audit_tex(project)
    fixed=p['tex'].replace(r'\ref{sec:methd}',r'\ref{sec:methods}')
    main.write_text(fixed,encoding='utf-8');after=dt.audit_tex(project)
    rt.save_json(out/'before-audit.json',before);rt.save_json(out/'after-audit.json',after)
    build=dt.build_tex(project,'main.tex',out/'tex-build',timeout=45);rt.save_json(out/'build.json',build)
    add('The intended section label is sec:methods','The requested deterministic correction has a supplied target.')
    return {'artifact':'tex-project/main.tex','before':'before-audit.json','after':'after-audit.json','build':'build.json','build_status':build['status'],'_partial':build['status']!='success'}, {'missing_label_detected':'sec:methd' in before['undefined_references'],'fixed_static_audit':after['valid'],'math_retained':r'$x^2$' in fixed},['Static reference repair verified; actual compilation/preview is '+build['status']+'. No absent compiler or PDF is claimed as successful.']

MODES={'academic-polish':polish,'evidence-notes':notes,'aligned-paper-translation':translation,'auditable-citations':citations,'source-locked-methods':methods,'evidence-first-introduction':introduction,'traceable-pdf-structure':pdf,'sourced-nanopublications':nanopub,'provenance-literature-graph':graph,'verified-latex-repair':latex}
PAYLOADS={
'academic-polish':{'source':'The catalyst were tested at 20 °C in 12 replicates and gave a mean yield of 8.2% [1].\n\nThe observations suggests that yield may be associated with the condition; this does not establish causality.'},
'evidence-notes':{'source':'Synthetic observational pilot; no real participants or study.\n\nMethods: 80 participants were enrolled.\n\nResults: two were excluded and 78 were analysed. The reported correlation was r=0.42 at 20 °C.\n\nTable 1 instead states 81 enrolled.\n\nRandomization method, software version and random seed are not reported.'},
'aligned-paper-translation':{'source':'At 20 °C, 12 replicates gave a mean yield of 8.2% [1]. This observation may be associated with the condition but does not establish causality.'},
'auditable-citations':{'source':'All identifiers and references below are invented for development, not real publications. r1 and r2 have identical identity fields. r3 intentionally conflicts.','records':[{'id':'r1','doi':'10.99999/synthetic.demo.001','title':'Invented study of A','year':2026,'authors':['Synthetic Author']},{'id':'r2','doi':'https://doi.org/10.99999/synthetic.demo.001','title':'Invented study of A','year':2026,'authors':['Synthetic Author']},{'id':'r3','doi':'10.99999/synthetic.demo.001','title':'Conflicting invented record','year':2025,'authors':['Another Synthetic Author']}]},
'source-locked-methods':{'source':'Synthetic configuration and logs, not measured research.\n\nConfiguration: 80 records, 60 training and 20 testing; learning_rate=0.001, epochs=5, configuration seed=7.\n\nRun log: epochs=5, run log seed=11.\n\nNo validation split, accuracy, software version, hardware or repetition count is supplied.','config':{'total':80,'train':60,'test':20,'learning_rate':0.001,'epochs':5,'seed':7},'run_log':{'epochs':5,'seed':11}},
'evidence-first-introduction':{'source':'These source notes are invented and do not describe real publications.\n\nS1: material A was studied only at 20 °C.\n\nS2: materials A and B were compared only at 25 °C.\n\nProposal: investigate temperature sensitivity. No experiment has yet been conducted.'},
'traceable-pdf-structure':{'source':'Create and parse a synthetic two-column PDF. The developer-generated layout is not an official case. Check reading order and real page/block anchors only.','left':['LEFT A: 12 replicates','LEFT B: temperature 20 C','LEFT C: source is synthetic','LEFT D: end of left column'],'right':['RIGHT A: yield 8.2 percent','RIGHT B: no causal claim','RIGHT C: no actual experiment','RIGHT D: end of right column']},
'sourced-nanopublications':{'source':'This is an invented development observation, not real research.\n\nIn the synthetic sample the mean yield was 8.2% at 20 °C across 12 replicates. No causal effect is established.'},
'provenance-literature-graph':{'source':'All entities and results are invented for development.\n\nStudy S1 uses material A.\n\nMaterial A has a mean yield of 8.2% at 20 °C.\n\nThe observation does not establish causality.'},
'verified-latex-repair':{'source':'Synthetic TeX repair request. The intended section label is sec:methods. Repair the misspelled reference while retaining the formula. Report any absent compiler honestly.','tex':'\\documentclass{article}\n\\begin{document}\n\\section{Methods}\\label{sec:methods}\nSee Section~\\ref{sec:methd}. Preserve $x^2$.\n\\end{document}\n'}
}

HEADER='''#!/usr/bin/env python3
"""Scripted synthetic worked example, not an official case or Agent benchmark."""
import argparse,json,sys
from pathlib import Path
import research_tools as rt
import document_tools as dt
'''
FOOTER='''
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
'''

PROBE='''#!/usr/bin/env python3
"""Read-only dependency probe; does not install packages or call a service."""
import argparse,importlib.util,importlib.metadata,json,shutil,sys
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--require-pdf',action='store_true');p.add_argument('--require-rdf',action='store_true');p.add_argument('--require-tex',action='store_true');a=p.parse_args()
packages={}
for name in ['pdfplumber','pypdf','reportlab','rdflib']:
    available=importlib.util.find_spec(name) is not None
    try:version=importlib.metadata.version(name) if available else None
    except importlib.metadata.PackageNotFoundError:version=None
    packages[name]={'available':available,'version':version}
compiler=next((x for x in ['latexmk','xelatex','pdflatex','lualatex'] if shutil.which(x)),None)
ok=sys.version_info>=(3,10)
if a.require_pdf:ok=ok and packages['pdfplumber']['available']
if a.require_rdf:ok=ok and packages['rdflib']['available']
if a.require_tex:ok=ok and compiler is not None
print(json.dumps({'python':sys.version.split()[0],'minimum_python':'3.10','packages':packages,'tex_engine':compiler,'required_capabilities_available':bool(ok),'scope':'Optional missing components are not a successful execution of those features.'}))
sys.exit(0 if ok else 2)
'''

def build():
    DEST.mkdir(parents=True,exist_ok=True)
    for folder in ['shared','tests','docs']:
        if (ORIGINAL/folder).resolve()!=(DEST/folder).resolve():shutil.copytree(ORIGINAL/folder,DEST/folder,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','.test-tmp','*.pyc'))
    for name in ['build_suite.py','export_development_trace.py','README.md']:
        if (ORIGINAL/name).resolve()!=(DEST/name).resolve():shutil.copyfile(ORIGINAL/name,DEST/name)
    if Path(__file__).resolve()!=(DEST/'build_worked_examples.py').resolve():shutil.copyfile(Path(__file__),DEST/'build_worked_examples.py')
    import importlib.util
    spec=importlib.util.spec_from_file_location('candidate_build',DEST/'build_suite.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.build(DEST/'skills')
    manifest=[]
    for task in module.TASKS:
        key=task['key'];folder=DEST/'skills'/key;example=folder/'examples/worked';example.mkdir(parents=True,exist_ok=True)
        code=HEADER+('import structured_tools as st\n' if key in ['auditable-citations','sourced-nanopublications','provenance-literature-graph'] else '')
        code+=inspect.getsource(MODES[key]).replace('def '+MODES[key].__name__+'(', 'def work(',1)+FOOTER
        (folder/'scripts/worked_example.py').write_text(code,encoding='utf-8');(folder/'scripts/dependency_probe.py').write_text(PROBE,encoding='utf-8')
        payload=dict(PAYLOADS[key])
        if key=='auditable-citations':payload['source']+='\n\n'+json.dumps(payload['records'],ensure_ascii=False,indent=2)
        (example/'input.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
        schema={'type':'object','required':['case_id','status','main_result','sources','uncertainty','changes'],'properties':{'case_id':{'type':'string'},'status':{'enum':['success','partial']},'main_result':{'type':'object'},'sources':{'type':'array','minItems':1},'uncertainty':{'type':'array'},'changes':{'type':'array'}}}
        case={'case_id':'synthetic-worked-'+key,'notice':'Synthetic developer micro-case only. Not an official case or benchmark.','task':task['deliver'],'output_contract':schema}
        (example/'case.json').write_text(json.dumps(case,ensure_ascii=False,indent=2),encoding='utf-8')
        (example/'README.md').write_text(f'''# Runnable synthetic worked example

This is a scripted micro-example for {task['title']}. It produces actual task-specific artifacts, source quotes and structural checks. It does not run a language model or compare Agent performance, and is not a fixed official case.

From this Skill root, first inspect [environment notes](../../references/environment.md), then run:

```sh
python3 scripts/worked_example.py --out /app/work/{key}-worked
```

Read result.json, the named main artifacts, evidence.json and selfcheck.json in that output directory. A partial result can be the correct behavior for contradictory/missing evidence or absent tools; inspect its uncertainty and build status. A green local selfcheck certifies only the specified synthetic checks, not official scientific quality.

The original examples/result.example.json remains an explicitly illustrative interface shape. This worked example is a separate concrete transformation. Never submit its synthetic artifacts as official-case results.
''',encoding='utf-8')
        requirements=[]
        if key=='traceable-pdf-structure':requirements=['pdfplumber==0.11.11','pypdf==7.1.1','reportlab==5.1.1']
        if key=='sourced-nanopublications':requirements=['rdflib==7.6.0']
        (example/'requirements-demo.txt').write_text('# Optional local worked-example dependencies; official resources manifest takes precedence.\n'+'\n'.join(requirements)+'\n',encoding='utf-8')
        envdoc='''# Environment and dependency notes

## Minimum and installation

The bundled helpers require Python 3.10 or newer (including Path.is_relative_to and runtime union annotations). Plain UTF-8, JSON and DOCX OOXML paths use the standard library. Developments were checked with Windows Python 3.14; a Linux check is recorded separately and is not the official pinned Harness image.

Use the case's environment/resources.yaml and actual pinned tools first. Do not replace the evaluator environment or install a large stack blindly inside its case budget. For local development, use a separate virtual environment:

```sh
python3 -m venv .venv
# Activate the environment using your OS's standard activation command.
python -m pip install -r examples/worked/requirements-demo.txt
python scripts/dependency_probe.py
```

Install only extras relevant to the actual task. PDF geometry: pdfplumber 0.11.11; fallback text-only PDF reading: pypdf 7.1.1. A synthetic PDF generator also uses reportlab 5.1.1. RDF syntax checks in the Nanopublication worked example use rdflib 7.6.0. These are locally tested versions, not a claim that the platform has the same versions.

Sources: https://pypi.org/project/pdfplumber/ , https://pypi.org/project/pypdf/ , https://pypi.org/project/reportlab/ , https://pypi.org/project/rdflib/ . Read the upstream packages' own licenses and dependency specifications before redistribution.

## Probe and fallback

`python3 scripts/dependency_probe.py --require-pdf` requires the geometry parser. `--require-rdf` requires RDFLib. `--require-tex` requires an actually discoverable TeX compiler. The probe reports versions and missing components; it performs no installation, login or paid API call. Select flags only when the case needs those capabilities.

No OCR engine, language pack, TeX distribution, font, Office suite or model service is bundled. Discover actual installed resources. If a required component is unavailable, retain partial output and the exact limitation; missing tools are not successful execution. For TeX, preserve real compiler commands/exit codes and render the actual PDF if produced. For PDF fallback without geometry, do not claim bbox/table/order verification. RDFLib parsing alone is not full Nanopublication standards certification.

## Worked example scope

The scripted synthetic example is a reproducible micro-case with real file outputs and checks. It is not an Agent performance measurement or proof of passing three official cases. Do not copy its results into /app/output for an unrelated official case.
'''
        (folder/'references/environment.md').write_text(envdoc,encoding='utf-8')
        skill=(folder/'SKILL.md').read_text(encoding='utf-8')
        skill+='\n## Local environment and worked example\n\nRead [dependency versions and installation](references/environment.md) when diagnosing missing tools. A [runnable synthetic worked example](examples/worked/README.md) shows real task artifacts and local checks. It is optional development material, not an official-case answer or an Agent benchmark.\n'
        (folder/'SKILL.md').write_text(skill,encoding='utf-8')
        files=[p for p in folder.rglob('*') if p.is_file()]
        manifest.append({'challenge_id':task['id'],'skill':key,'title':task['title'],'files':len(files),'bytes':sum(p.stat().st_size for p in files),'sha256':{p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}})
    (DEST/'suite-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'candidate':str(DEST),'skills':len(manifest),'files':sum(x['files'] for x in manifest)},ensure_ascii=False,indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,default=HERE);parser.add_argument('--destination',type=Path,default=HERE);args=parser.parse_args()
    ORIGINAL=args.source.resolve();DEST=args.destination.resolve();build()
