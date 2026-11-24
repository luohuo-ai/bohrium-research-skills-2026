# 文献总结与结构化笔记 workflow

1. Identify the actual paper structure, not a universal template. Inspect title, abstract, headings, methods, results, discussion, figures, tables and supplements that are in scope. Extract source segments and preserve original page or paragraph locators.
2. Build a coverage map from actual sections and requested fields. At minimum consider research question, population/data, method, assumptions/conditions, key results and limitations, but respect this case's schema and do not pretend absent sections exist.
3. Create notes as small sourced claims. Preserve the study's measured quantities, units, denominators, comparisons, uncertainty and applicability conditions. Separate authors' findings, related-work statements and your own inference. Each key note names the supporting source segment and an actual short quotation.
4. For each field record supported, not_reported, conflicting or unassessable as permitted by the actual contract. A missing value is not zero. A reported association is not causal proof. Do not infer a dataset split or sample count merely because one is typical.
5. Produce a paper card and section-by-section notes. Link terminology aliases while retaining original terms. Include methodological limits and negative/qualified findings, not only favorable conclusions. Avoid making the abstract the evidence source for details available only in methods or tables.
6. Run check-evidence on the extraction JSON and ledger; manually verify entailment, scope and numeric transcription. Check that every requested section and material type is either covered or explicitly listed as unavailable. The quoted passage must be in the identified segment, not just somewhere in the paper.
7. Deliver the requested JSON/Markdown or editable notes with source indexes and a concise uncertainty list. If searchable notes are requested, use stable IDs, descriptive topic tags and a field dictionary. Preserve provenance through incremental updates instead of silently replacing earlier interpretations.

## Practical checks and limits

A local note may use {id, section, field, claim, evidence_ids, status, conditions}; these are intermediate fields, not a replacement for output_contract. Test missing methods, conditional results, contradictory tables, a fabricated quote, and a query whose answer the paper does not report.
