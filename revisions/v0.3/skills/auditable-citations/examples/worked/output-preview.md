# Actual scripted synthetic output preview

This artifact was generated from input.json by scripts/worked_example.py. It is not an official case result or an Agent performance score.

Development result status: `partial`.

```text
# Synthetic bibliography cleaning

The exact identity duplicates r1 and r2 form one group. r3 has the same invented DOI with conflicting title/year and remains separate for review. DOI existence is not checked; these are synthetic records.

```

## Checks

```json
{
  "duplicates_grouped": true,
  "conflict_retained": true,
  "original_case_id": true
}
```

## Boundaries

- The conflicting record is unresolved; all DOI strings are fictional examples.
