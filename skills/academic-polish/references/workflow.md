# 学术语言润色 workflow

1. Establish requested language, genre, audience, edit scope and available glossary. Keep an untouched original. Extract every in-scope segment with a stable ID; include unchanged segments in the alignment map so coverage can be checked.
2. Make a protected-fact list before editing: values and units, mathematical expressions, citations, figure/table references, negation, population, conditions and claim strength. Preserve these unless the task explicitly requests a documented factual correction supported by source material.
3. Edit for hard grammar, agreement, tense, terminology and readable academic phrasing. Prefer the smallest change that fixes the actual problem; do not replace technical words with casual synonyms. Distinguish causal claims from association and hypotheses from findings.
4. Maintain an edits JSON list with id, after, change_type and reason. A reason names the concrete problem and why the change preserves meaning, rather than only saying "improved clarity". Record unchanged text honestly. For a split or merged sentence retain mapping to all original segments.
5. Run audit-edits against the source segments. Review every numeric/unit/citation/math difference. Legitimate requested changes must be individually justified against actual evidence, not bypassed by removing their source. Review semantic_review flags manually; no flags does not establish equivalence. For text unsupported by the helper, use a transparent manual alignment instead of fabricating a green report.
6. Read the edited text back against the original, with special attention to may/must, not/only, significance, denominators and conditions. Then generate the requested editable artifact and a readable change list. In a bilingual report audit translated or edited spans separately: numbers repeated in the source column are not newly introduced facts.
7. Validate full-text coverage and terminology consistency across all sections. Do not omit difficult paragraphs. Resolve glossary conflicts from explicit task instructions or report them. Deliver partial edits with precise unedited ranges when the input exceeds the available budget.

## Practical checks and limits

Recommended development checks: subject–verb fixes without changing numbers; a hedge becoming a certainty; a unit accidentally changing from mg to kg; duplicate/missing paragraph IDs; LaTeX citation/inline formula retention; unchanged paragraphs retained. The helper does not determine journal style or scientific meaning.
