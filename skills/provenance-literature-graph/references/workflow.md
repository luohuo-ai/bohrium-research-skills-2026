# 文献知识图谱构建 workflow

1. Read the actual papers and query requirements; define a small schema of needed scientific entity and relation types. Distinguish original findings, reviews, hypotheses and comparisons. Do not add plausible domain objects that are absent from sources.
2. Extract entities with raw mention, canonical label, type, source passage and evidence locator. Assign stable IDs. Propose alias merges only with explicit supporting context; shared surname, acronym or similar spelling is not sufficient identity evidence. Preserve an auditable alignment decision log.
3. Create directed relations only when supported. Record relation type, source/target, relevant conditions and evidence IDs. A co-occurrence is not uses/causes/outperforms. Conflicting relations may coexist with their scope and provenance; do not force them into one "true" edge.
4. Maintain nodes and edges in the case's requested format. For the optional local helper map to nodes=[{id,label,...}] and edges=[{id,source,target,relation,evidence,...}] without replacing required fields in final artifacts. Validate IDs, endpoints, duplicates and evidence presence with graph-check, then verify actual quotations with check-evidence.
5. Execute at least three case-relevant queries, including source-backed relations, a comparison/condition question and an unresolved or conflict case where relevant. graph-query supports outgoing direct edges only; multi-hop/domain-specific queries require an actual implementation with disclosed semantics, not invented answers.
6. When adding documents, retain existing IDs and old provenance, append new evidence and preserve unresolved aliases/conflicts. Stable IDs must not be renumbered merely because input ordering changes. Demonstrate an actual incremental update if requested.
7. Export the requested editable/queryable graph and a readable evidence index. If a diagram is requested, generate it from the actual graph and render a true preview. No query result means not established in this graph, not scientifically false.

## Practical checks and limits

Helper commands: structured_tools.py graph-check --input graph.json --out graph-check.json; structured_tools.py graph-query --input graph.json --subject ENTITY_ID --relation RELATION --out query.json. Edge evidence_ids must resolve to the original evidence ledger; helper presence checks alone cannot verify them.
