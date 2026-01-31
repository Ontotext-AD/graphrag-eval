Divide the reference answer into claims and try to match each claim to the
SPARQL query results. Count the:
- reference claims
- SPARQL results
- matching claims

Output the following values separated by tabs:
- sparql_recall: Number of matching claims as a fraction of reference claims (fraction 0-1)
- sparql_precision: Number of matching claims as a fraction of SPARQL results (fraction 0-1)
- sparql_reason: reason for your evaluation

# Question
List all transformers within Substation OSLO

# Reference answer
OSLO T1, OSLO T2

# Actual steps
[
  {
    "output": {
      "head": {
        "vars": [
          "transformer",
          "transformerName"
        ]
      },
      "results": {
        "bindings": [
          {
            "transformer": {
              "type": "uri",
              "value": "urn:uuid:f1769de8-9aeb-11e5-91da-b8763fd99c5f"
            },
            "transformerName": {
              "type": "literal",
              "value": "OSLO    T2"
            }
          },
          {
            "transformer": {
              "type": "uri",
              "value": "urn:uuid:f1769dd6-9aeb-11e5-91da-b8763fd99c5f"
            },
            "transformerName": {
              "type": "literal",
              "value": "OSLO    T1"
            }
          }
        ]
      }
    }
  }
]
