Given the question, evaluate the actual answer based on the
reference answer.

Also evaluate the actual context based on the reference context.

Also evaluate the actual steps based on the reference steps.

Output the following values separated by tabs:
* custom_1_answer_score: fraction between 0 and 1
* custom_1_answer_reason: reason for your evaluation of the answer
* custom_1_context_score: fraction between 0 and 1
* custom_1_context_reason: reason for your evaluation of the context
* custom_1_steps_score: fraction between 0 and 1
* custom_1_steps_reason: reason for your evaluation of the steps

# Question
List all transformers within Substation OSLO

# Actual answer
The following transformers are located within the Substation OSLO:

1. **OSLO T2** (IRI: `urn:uuid:f1769de8-9aeb-11e5-91da-b8763fd99c5f`)
2. **OSLO T1** (IRI: `urn:uuid:f1769dd6-9aeb-11e5-91da-b8763fd99c5f`)

# Reference answer
OSLO T1, OSLO T2

# Actual context
{
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

# Reference context
{
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

# Actual steps
[
  {
    "name": "retrieval",
    "args": {
      "query": "transformers Substation OSLO",
      "k": 2
    },
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
  },
  {
    "name": "autocomplete_search",
    "args": {
      "query": "OSLO",
      "result_class": "cim:Substation"
    },
    "output": {
      "head": {
        "vars": [
          "iri",
          "name",
          "rank"
        ]
      },
      "results": {
        "bindings": [
          {
            "iri": {
              "type": "uri",
              "value": "urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f"
            },
            "name": {
              "type": "literal",
              "value": "OSLO"
            },
            "rank": {
              "datatype": "http://www.w3.org/2001/XMLSchema#float",
              "type": "literal",
              "value": "0.01185"
            }
          }
        ]
      }
    }
  },
  {
    "name": "sparql_query",
    "args": {
      "query": "SELECT ?transformer ?transformerName WHERE {\n  ?transformer a cim:PowerTransformer ;\n               cim:Equipment.EquipmentContainer <urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f> ;\n               cim:IdentifiedObject.name ?transformerName .\n}"
    },
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

# Reference steps
[
  {
    "name": "retrieval",
    "args": {
      "query": "transformers Substation OSLO",
      "k": 2
    },
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
  },
  {
    "name": "sparql_query",
    "args": {
      "query": "\nPREFIX cimex: <https://rawgit2.com/statnett/Talk2PowerSystem/main/demo1/cimex/>\nPREFIX cim: <https://cim.ucaiug.io/ns#>\nPREFIX rank: <http://www.ontotext.com/owlim/RDFRank#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nselect distinct ?transformer ?transformerName\nwhere {\n    bind(<urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f> as ?substation)\n\n    ?transformer a cim:PowerTransformer ;\n      cim:Equipment.EquipmentContainer ?substation ;\n      cim:IdentifiedObject.name ?transformerName .\n}\n"
    },
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