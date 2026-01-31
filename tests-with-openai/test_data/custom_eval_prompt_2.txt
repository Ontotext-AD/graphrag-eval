Divide both reference chunks and actual chunks into claims and try to
match claims between them. Count the:
- reference claims
- actual claims
- matching claims

Output the following values separated by tabs:
- retrieval_recall: Number of matching claims as a fraction of reference claims (fraction 0-1)
- retrieval_precision: Number of matching claims as a fraction of actual claims (fraction 0-1)
- retrieval_reason: reason for your evaluation

# Reference steps
[
  {
    "output": [
      {
        "id": "http://example.com/resource/doc/1",
        "text": "Transformer OSLO T1 is in Substation Oslo."
      },
      {
        "id": "http://example.com/resource/doc/2",
        "text": "Transformer OSLO T2 is in Substation Oslo."
      }
    ]
  }
]

# Actual steps
[
  {
    "output": [
      {
        "id": "http://example.com/resource/doc/1",
        "text": "Transformer OSLO T1 is in Substation Oslo."
      },
      {
        "id": "http://example.com/resource/doc/2",
        "text": "Transformer OSLO T2 is in Substation Oslo."
      }
    ]
  }
]
