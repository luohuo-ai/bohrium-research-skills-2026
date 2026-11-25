# Actual scripted synthetic output preview

This artifact was generated from input.json by scripts/worked_example.py. It is not an official case result or an Agent performance score.

Development result status: `success`.

```text
{
  "nodes": [
    {
      "id": "S1",
      "label": "Synthetic study S1"
    },
    {
      "id": "A",
      "label": "Material A"
    },
    {
      "id": "Y",
      "label": "Mean yield 8.2%"
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "S1",
      "target": "A",
      "relation": "uses",
      "evidence": [
        "e1"
      ]
    },
    {
      "id": "e2",
      "source": "A",
      "target": "Y",
      "relation": "reported_mean_yield",
      "conditions": {
        "temperature": "20 °C"
      },
      "evidence": [
        "e2"
      ]
    }
  ]
}
```

## Checks

```json
{
  "topology": true,
  "relation_query_has_source": true,
  "two_hop": true,
  "condition_query": true,
  "original_case_id": true
}
```

## Boundaries

- This tiny synthetic graph does not establish real-world entity identity or query recall.
