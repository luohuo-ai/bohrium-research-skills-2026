# Environment and dependency notes

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
