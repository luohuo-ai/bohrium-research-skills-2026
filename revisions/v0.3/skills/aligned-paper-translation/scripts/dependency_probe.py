#!/usr/bin/env python3
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
