# 文献翻译 workflow

1. Establish the target language, requested page/section span, glossary and output format. Extract the actual source; inspect multi-column reading order before translating. Give each source paragraph a stable ID, including captions, notes and relevant table headers.
2. Build a compact glossary from supplied terminology and actual domain context. Record each source term, chosen translation, definition/context and any explicit user preference. Resolve conflicts openly; enforce the same chosen term across title, abstract, body and captions unless the source uses genuinely different senses.
3. Protect equations, citation keys/markers, numeric values, units and figure/table identifiers. Translate in semantic chunks with a small carry-over context: current section, antecedents, accepted glossary and unresolved items. Keep a coverage ledger to resume without duplication or omission.
4. Translate the requested content fully, preserving polarity, causality versus association, modal strength, comparison direction and conditions. Preserve quoted/source language where requested. Do not make an uncertain or unreadable source sound definitive.
5. Store an alignment list with source segment id, original, translation, glossary decisions and review status. Audit source versus translated spans for numbers, units, citations and formulas. In bilingual artifacts audit the translation field alone, not the concatenation of both languages.
6. Review pronouns and cross-paragraph antecedents against preceding source context. Review all numbers and table content against the original PDF/table cells. Explicitly mark unreadable glyphs, missing formulas, ambiguous terms and unsupported OCR rather than completing them from memory.
7. Assemble all requested segments in original order, check complete unique coverage, and produce the requested editable/bilingual artifact with real preview when relevant. A partial translation lists exact missing spans and a continuation point.

## Practical checks and limits

Use audit-text on each original/translation pair, with a documented allowance when numeric typography is explicitly transformed (for example decimal notation). Script checks do not validate translation quality. Development examples should cover negation, term drift, cross-page continuations and bilingual numeric duplication.
