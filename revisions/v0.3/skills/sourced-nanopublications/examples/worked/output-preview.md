# Actual scripted synthetic output preview

This artifact was generated from input.json by scripts/worked_example.py. It is not an official case result or an Agent performance score.

Development result status: `success`.

```text
@prefix this: <https://example.invalid/synthetic-np/> .
@prefix np: <http://www.nanopub.org/nschema#> .
@prefix ex: <https://example.invalid/demo/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
this:head { this:np a np:Nanopublication; np:hasAssertion this:assertion; np:hasProvenance this:provenance; np:hasPublicationInfo this:pubinfo . }
this:assertion { ex:sample ex:reportedMeanYield "8.2"^^xsd:decimal; ex:temperatureCelsius "20"^^xsd:decimal; ex:replicates "12"^^xsd:integer . }
this:provenance { this:assertion prov:wasDerivedFrom ex:syntheticSource . }
this:pubinfo { this:np prov:wasAttributedTo ex:developmentExample; ex:synthetic true . }

```

## Checks

```json
{
  "local_assertion_lint": true,
  "trig_parsed": true,
  "four_named_graphs": true,
  "original_case_id": true
}
```

## Boundaries

- RDF syntax and this four-graph structure checked; no external publication, signature or full Nanopublication standards certification claimed.
