# 方法与实验章节写作 workflow

1. Inventory the actual factual materials, relevant code/config/log versions, requested scope and target style. Separate training, validation, testing and analysis stages. Do not treat comments in an old config as evidence of the run that actually happened.
2. Build a factual ledger: parameter name/value/unit, applicable stage/run/dataset split, exact source location, and conflict status. Record dataset identity/version, preprocessing, split construction, baselines, metrics, seeds, repetitions, hardware/software and commands only when evidenced.
3. Reconcile sources according to explicit version/run linkage, not an assumed blanket precedence of code over logs. Retain conflicting values with both references when the correct run cannot be determined. Missing repeats, seed, statistical method or test results remain author-confirmation items.
4. Convert the verified procedure into ordered steps with input, action, output and decision/termination conditions. Describe method assumptions and failure modes concretely. Avoid reporting a proposed step as an executed experiment.
5. Draft method and experiment sections with a clear separation of algorithm, implementation, evaluation protocol and measured findings. Make comparison conditions explicit. Do not claim fairness or reproducibility merely because the required fields are present; inspect whether budgets and partitions are actually comparable.
6. Cross-check every number in prose/tables against the ledger and source. Check dataset split roles and denominator consistency. Include actual commands/version identifiers when available, and do not silently add typical hyperparameters or synthetic performance values.
7. Deliver usable prose plus the parameter/condition ledger, source links, reproducibility checklist and gap list. If essential values are absent, retain a clearly marked draft/partial status and targeted questions rather than making the narrative appear complete.

## Practical checks and limits

Useful intermediate fields: parameter, value, unit, stage, run_id, source_id, segment_id, source_sha256, status. A config/log conflict is a first-class result; do not resolve it with generic defaults. Local examples are not the user's prior research projects.
