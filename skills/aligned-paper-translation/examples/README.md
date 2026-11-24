# Synthetic interface demonstration

These files explain the interface; they are not formal cases, benchmark scores or prepared competition answers.

From this Skill's root, run:

```sh
python3 scripts/research_tools.py extract --input examples/source.md --out /app/work/aligned-paper-translation-source.json
python3 scripts/research_tools.py check-result --case examples/case.json --result examples/result.example.json --out /app/work/aligned-paper-translation-example-check.json
```

The first command produces actual source IDs, paragraphs, hashes and line locators. The second validates only the example's structural contract; its `partial` content explicitly states no actual task has been completed. A structurally valid example is not a good-scoring solution.

For a full invocation, ask an Agent to use this SKILL.md with a real, authorized input, the actual task and output contract, and an output directory; follow references/workflow.md to produce **Complete requested translation, aligned original/translated segments, applied glossary, evidence locators and unresolved translation issues.** Do not copy result.example.json into a formal result. In evaluation the paths and fields come from the provided case instead.
