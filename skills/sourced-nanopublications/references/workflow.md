# Nanopublication workflow

1. Inspect source versions and actual output requirements, including whether JSON, JSON-LD, RDF/TriG or a specific Nanopublication profile is required. Read scientific statements in context, including methods/conditions and cited-versus-original findings.
2. Split composite conclusions into independently assessable assertions. Each includes subject, relation, object, direction, population/conditions, uncertainty and original scope. A conjunction inside an entity name need not split; a sentence asserting two outcomes usually does.
3. Bind each assertion to the smallest sufficient actual evidence passage and a retrievable source locator, source hash, document identity/version and provenance. Distinguish direct evidence, authors' interpretation and your own inference. Do not upgrade correlation to cause or omit experimental conditions.
4. Record insufficient, contradictory and missing evidence as explicit outcomes. Avoid arbitrary confidence numbers: describe the basis or use contract-provided confidence categories. Preserve the original wording alongside normalized terms.
5. Use assertion-check on the intermediate schema, then check-evidence on actual source segments. Review every flagged compound claim and condition gap. These checks establish field/quote presence, not entailment or RDF conformance.
6. Serialize the actual requested format with a real available library or carefully validated syntax. For a standard Nanopublication representation separate assertion, provenance and publication-info graphs and use stable, documented identifiers. Do not invent publisher, publication timestamps, identifiers or network resolution. If standards conformance cannot be checked, say so rather than substituting arbitrary JSON as a valid requested RDF deliverable.
7. Parse exported data back with an actually available compatible parser, check identifier/link integrity, and deliver evidence indexes plus unresolved statements. Keep development examples labeled and distinct from platform results.

## Practical checks and limits

Intermediate shape: assertions=[{id,assertion,subject,relation,object,conditions,evidence:[evidence_id]}]. python scripts/structured_tools.py assertion-check --input assertions.json --out lint.json. Do not submit this intermediate shape when the actual case requires a different serialization.
