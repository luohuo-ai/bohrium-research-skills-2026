# Actual scripted synthetic output preview

This artifact was generated from input.json by scripts/worked_example.py. It is not an official case result or an Agent performance score.

Development result status: `success`.

```text
# Actual extraction of synthetic PDF

SYNTHETIC TWO-COLUMN DEMO

LEFT A: 12 replicates

LEFT B: temperature 20 C

LEFT C: source is synthetic

LEFT D: end of left column

RIGHT A: yield 8.2 percent

RIGHT B: no causal claim

RIGHT C: no actual experiment

RIGHT D: end of right column
```

## Checks

```json
{
  "left_before_right": true,
  "page_anchors": true,
  "real_bboxes": true,
  "original_case_id": true
}
```

## Boundaries

- Only this synthetic two-column layout is tested; OCR, cross-page tables and formula transcription are outside this example.
