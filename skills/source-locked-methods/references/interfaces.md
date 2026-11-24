# Helper interfaces

These are optional local intermediate structures. Translate the actual case's fields carefully and preserve the original final contract.

## Extracted source

`source.json` contains `source_id`, `path`, `sha256`, `status`, `parser`, `segments`, `limitations`. A segment has `id`, `text` and real locator fields (`line_start/line_end`, PDF `page/bbox`, or DOCX `paragraph`). Locations describe the extraction source, not invented rendered page numbers. A null bbox means geometry was not available.

## Evidence ledger

`{"evidence":[{"id":"e1","source_id":"FROM_EXTRACTION","source_sha256":"FROM_EXTRACTION","segment_id":"FROM_EXTRACTION","quote":"actual short source substring","claim":"the specific supported statement","support":"direct/qualified/inference"}]}`

Copy IDs/hashes from actual extraction. Choose quotes sufficient to support the claim, with conditions preserved; a matching substring alone does not establish support. Do not manufacture confidence percentages.

## Aligned edits

`{"edits":[{"id":"SOURCE_SEGMENT_ID","after":"complete edited or translated segment","change_type":"grammar/terminology/translation/unchanged/other","reason":"specific reason for the actual change"}]}`

Use exactly one entry per source segment for this helper. If the requested final structure splits or combines segments, keep a separate many-to-many lineage map and audit the uncombined edited spans. The helper never writes the final prose for you.

## Contract checking limits

Supported checks: object/array/string/number/integer/boolean/null types, properties/required, enum/const, additionalProperties, items, length/bounds, regular-expression patterns and allOf/anyOf/oneOf. `$ref`, format and other unimplemented keywords are explicitly unchecked. Plain required-field-name lists can be checked. Descriptive contracts receive field-presence checks plus manual-review notices. Scientific correctness, artifact existence, source coverage and semantic requirements require additional real inspection.

Unknown, missing or unsupported checks must remain visible; do not edit the schema or force a passing report. Keep original `case_id`; allow the original contract to specify extra field rules.

## Dependencies

Python 3 is required for helpers. Plain UTF-8 and DOCX extraction uses the standard library. Geometry-aware PDF extraction uses pdfplumber when installed; pypdf is a fallback with reduced guarantees. For OCR, rendering, TeX and format-specific exports discover the actual environment resources and use their real installed commands. No parser, OCR model, TeX distribution, font or network access is bundled or promised.
