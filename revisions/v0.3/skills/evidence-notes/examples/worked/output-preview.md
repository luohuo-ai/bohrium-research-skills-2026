# Actual scripted synthetic output preview

This artifact was generated from input.json by scripts/worked_example.py. It is not an official case result or an Agent performance score.

Development result status: `partial`.

```text
# Synthetic paper card

Question: describe an invented observational pilot.

Population: 80 enrolled in the methods prose; Table 1 says 81. Keep both and request resolution. Two exclusions leave 78 analysed according to the results prose; do not silently reconcile this with Table 1.

Result: reported correlation r=0.42 at 20 °C; this observational result does not establish causality.

Missing: randomization method, software version and seed are not reported.

```

## Checks

```json
{
  "conflict_retained": true,
  "analysed_count_retained": true,
  "original_case_id": true
}
```

## Boundaries

- Enrolled count conflicts; seed and software are not reported.
