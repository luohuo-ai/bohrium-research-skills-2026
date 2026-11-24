# 参考文献与引用管理 workflow

1. Snapshot the manuscript and original bibliography; identify the requested citation convention and exact style version. Parse the actual format with an available reliable parser, or make a transparent structured intermediate without discarding braces, Unicode, author ordering or raw records.
2. Assign stable internal record IDs independent of display numbering. Normalize DOI syntax but preserve the original. Run structured_tools deduplicate on a records list containing id, title, year, authors and doi when known. Inspect conflicts and candidates. Similar titles alone must not merge; preprints and journal versions require explicit relationship evidence.
3. Verify records against supplied originals or authoritative DOI/publisher/database sources when permitted and reachable. Distinguish verified, conflicting, unverified and not-found. A DOI-shaped string is not proof of existence; a working DOI is not proof that it supports the manuscript's claim.
4. Map each citation to the exact claim sentence and actual source passage. Flag unsupported or missing citations. Insert or change a supporting reference only when the source actually supports the claim; do not substitute a convenient paper to hide missing evidence.
5. Complete deduplication decisions before assigning final numeric references. Create an old-id → canonical-id → display-number map; then update main text, captions, footnotes, appendices and reference list consistently in one pass. Prefer stable citation keys in LaTeX projects; do not edit numbers inside equations or unrelated bracketed data.
6. Apply the requested format from real style rules; missing fields stay missing/flagged. Check every in-text citation resolves, every cited record appears once, no stale numbers remain and bibliography fields survive conversion. Recompile/render the actual manuscript when its format requires it.
7. Deliver the editable result, bibliography, deduplication decisions with raw-record retention, numbering map, source-verification log and limitations. Mark offline verification limits honestly; never fill missing author/year/pages by guessing.

## Practical checks and limits

Intermediate helper example: python scripts/structured_tools.py deduplicate --input /app/work/records.json --out /app/work/reference-groups.json. It conservatively groups matching DOI+identity fields and retains input_records. It does not parse arbitrary BibTeX, prove source existence, implement APA/GB standards, or decide semantic citation support.
