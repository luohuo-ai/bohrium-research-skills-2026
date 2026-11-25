# Runnable synthetic worked example

This is a scripted micro-example for 引言与相关工作写作. It produces actual task-specific artifacts, source quotes and structural checks. It does not run a language model or compare Agent performance, and is not a fixed official case.

From this Skill root, first inspect [environment notes](../../references/environment.md), then run:

```sh
python3 scripts/worked_example.py --out /app/work/evidence-first-introduction-worked
```

Read result.json, the named main artifacts, evidence.json and selfcheck.json in that output directory. A partial result can be the correct behavior for contradictory/missing evidence or absent tools; inspect its uncertainty and build status. A green local selfcheck certifies only the specified synthetic checks, not official scientific quality.

The original examples/result.example.json remains an explicitly illustrative interface shape. This worked example is a separate concrete transformation. Never submit its synthetic artifacts as official-case results.

[Actual output preview](output-preview.md) shows the main artifact from the recorded scripted run.
