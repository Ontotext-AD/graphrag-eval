### Reference Q&A Data

A reference dataset is a list of templates, each of which contains:

- `template_id`: Unique template identifier
- `questions`: A list of questions derived from this template, where each includes:
  - `id`: Unique question identifier
  - `question_text`: The natural language query passed to the LLM
  - `reference_steps`: (optional) A list of expected steps grouped by expected order of execution, where all steps in a group can be executed in any order relative to each other, but after all steps in the previous group and before all steps in the next group.
  - `reference_answer`: (optional) The expected answer to the question

The assumption is that the final answer to the question is derived from the outputs of the steps, which are executed last (last level).

Each step includes:

- `name`: The name of the step (e.g., `sparql_query`)
- `args`: Arguments of the step (e.g., arguments to a tool used in the step, such as a SPARQL query)
- `output`: The expected output from the step.
- `output_media_type`: (optional, missing or one of `application/sparql-results+json`, `application/json`) Indicates how the output of a step must be processed
- `ordered`: (optional, defaults to `false`) For SPARQL query results, whether results order matters. `true` means that the actual result rows must be ordered as the reference result; `false` means that result rows are matched as a set.
- `required_columns`: (optional) - required only for SPARQL query results; list of binding names, which are required for SPARQL query results to match
- `ignore_duplicates`: (optional, defaults to `true`) For SPARQL query results, whether duplicate binding values in the expected or in the actual results should be ignored for the comparison.

#### Reference Data

The example data below illustrates a minimal but realistic Q&A dataset, showing two templates with associated questions and steps.

```yaml
- template_id: list_all_transformers_within_Substation_SUBSTATION
  questions:
  - id: c10bbc8dce98a4b8832d125134a16153
    question_text: List all transformers within Substation OSLO
    reference_answer: OSLO T1, OSLO T2
    reference_steps:
    - - name: retrieval
        args:
          query: transformers Substation OSLO
          k: 2
        output: |-
          [
            {
              "id": "http://example.com/resource/doc/1",
              "text": "Transformer OSLO T1 is in Substation Oslo."
            },
            {
              "id": "http://example.com/resource/doc/2",
              "text": "Transformer OSLO T2 is in Substation Oslo."
            }
          ]
      - name: sparql_query
        args:
          query: |2

            PREFIX cimex: <https://rawgit2.com/statnett/Talk2PowerSystem/main/demo1/cimex/>
            PREFIX cim: <https://cim.ucaiug.io/ns#>
            PREFIX rank: <http://www.ontotext.com/owlim/RDFRank#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            select distinct ?transformer ?transformerName
            where {
                bind(<urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f> as ?substation)

                ?transformer a cim:PowerTransformer ;
                  cim:Equipment.EquipmentContainer ?substation ;
                  cim:IdentifiedObject.name ?transformerName .
            }
        output: '{"head": {"vars": ["transformer", "transformerName"]}, "results":
          {"bindings": [{"transformer": {"type": "uri", "value": "urn:uuid:f1769de8-9aeb-11e5-91da-b8763fd99c5f"},
          "transformerName": {"type": "literal", "value": "OSLO    T2"}}, {"transformer":
          {"type": "uri", "value": "urn:uuid:f1769dd6-9aeb-11e5-91da-b8763fd99c5f"},
          "transformerName": {"type": "literal", "value": "OSLO    T1"}}]}}'
        output_media_type: application/sparql-results+json
        required_columns:
          - transformer
          - transformerName
  - id: 8bbea9a10876a04ad77a82fd2aedee40
    question_text: List all transformers within Substation STAVANGER
    reference_answer: STAVANGET1
    reference_steps:
    - - name: sparql_query
        args:
          query: |2

            PREFIX cimex: <https://rawgit2.com/statnett/Talk2PowerSystem/main/demo1/cimex/>
            PREFIX cim: <https://cim.ucaiug.io/ns#>
            PREFIX rank: <http://www.ontotext.com/owlim/RDFRank#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            select distinct ?transformer ?transformerName
            where {
                bind(<urn:uuid:f1769664-9aeb-11e5-91da-b8763fd99c5f> as ?substation)

                ?transformer a cim:PowerTransformer ;
                  cim:Equipment.EquipmentContainer ?substation ;
                  cim:IdentifiedObject.name ?transformerName .
            }
        output: '{"head": {"vars": ["transformer", "transformerName"]}, "results":
          {"bindings": [{"transformer": {"type": "uri", "value": "urn:uuid:f1769e0c-9aeb-11e5-91da-b8763fd99c5f"},
          "transformerName": {"type": "literal", "value": "STAVANGET1"}}]}}'
        output_media_type: application/sparql-results+json
        required_columns:
          - transformer
          - transformerName
- template_id: list_all_substations_within_bidding_zone_REGION
  questions:
  - id: d566b1e9da418ac83e520a66cc7af4d7
    question_text: List all substations within bidding zone NO2 SGR
    reference_answer: ARENDAL, BLAFALLI, STAVANGER, KRISTIA_HVDC, KVILLDAL, SANDEFJORD, KRISTIANSAND, FEDA_HVDC
    reference_steps:
    - - name: sparql_query
        args:
          query: |2

            PREFIX cimex: <https://rawgit2.com/statnett/Talk2PowerSystem/main/demo1/cimex/>
            PREFIX cim: <https://cim.ucaiug.io/ns#>
            PREFIX rank: <http://www.ontotext.com/owlim/RDFRank#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            select distinct ?substation ?substationName
            where {
                bind(<urn:uuid:f176965f-9aeb-11e5-91da-b8763fd99c5f> as ?region)

                ?substation a cim:Substation ;
                  cim:Substation.Region ?region ;
                  cim:IdentifiedObject.name ?substationName .
            }
        output: '{"head": {"vars": ["substation", "substationName"]}, "results": {"bindings":
          [{"substation": {"type": "uri", "value": "urn:uuid:f1769670-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "ARENDAL"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f176968e-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "BLAFALLI"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f1769664-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "STAVANGER"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f1769676-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "KRISTIA_HVDC"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f1769682-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "KVILLDAL"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f176966a-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "SANDEFJORD"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f176965a-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "KRISTIANSAND"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f176967c-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "FEDA_HVDC"}}]}}'
        output_media_type: application/sparql-results+json
        required_columns:
          - substation
          - substationName
        ordered: false
  - id: 03d4283773b4387114342518176b128b
    question_text: List all substations within bidding zone NO1 SGR
    reference_answer: HALDEN, KONGSBERG, SYLLING, OSLO, ASKER, SYSLE, SKIEN, TRETTEN
    reference_steps:
    - - name: sparql_query
        args:
          query: |2

            PREFIX cimex: <https://rawgit2.com/statnett/Talk2PowerSystem/main/demo1/cimex/>
            PREFIX cim: <https://cim.ucaiug.io/ns#>
            PREFIX rank: <http://www.ontotext.com/owlim/RDFRank#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            select distinct ?substation ?substationName
            where {
                bind(<urn:uuid:f1769609-9aeb-11e5-91da-b8763fd99c5f> as ?region)

                ?substation a cim:Substation ;
                  cim:Substation.Region ?region ;
                  cim:IdentifiedObject.name ?substationName .
            }
        output: '{"head": {"vars": ["substation", "substationName"]}, "results": {"bindings":
          [{"substation": {"type": "uri", "value": "urn:uuid:f176960e-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "HALDEN"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f176961e-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "KONGSBERG"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f1769642-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "SYLLING"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "OSLO"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f176964e-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "ASKER"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f1769648-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "SYSLE"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f1769654-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "SKIEN"}}, {"substation":
          {"type": "uri", "value": "urn:uuid:f1769604-9aeb-11e5-91da-b8763fd99c5f"},
          "substationName": {"type": "literal", "value": "TRETTEN"}}]}}'
        output_media_type: application/sparql-results+json
        required_columns:
          - substation
          - substationName
        ordered: false
```

The module is agnostic to the specific LLM agent implementation and model; it depends solely on the format of the response.
