# Actual scripted synthetic output preview

This artifact was generated from input.json by scripts/worked_example.py. It is not an official case result or an Agent performance score.

Development result status: `partial`.

```text
\documentclass{article}
\begin{document}
\section{Methods}\label{sec:methods}
See Section~\ref{sec:methods}. Preserve $x^2$.
\end{document}

```

## Checks

```json
{
  "missing_label_detected": true,
  "fixed_static_audit": true,
  "math_retained": true,
  "original_case_id": true
}
```

## Boundaries

- Static reference repair verified; actual compilation/preview is missing_tool. No absent compiler or PDF is claimed as successful.
