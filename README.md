<p align="center">
  <img alt="Graphwise Logo" src="https://github.com/Ontotext-AD/graphrag-eval/blob/main/.github/Graphwise_Logo.jpg">
</p>

# QA Evaluation

This is a Python module for assessing the quality of question-answering systems such as ones based on LLM agents, 
based on a set of questions and reference answers for them. This includes evaluating the final answer and 
the steps used to reach the answer (such as orchestrated and executed steps), compared to the given reference steps.

## License

Apache-2.0 License. See [LICENSE](https://github.com/Ontotext-AD/graphrag-eval/blob/main/LICENSE) file for details.

## Installation

To evaluate only steps:
```bash
pip install graphrag-eval
```
or add the following dependency in your `pyproject.toml` file:
```toml
graphrag-eval = "*"
```

To evaluate answer relevance and answer correctness:
```bash
pip install 'graphrag-eval[ragas]'
```
or add the following dependency in your `pyproject.toml` file:
```toml
graphrag-eval = {version = "*", extras = ["ragas"]}
```

## Maintainers

Developed and maintained by [Graphwise](https://graphwise.ai/).
For issues or feature requests, please open [a GitHub issue](https://github.com/Ontotext-AD/graphrag-eval/issues).

## Command Line Use

To evaluate only correctness of final answers (system responses), you can clone this repository and 
run the code on the command line:

1. Prepare an input TSV file with columns `Question`, `Reference answer` and `Actual answer`
1. Execute `poetry install --with ragas`
1. Execute `OPENAI_API_KEY=<your_api_key> poetry run answer-correctness -i <input_file.tsv> -o <output_file.tsv>`

We plan to improve CLI support in future releases.

## Use as a Library

To evaluate answers and/or steps:
1. Install this package: section [Install](#Installation)
1. Format the dataset of questions and reference answers and/or steps: section [Reference Q&A Data](#Reference-qa-Data)
1. Format the answers and/or steps you want to evaluate: section [Responses to evaluate](#Responses-to-evaluate)
1. To evaluate answer relevance:
    1. Include `actual_answer` in the target data to evaluate
    1. Set environment variable `OPENAI_API_KEY` appropriately
1. To evaluate answer correctness:
    1. Include `reference_answer` in the reference dataset and `actual_answer` in the target data to evaluate
    1. Set environment variable `OPENAI_API_KEY` appropriately
1. To evaluate steps:
    1. Include `reference_steps` in the reference data and `actual_steps` in target data to evaluate
1. Call the evaluation function with the reference data and target data: section [Usage Code](#Usage-Code)
1. Call the aggregation function with the evaluation results: section [Usage Code](#Usage-Code)

Answer evaluation (correctness and relevance) uses the LLM `openai/gpt-4o-mini`.

### Reference Q&A Data

A reference dataset is a list of templates, each of which contains:

- `template_id`: Unique template identifier
- `questions`: A list of questions derived from this template, where each includes:
  - `id`: Unique question identifier
  - `question_text`: The natural language query passed to the LLM
  - `reference_steps`: (optional) A list of expected steps grouped by expected order of execution, 
  where all steps in a group can be executed in any order relative to each other, 
  but after all steps in the previous group and before all steps in the next group.
  - `reference_answer`: (optional) The expected answer to the question

The assumption is that the final answer to the question is derived from the outputs of the steps, 
which are executed last (last level).

Each step includes:

- `name`: The name of the step (e.g., `sparql_query`)
- `args`: Arguments of the step (e.g., arguments to a tool used in the step, such as a SPARQL query)
- `output`: The expected output from the step.
- `output_media_type`: (optional, missing or one of `application/sparql-results+json`, `application/json`) 
Indicates how the output of a step must be processed
- `ordered`: (optional, defaults to `false`) For SPARQL query results, whether results order matters.
`true` means that the actual result rows must be ordered as the reference result; 
`false` means that result rows are matched as a set.
- `required_columns`: (optional) - required only for SPARQL query results; list of binding names, 
which are required for SPARQL query results to match
- `ignore_duplicates`: (optional, defaults to `true`) For SPARQL query results, 
whether duplicate binding values in the expected or in the actual results should be ignored for the comparison.

#### Reference Data

The example data below illustrates a minimal but realistic Q&A dataset, 
showing two templates with associated questions and steps.

```yaml
- template_id: list_all_transformers_within_Substation_SUBSTATION
  questions:
  - id: c10bbc8dce98a4b8832d125134a16153
    question_text: List all transformers within Substation OSLO
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

The module is agnostic to the specific LLM agent implementation and model; 
it depends solely on the format of the response.

### Responses to evaluate

Given a question, if the question-answering system successfully responds, 
to evaluate the response, call `run_evaluation()` with the response formatted as in the example below. 
If an error occurs while generating a response, format it as in [Target Input on Error](#target-input-on-error).

```json
{
    "question_id": "timeseries_template_1_question_1",
    "input_tokens": 791569,
    "output_tokens": 15522,
    "total_tokens": 807091,
    "elapsed_sec": 205.36997318267822,
    "actual_steps": [
        {
            "name": "autocomplete_search",
            "args": {
                "query": "NO1",
                "result_class": "nc:BiddingZone",
                "limit": 5
            },
            "id": "call_McU1eeVy7OpLxuD6J07bvqBi",
            "status": "success",
            "execution_timestamp": "2025-12-15T15:06:14Z",
            "output": "{\n \"head\": {\n \"vars\": [\n \"iri\",\n \"name\",\n \"class\",\n \"rank\"\n ]\n },\n \"results\": {\n \"bindings\": [\n {\n \"iri\": {\n \"type\": \"uri\",\n \"value\": \"urn:uuid:83aa03e5-5fd0-431c-b8dd-acc08c21ed6a\"\n },\n \"name\": {\n \"type\": \"literal\",\n \"value\": \"NO1\"\n },\n \"class\": {\n \"type\": \"uri\",\n \"value\": \"https://cim4.eu/ns/nc#BiddingZone\"\n },\n \"rank\": {\n \"datatype\": \"http://www.w3.org/2001/XMLSchema#float\",\n \"type\": \"literal\",\n \"value\": \"0.01489\"\n }\n },\n {\n \"iri\": {\n \"type\": \"uri\",\n \"value\": \"urn:uuid:173e9d6d-77c8-44e0-805f-dc2f773c61fb\"\n },\n \"name\": {\n \"type\": \"literal\",\n \"value\": \"NO_NO2_DK1\"\n },\n \"class\": {\n \"type\": \"uri\",\n \"value\": \"https://cim4.eu/ns/nc#BiddingZone\"\n },\n \"rank\": {\n \"datatype\": \"http://www.w3.org/2001/XMLSchema#float\",\n \"type\": \"literal\",\n \"value\": \"0.00000\"\n }\n }\n ]\n }\n}"
        },
        {
            "name": "autocomplete_search",
            "args": {
                "query": "NO3",
                "result_class": "nc:BiddingZone",
                "limit": 5
            },
            "id": "call_vMtXHDegeihqw1PjViNdh3M3",
            "status": "success",
            "execution_timestamp": "2025-12-15T15:06:45Z",
            "output": "{\n \"head\": {\n \"vars\": [\n \"iri\",\n \"name\",\n \"class\",\n \"rank\"\n ]\n },\n \"results\": {\n \"bindings\": [\n {\n \"iri\": {\n \"type\": \"uri\",\n \"value\": \"urn:uuid:0f094148-164b-427a-a8e8-0c5f334688ae\"\n },\n \"name\": {\n \"type\": \"literal\",\n \"value\": \"NO3\"\n },\n \"class\": {\n \"type\": \"uri\",\n \"value\": \"https://cim4.eu/ns/nc#BiddingZone\"\n },\n \"rank\": {\n \"datatype\": \"http://www.w3.org/2001/XMLSchema#float\",\n \"type\": \"literal\",\n \"value\": \"0.00433\"\n }\n }\n ]\n }\n}"
        },
        {
            "name": "sparql_query",
            "args": {
                "query": "SELECT ?border ?meas ?mrid ?type ?posFlowIn ?isInCognite WHERE {\n BIND(<urn:uuid:83aa03e5-5fd0-431c-b8dd-acc08c21ed6a> AS ?no1)\n BIND(<urn:uuid:0f094148-164b-427a-a8e8-0c5f334688ae> AS ?no3)\n ?border a <https://cim4.eu/ns/nc#BiddingZoneBorder> ;\n <https://cim4.eu/ns/nc#BiddingZoneBorder.BiddingZoneOne> ?no1 ;\n <https://cim4.eu/ns/nc#BiddingZoneBorder.BiddingZoneTwo> ?no3 .\n ?meas a <https://cim.ucaiug.io/ns#Analog> ;\n <https://cim.ucaiug.io/ns#Measurement.PowerSystemResource> ?border ;\n <https://cim.ucaiug.io/ns#Measurement.measurementType> ?type ;\n <https://cim.ucaiug.io/ns#IdentifiedObject.mRID> ?mrid ;\n <https://cim.ucaiug.io/ns#Measurement.unitSymbol> ?unit ;\n <https://cim.ucaiug.io/ns#Measurement.unitMultiplier> ?mult ;\n <https://cim.ucaiug.io/ns#Analog.positiveFlowIn> ?posFlowIn .\n OPTIONAL { ?meas <https://cim.ucaiug.io/rules#Measurement.isInCognite> ?isInCognite }\n FILTER( ?type = \"ThreePhaseActivePower-Flow-Estimated\"^^xsd:string || ?type = \"ThreePhaseActivePower\"^^xsd:string )\n}"
            },
            "id": "call_C3qAMjRWOrBZCU4QyPOx3X5D",
            "status": "success",
            "execution_timestamp": "2025-12-15T15:06:59Z",
            "output": "{\n \"head\": {\n \"vars\": [\n \"border\",\n \"meas\",\n \"mrid\",\n \"type\",\n \"posFlowIn\",\n \"isInCognite\"\n ]\n },\n \"results\": {\n \"bindings\": [\n {\n \"border\": {\n \"type\": \"uri\",\n \"value\": \"urn:uuid:852b95c0-4c49-4ded-85b2-a8f2b610db30\"\n },\n \"meas\": {\n \"type\": \"uri\",\n \"value\": \"urn:uuid:9bb00fb1-4e7f-831a-e040-1e828c94e833\"\n },\n \"mrid\": {\n \"type\": \"literal\",\n \"value\": \"9bb00fb1-4e7f-831a-e040-1e828c94e833\"\n },\n \"type\": {\n \"type\": \"literal\",\n \"value\": \"ThreePhaseActivePower-Flow-Estimated\"\n },\n \"posFlowIn\": {\n \"datatype\": \"http://www.w3.org/2001/XMLSchema#boolean\",\n \"type\": \"literal\",\n \"value\": \"true\"\n },\n \"isInCognite\": {\n \"datatype\": \"http://www.w3.org/2001/XMLSchema#boolean\",\n \"type\": \"literal\",\n \"value\": \"true\"\n }\n }\n ]\n }\n}"
        },
        {
            "name": "retrieve_time_series",
            "args": {
                "mrid": "9bb00fb1-4e7f-831a-e040-1e828c94e833",
                "limit": 5
            },
            "id": "call_oU7gHlH48L7IqDl4T9CVkUbc",
            "status": "success",
            "execution_timestamp": "2025-12-15T15:07:05Z",
            "output": "[\n {\n \"external_id\": \"9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value\",\n \"name\": \"Elspot NO1-NO3 MW_estimated_value\",\n \"is_string\": false,\n \"metadata\": {\n \"unit\": \"MW\",\n \"measurement_type\": \"ThreePhaseActivePower\",\n \"mrid\": \"9bb00fb1-4e7f-831a-e040-1e828c94e833\",\n \"unit_symbol\": \"W\",\n \"timeseries_type\": \"estimated_value\",\n \"substation\": \"DIV_NCC\",\n \"end_time\": \"\",\n \"topic\": \"observations_grid_power_no_ems_analog_active_power_res_1s_avro_v1\",\n \"unit_multiplier\": \"M\",\n \"source\": \"eTerra\",\n \"subscription\": \"DIV_NCC\",\n \"device\": \"ELSPOT\"\n },\n \"unit\": \"MW\",\n \"asset_id\": 2296222851104770,\n \"is_step\": false,\n \"description\": \"ThreePhaseActivePower\",\n \"security_categories\": [],\n \"data_set_id\": 5515145765342807,\n \"id\": 2314805086177702,\n \"created_time\": \"2023-06-13 21:11:59.579+00:00\",\n \"last_updated_time\": \"2025-09-29 12:22:45.755+00:00\"\n }\n]"
        },
        {
            "name": "retrieve_data_points",
            "args": {
                "external_id": "9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value",
                "start": "2025-01-01T00:00:00Z",
                "end": "2026-01-01T00:00:00Z",
                "aggregates": [
                    "min",
                    "max",
                    "average"
                ],
                "granularity": "1week"
            },
            "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
            "status": "success",
            "execution_timestamp": "2025-12-15T15:07:14Z",
            "output": "{\n \"id\": 2314805086177702,\n \"externalId\": \"9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value\",\n \"isString\": false,\n \"isStep\": false,\n \"unit\": \"MW\",\n \"unitExternalId\": \"\",\n \"granularity\": \"1week\",\n \"datapoints\": [\n {\n \"timestamp\": \"2025-01-01 00:00:00\",\n \"max\": -22.4774875640869,\n \"min\": -634.605163574219,\n \"sum\": -6079679.572650909\n },\n {\n \"timestamp\": \"2025-01-08 00:00:00\",\n \"max\": -176.806610107422,\n \"min\": -592.054992675781,\n \"sum\": -7497037.204193115\n },\n {\n \"timestamp\": \"2025-01-15 00:00:00\",\n \"max\": -48.8348274230957,\n \"min\": -604.223022460938,\n \"sum\": -7033178.197429657\n },\n {\n \"timestamp\": \"2025-01-22 00:00:00\",\n \"max\": -93.4801940917969,\n \"min\": -638.378295898438,\n \"sum\": -6409085.44443512\n },\n {\n \"timestamp\": \"2025-01-29 00:00:00\",\n \"max\": -174.200958251953,\n \"min\": -591.80126953125,\n \"sum\": -5810485.415344238\n },\n {\n \"timestamp\": \"2025-02-05 00:00:00\",\n \"max\": -129.160598754883,\n \"min\": -583.906555175781,\n \"sum\": -5875491.905670166\n },\n {\n \"timestamp\": \"2025-02-12 00:00:00\",\n \"max\": -82.5265808105469,\n \"min\": -473.589019775391,\n \"sum\": -4749596.438865662\n },\n {\n \"timestamp\": \"2025-02-19 00:00:00\",\n \"max\": -94.3547592163086,\n \"min\": -553.544799804687,\n \"sum\": -6127722.962348938\n },\n {\n \"timestamp\": \"2025-02-26 00:00:00\",\n \"max\": 39.375675201416,\n \"min\": -495.355010986328,\n \"sum\": -5909059.358499527\n },\n {\n \"timestamp\": \"2025-03-05 00:00:00\",\n \"max\": -0.723251342773438,\n \"min\": -444.584655761719,\n \"sum\": -5032459.175174713\n },\n {\n \"timestamp\": \"2025-03-12 00:00:00\",\n \"max\": 53.3467674255371,\n \"min\": -367.410522460938,\n \"sum\": -3308910.4881810993\n },\n {\n \"timestamp\": \"2025-03-19 00:00:00\",\n \"max\": 165.641891479492,\n \"min\": -345.912719726563,\n \"sum\": -3240730.651639104\n },\n {\n \"timestamp\": \"2025-03-26 00:00:00\",\n \"max\": 81.5682983398438,\n \"min\": -420.76953125,\n \"sum\": -5090794.093489647\n },\n {\n \"timestamp\": \"2025-04-02 00:00:00\",\n \"max\": 66.1184768676758,\n \"min\": -415.227844238281,\n \"sum\": -4365653.5047190515\n },\n {\n \"timestamp\": \"2025-04-09 00:00:00\",\n \"max\": 113.980033874512,\n \"min\": -352.113433837891,\n \"sum\": -3703392.03900598\n },\n {\n \"timestamp\": \"2025-04-16 00:00:00\",\n \"max\": -23.1248321533203,\n \"min\": -418.720520019531,\n \"sum\": -2175163.6172618866\n },\n {\n \"timestamp\": \"2025-04-23 00:00:00\",\n \"max\": 66.5215454101563,\n \"min\": -409.330108642578,\n \"sum\": -4216380.705057085\n },\n {\n \"timestamp\": \"2025-04-30 00:00:00\",\n \"max\": 36.223258972168,\n \"min\": -443.705169677734,\n \"sum\": -2727791.800246954\n },\n {\n \"timestamp\": \"2025-05-07 00:00:00\",\n \"max\": -101.288871765137,\n \"min\": -464.468048095703,\n \"sum\": -3374325.6654815674\n },\n {\n \"timestamp\": \"2025-05-14 00:00:00\",\n \"max\": -65.273193359375,\n \"min\": -515.709655761719,\n \"sum\": -4706765.8790130615\n },\n {\n \"timestamp\": \"2025-05-21 00:00:00\",\n \"max\": 2.4623658657074,\n \"min\": -628.811157226562,\n \"sum\": -5354630.00902313\n },\n {\n \"timestamp\": \"2025-05-28 00:00:00\",\n \"max\": 86.4481430053711,\n \"min\": -648.408813476563,\n \"sum\": -6994838.807719275\n },\n {\n \"timestamp\": \"2025-06-04 00:00:00\",\n \"max\": 101.356071472168,\n \"min\": -586.686218261719,\n \"sum\": -13510767.91916069\n },\n {\n \"timestamp\": \"2025-06-11 00:00:00\",\n \"max\": 163.898529052734,\n \"min\": -556.988159179688,\n \"sum\": -14113734.887452226\n },\n {\n \"timestamp\": \"2025-06-18 00:00:00\",\n \"max\": 47.9553833007813,\n \"min\": -566.966491699219,\n \"sum\": -5525602.276288301\n },\n {\n \"timestamp\": \"2025-06-25 00:00:00\",\n \"max\": 82.483642578125,\n \"min\": -481.129364013672,\n \"sum\": -4503993.2934425045\n },\n {\n \"timestamp\": \"2025-07-02 00:00:00\",\n \"max\": 4.44720029830933,\n \"min\": -645.917663574219,\n \"sum\": -3699148.5399570465\n },\n {\n \"timestamp\": \"2025-07-09 00:00:00\",\n \"max\": 18.5413227081299,\n \"min\": -433.975158691406,\n \"sum\": -2930218.747092165\n },\n {\n \"timestamp\": \"2025-07-16 00:00:00\",\n \"max\": 9.86935138702393,\n \"min\": -466.966949462891,\n \"sum\": -4869006.952767938\n },\n {\n \"timestamp\": \"2025-07-23 00:00:00\",\n \"max\": -79.1166152954102,\n \"min\": -416.107727050781,\n \"sum\": -4550968.429283142\n },\n {\n \"timestamp\": \"2025-07-30 00:00:00\",\n \"max\": 206.594253540039,\n \"min\": -428.860229492188,\n \"sum\": -3211479.5606954247\n },\n {\n \"timestamp\": \"2025-08-06 00:00:00\",\n \"max\": 211.718780517578,\n \"min\": -428.881683349609,\n \"sum\": -1789749.3762937572\n },\n {\n \"timestamp\": \"2025-08-13 00:00:00\",\n \"max\": 68.2974395751953,\n \"min\": -23.84885597229,\n \"sum\": 120343.40388285261\n },\n {\n \"timestamp\": \"2025-08-20 00:00:00\",\n \"max\": 219.931503295898,\n \"min\": -8.17569255828857,\n \"sum\": 955194.8288861046\n },\n {\n \"timestamp\": \"2025-08-27 00:00:00\",\n \"max\": 183.314514160156,\n \"min\": -687.299377441406,\n \"sum\": -12165633.712079525\n },\n {\n \"timestamp\": \"2025-09-03 00:00:00\",\n \"max\": 51.6008987426758,\n \"min\": -627.613830566406,\n \"sum\": -16095338.66005943\n },\n {\n \"timestamp\": \"2025-09-10 00:00:00\",\n \"max\": 57.2205429077148,\n \"min\": -563.739929199219,\n \"sum\": -10858557.12343351\n },\n {\n \"timestamp\": \"2025-09-17 00:00:00\",\n \"max\": 205.345397949219,\n \"min\": -550.26513671875,\n \"sum\": -10393817.01633801\n },\n {\n \"timestamp\": \"2025-09-24 00:00:00\",\n \"max\": 268.643463134766,\n \"min\": -549.864868164063,\n \"sum\": -6616383.323891792\n },\n {\n \"timestamp\": \"2025-10-01 00:00:00\",\n \"max\": 318.965423583984,\n \"min\": -432.655151367188,\n \"sum\": -1600749.2544672987\n },\n {\n \"timestamp\": \"2025-10-08 00:00:00\",\n \"max\": -3.35211229324341,\n \"min\": -471.751831054688,\n \"sum\": -5144527.891113758\n },\n {\n \"timestamp\": \"2025-10-15 00:00:00\",\n \"max\": 90.3368453979492,\n \"min\": -471.285675048828,\n \"sum\": -3875047.637278557\n },\n {\n \"timestamp\": \"2025-10-22 00:00:00\",\n \"max\": 110.84740447998,\n \"min\": -483.147857666016,\n \"sum\": -3056732.2498025894\n },\n {\n \"timestamp\": \"2025-10-29 00:00:00\",\n \"max\": 109.893417358398,\n \"min\": -440.507598876953,\n \"sum\": -2343687.2623984218\n },\n {\n \"timestamp\": \"2025-11-05 00:00:00\",\n \"max\": 120.950942993164,\n \"min\": -401.896026611328,\n \"sum\": -2414128.2356422693\n },\n {\n \"timestamp\": \"2025-11-12 00:00:00\",\n \"max\": 100.14469909668,\n \"min\": -384.338897705078,\n \"sum\": -1426443.203330338\n },\n {\n \"timestamp\": \"2025-11-19 00:00:00\",\n \"max\": 120.508186340332,\n \"min\": 86.9833068847656,\n \"sum\": 362196.56188201904\n },\n {\n \"timestamp\": \"2025-11-26 00:00:00\",\n \"max\": 120.065689086914,\n \"min\": -473.767059326172,\n \"sum\": -3704030.113606751\n },\n {\n \"timestamp\": \"2025-12-03 00:00:00\",\n \"max\": -18.4274024963379,\n \"min\": -430.414184570312,\n \"sum\": -3881328.2995967865\n },\n {\n \"timestamp\": \"2025-12-10 00:00:00\",\n \"max\": -106.10661315918,\n \"min\": -416.067596435547,\n \"sum\": -1366852.111000061\n }\n ]\n}"
        }
    ]
}
```

#### Target Input on Error

If an error occurs while the question-answering system is generating a response, 
and you want to tally this error, the input to `run_evaluate()` should be like:

```json
{
    "question_id": "a8daaf98b84b4f6b0e0052fb942bf6b6",
    "error": "Error message",
    "status": "error"
}
```

### Usage Code

```python
from graphrag_eval import run_evaluation, compute_aggregates

reference_qa_dataset: list[dict] = [] # read your reference data
chat_responses: dict = {} # call your implementation to get the response
evaluation_results = run_evaluation(reference_qa_dataset, chat_responses)
aggregates = compute_aggregates(evaluation_results)
```

`evaluation_results` is a list of statistics for each question, as in section [Evaluation Results](#Evaluation-results). 
The format is explained in section [Output Keys](#output-keys)

If your chat responses contain actual answers, set your environment variable `OPENAI_API_KEY` before running the code above.

### Evaluation Results

The output is a list of statistics for each question from the reference Q&A dataset. Here is an example of statistics for one question:

```yaml
- template_id: timeseries_template_1
  question_id: timeseries_template_1_question_1
  question_text: Power flow from NO1 to NO3; for 2025, weekly average, min, max
  reference_steps:
  - - args:
        query: NO1 - NO3
      name: iri_discovery
      output: urn:uuid:852b95c0-4c49-4ded-85b2-a8f2b610db30
      output_media_type: text/uri
      required_columns:
      - uri
  - - args:
        query: 'PREFIX cimr: <https://cim.ucaiug.io/rules#>
PREFIX cim: <https://cim.ucaiug.io/ns#>
PREFIX nc: <https://cim4.eu/ns/nc#>
SELECT ?mrid WHERE {
    ?analog cim:Measurement.PowerSystemResource <urn:uuid:852b95c0-4c49-4ded-85b2-a8f2b610db30>;
    cim:Measurement.measurementType "ThreePhaseActivePower-Flow-Estimated";
    cim:Analog.positiveFlowIn true ;
    cimr:Measurement.isInCognite true;
    cim:IdentifiedObject.mRID ?mrid.
}'
      name: sparql_query
      output: '{
  "head": {
    "vars": [
      "mrid"
    ]
  },
  "results": {
    "bindings": [
      {
        "mrid": {
          "type": "literal",
          "value": "9bb00fb1-4e7f-831a-e040-1e828c94e833"
        }
      }
    ]
  }
}'
      output_media_type: application/sparql-results+json
      required_columns:
      - mrid
      matches: call_C3qAMjRWOrBZCU4QyPOx3X5D
  - - args:
        mrid: 9bb00fb1-4e7f-831a-e040-1e828c94e833
      name: retrieve_time_series
      matches: call_oU7gHlH48L7IqDl4T9CVkUbc
  - - args:
        external_id: 9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value
        aggregates:
        - average
        - min
        - max
        granularity: 1w
        start: 2025-01-01 00:00:00+00:00
        end: 2026-01-01 00:00:00+00:00
      name: retrieve_data_points
      matches: call_1MA7PL4KAPJ7riH2UrxseyZW
  status: success
  actual_steps:
  - name: autocomplete_search
    args:
      query: NO1
      result_class: nc:BiddingZone
      limit: 5
    id: call_McU1eeVy7OpLxuD6J07bvqBi
    status: success
    execution_timestamp: '2025-12-15T15:06:14Z'
    output: "{\n \"head\": {\n \"vars\": [\n \"iri\",\n \"name\",\n \"class\",\n \"\
      rank\"\n ]\n },\n \"results\": {\n \"bindings\": [\n {\n \"iri\": {\n \"type\"\
      : \"uri\",\n \"value\": \"urn:uuid:83aa03e5-5fd0-431c-b8dd-acc08c21ed6a\"\n\
      \ },\n \"name\": {\n \"type\": \"literal\",\n \"value\": \"NO1\"\n },\n \"class\"\
      : {\n \"type\": \"uri\",\n \"value\": \"https://cim4.eu/ns/nc#BiddingZone\"\n\
      \ },\n \"rank\": {\n \"datatype\": \"http://www.w3.org/2001/XMLSchema#float\"\
      ,\n \"type\": \"literal\",\n \"value\": \"0.01489\"\n }\n },\n {\n \"iri\":\
      \ {\n \"type\": \"uri\",\n \"value\": \"urn:uuid:173e9d6d-77c8-44e0-805f-dc2f773c61fb\"\
      \n },\n \"name\": {\n \"type\": \"literal\",\n \"value\": \"NO_NO2_DK1\"\n },\n\
      \ \"class\": {\n \"type\": \"uri\",\n \"value\": \"https://cim4.eu/ns/nc#BiddingZone\"\
      \n },\n \"rank\": {\n \"datatype\": \"http://www.w3.org/2001/XMLSchema#float\"\
      ,\n \"type\": \"literal\",\n \"value\": \"0.00000\"\n }\n }\n ]\n }\n}"
  - name: autocomplete_search
    args:
      query: NO3
      result_class: nc:BiddingZone
      limit: 5
    id: call_vMtXHDegeihqw1PjViNdh3M3
    status: success
    execution_timestamp: '2025-12-15T15:06:45Z'
    output: "{\n \"head\": {\n \"vars\": [\n \"iri\",\n \"name\",\n \"class\",\n \"\
      rank\"\n ]\n },\n \"results\": {\n \"bindings\": [\n {\n \"iri\": {\n \"type\"\
      : \"uri\",\n \"value\": \"urn:uuid:0f094148-164b-427a-a8e8-0c5f334688ae\"\n\
      \ },\n \"name\": {\n \"type\": \"literal\",\n \"value\": \"NO3\"\n },\n \"class\"\
      : {\n \"type\": \"uri\",\n \"value\": \"https://cim4.eu/ns/nc#BiddingZone\"\n\
      \ },\n \"rank\": {\n \"datatype\": \"http://www.w3.org/2001/XMLSchema#float\"\
      ,\n \"type\": \"literal\",\n \"value\": \"0.00433\"\n }\n }\n ]\n }\n}"
  - name: sparql_query
    args:
      query: "SELECT ?border ?meas ?mrid ?type ?posFlowIn ?isInCognite WHERE {\n BIND(<urn:uuid:83aa03e5-5fd0-431c-b8dd-acc08c21ed6a>\
        \ AS ?no1)\n BIND(<urn:uuid:0f094148-164b-427a-a8e8-0c5f334688ae> AS ?no3)\n\
        \ ?border a <https://cim4.eu/ns/nc#BiddingZoneBorder> ;\n <https://cim4.eu/ns/nc#BiddingZoneBorder.BiddingZoneOne>\
        \ ?no1 ;\n <https://cim4.eu/ns/nc#BiddingZoneBorder.BiddingZoneTwo> ?no3 .\n\
        \ ?meas a <https://cim.ucaiug.io/ns#Analog> ;\n <https://cim.ucaiug.io/ns#Measurement.PowerSystemResource>\
        \ ?border ;\n <https://cim.ucaiug.io/ns#Measurement.measurementType> ?type\
        \ ;\n <https://cim.ucaiug.io/ns#IdentifiedObject.mRID> ?mrid ;\n <https://cim.ucaiug.io/ns#Measurement.unitSymbol>\
        \ ?unit ;\n <https://cim.ucaiug.io/ns#Measurement.unitMultiplier> ?mult ;\n\
        \ <https://cim.ucaiug.io/ns#Analog.positiveFlowIn> ?posFlowIn .\n OPTIONAL\
        \ { ?meas <https://cim.ucaiug.io/rules#Measurement.isInCognite> ?isInCognite\
        \ }\n FILTER( ?type = \"ThreePhaseActivePower-Flow-Estimated\"^^xsd:string\
        \ || ?type = \"ThreePhaseActivePower\"^^xsd:string )\n}"
    id: call_C3qAMjRWOrBZCU4QyPOx3X5D
    status: success
    execution_timestamp: '2025-12-15T15:06:59Z'
    output: "{\n \"head\": {\n \"vars\": [\n \"border\",\n \"meas\",\n \"mrid\",\n\
      \ \"type\",\n \"posFlowIn\",\n \"isInCognite\"\n ]\n },\n \"results\": {\n \"\
      bindings\": [\n {\n \"border\": {\n \"type\": \"uri\",\n \"value\": \"urn:uuid:852b95c0-4c49-4ded-85b2-a8f2b610db30\"\
      \n },\n \"meas\": {\n \"type\": \"uri\",\n \"value\": \"urn:uuid:9bb00fb1-4e7f-831a-e040-1e828c94e833\"\
      \n },\n \"mrid\": {\n \"type\": \"literal\",\n \"value\": \"9bb00fb1-4e7f-831a-e040-1e828c94e833\"\
      \n },\n \"type\": {\n \"type\": \"literal\",\n \"value\": \"ThreePhaseActivePower-Flow-Estimated\"\
      \n },\n \"posFlowIn\": {\n \"datatype\": \"http://www.w3.org/2001/XMLSchema#boolean\"\
      ,\n \"type\": \"literal\",\n \"value\": \"true\"\n },\n \"isInCognite\": {\n\
      \ \"datatype\": \"http://www.w3.org/2001/XMLSchema#boolean\",\n \"type\": \"\
      literal\",\n \"value\": \"true\"\n }\n }\n ]\n }\n}"
  - name: retrieve_time_series
    args:
      mrid: 9bb00fb1-4e7f-831a-e040-1e828c94e833
      limit: 5
    id: call_oU7gHlH48L7IqDl4T9CVkUbc
    status: success
    execution_timestamp: '2025-12-15T15:07:05Z'
    output: "[\n {\n \"external_id\": \"9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value\"\
      ,\n \"name\": \"Elspot NO1-NO3 MW_estimated_value\",\n \"is_string\": false,\n\
      \ \"metadata\": {\n \"unit\": \"MW\",\n \"measurement_type\": \"ThreePhaseActivePower\"\
      ,\n \"mrid\": \"9bb00fb1-4e7f-831a-e040-1e828c94e833\",\n \"unit_symbol\": \"\
      W\",\n \"timeseries_type\": \"estimated_value\",\n \"substation\": \"DIV_NCC\"\
      ,\n \"end_time\": \"\",\n \"topic\": \"observations_grid_power_no_ems_analog_active_power_res_1s_avro_v1\"\
      ,\n \"unit_multiplier\": \"M\",\n \"source\": \"eTerra\",\n \"subscription\"\
      : \"DIV_NCC\",\n \"device\": \"ELSPOT\"\n },\n \"unit\": \"MW\",\n \"asset_id\"\
      : 2296222851104770,\n \"is_step\": false,\n \"description\": \"ThreePhaseActivePower\"\
      ,\n \"security_categories\": [],\n \"data_set_id\": 5515145765342807,\n \"id\"\
      : 2314805086177702,\n \"created_time\": \"2023-06-13 21:11:59.579+00:00\",\n\
      \ \"last_updated_time\": \"2025-09-29 12:22:45.755+00:00\"\n }\n]"
  - name: retrieve_data_points
    args:
      external_id: 9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value
      start: '2025-01-01T00:00:00Z'
      end: '2026-01-01T00:00:00Z'
      aggregates:
      - min
      - max
      - average
      granularity: 1week
    id: call_1MA7PL4KAPJ7riH2UrxseyZW
    status: success
    execution_timestamp: '2025-12-15T15:07:14Z'
    output: "{\n \"id\": 2314805086177702,\n \"externalId\": \"9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value\"\
      ,\n \"isString\": false,\n \"isStep\": false,\n \"unit\": \"MW\",\n \"unitExternalId\"\
      : \"\",\n \"granularity\": \"1week\",\n \"datapoints\": [\n {\n \"timestamp\"\
      : \"2025-01-01 00:00:00\",\n \"max\": -22.4774875640869,\n \"min\": -634.605163574219,\n\
      \ \"sum\": -6079679.572650909\n },\n {\n \"timestamp\": \"2025-01-08 00:00:00\"\
      ,\n \"max\": -176.806610107422,\n \"min\": -592.054992675781,\n \"sum\": -7497037.204193115\n\
      \ },\n {\n \"timestamp\": \"2025-01-15 00:00:00\",\n \"max\": -48.8348274230957,\n\
      \ \"min\": -604.223022460938,\n \"sum\": -7033178.197429657\n },\n {\n \"timestamp\"\
      : \"2025-01-22 00:00:00\",\n \"max\": -93.4801940917969,\n \"min\": -638.378295898438,\n\
      \ \"sum\": -6409085.44443512\n },\n {\n \"timestamp\": \"2025-01-29 00:00:00\"\
      ,\n \"max\": -174.200958251953,\n \"min\": -591.80126953125,\n \"sum\": -5810485.415344238\n\
      \ },\n {\n \"timestamp\": \"2025-02-05 00:00:00\",\n \"max\": -129.160598754883,\n\
      \ \"min\": -583.906555175781,\n \"sum\": -5875491.905670166\n },\n {\n \"timestamp\"\
      : \"2025-02-12 00:00:00\",\n \"max\": -82.5265808105469,\n \"min\": -473.589019775391,\n\
      \ \"sum\": -4749596.438865662\n },\n {\n \"timestamp\": \"2025-02-19 00:00:00\"\
      ,\n \"max\": -94.3547592163086,\n \"min\": -553.544799804687,\n \"sum\": -6127722.962348938\n\
      \ },\n {\n \"timestamp\": \"2025-02-26 00:00:00\",\n \"max\": 39.375675201416,\n\
      \ \"min\": -495.355010986328,\n \"sum\": -5909059.358499527\n },\n {\n \"timestamp\"\
      : \"2025-03-05 00:00:00\",\n \"max\": -0.723251342773438,\n \"min\": -444.584655761719,\n\
      \ \"sum\": -5032459.175174713\n },\n {\n \"timestamp\": \"2025-03-12 00:00:00\"\
      ,\n \"max\": 53.3467674255371,\n \"min\": -367.410522460938,\n \"sum\": -3308910.4881810993\n\
      \ },\n {\n \"timestamp\": \"2025-03-19 00:00:00\",\n \"max\": 165.641891479492,\n\
      \ \"min\": -345.912719726563,\n \"sum\": -3240730.651639104\n },\n {\n \"timestamp\"\
      : \"2025-03-26 00:00:00\",\n \"max\": 81.5682983398438,\n \"min\": -420.76953125,\n\
      \ \"sum\": -5090794.093489647\n },\n {\n \"timestamp\": \"2025-04-02 00:00:00\"\
      ,\n \"max\": 66.1184768676758,\n \"min\": -415.227844238281,\n \"sum\": -4365653.5047190515\n\
      \ },\n {\n \"timestamp\": \"2025-04-09 00:00:00\",\n \"max\": 113.980033874512,\n\
      \ \"min\": -352.113433837891,\n \"sum\": -3703392.03900598\n },\n {\n \"timestamp\"\
      : \"2025-04-16 00:00:00\",\n \"max\": -23.1248321533203,\n \"min\": -418.720520019531,\n\
      \ \"sum\": -2175163.6172618866\n },\n {\n \"timestamp\": \"2025-04-23 00:00:00\"\
      ,\n \"max\": 66.5215454101563,\n \"min\": -409.330108642578,\n \"sum\": -4216380.705057085\n\
      \ },\n {\n \"timestamp\": \"2025-04-30 00:00:00\",\n \"max\": 36.223258972168,\n\
      \ \"min\": -443.705169677734,\n \"sum\": -2727791.800246954\n },\n {\n \"timestamp\"\
      : \"2025-05-07 00:00:00\",\n \"max\": -101.288871765137,\n \"min\": -464.468048095703,\n\
      \ \"sum\": -3374325.6654815674\n },\n {\n \"timestamp\": \"2025-05-14 00:00:00\"\
      ,\n \"max\": -65.273193359375,\n \"min\": -515.709655761719,\n \"sum\": -4706765.8790130615\n\
      \ },\n {\n \"timestamp\": \"2025-05-21 00:00:00\",\n \"max\": 2.4623658657074,\n\
      \ \"min\": -628.811157226562,\n \"sum\": -5354630.00902313\n },\n {\n \"timestamp\"\
      : \"2025-05-28 00:00:00\",\n \"max\": 86.4481430053711,\n \"min\": -648.408813476563,\n\
      \ \"sum\": -6994838.807719275\n },\n {\n \"timestamp\": \"2025-06-04 00:00:00\"\
      ,\n \"max\": 101.356071472168,\n \"min\": -586.686218261719,\n \"sum\": -13510767.91916069\n\
      \ },\n {\n \"timestamp\": \"2025-06-11 00:00:00\",\n \"max\": 163.898529052734,\n\
      \ \"min\": -556.988159179688,\n \"sum\": -14113734.887452226\n },\n {\n \"timestamp\"\
      : \"2025-06-18 00:00:00\",\n \"max\": 47.9553833007813,\n \"min\": -566.966491699219,\n\
      \ \"sum\": -5525602.276288301\n },\n {\n \"timestamp\": \"2025-06-25 00:00:00\"\
      ,\n \"max\": 82.483642578125,\n \"min\": -481.129364013672,\n \"sum\": -4503993.2934425045\n\
      \ },\n {\n \"timestamp\": \"2025-07-02 00:00:00\",\n \"max\": 4.44720029830933,\n\
      \ \"min\": -645.917663574219,\n \"sum\": -3699148.5399570465\n },\n {\n \"timestamp\"\
      : \"2025-07-09 00:00:00\",\n \"max\": 18.5413227081299,\n \"min\": -433.975158691406,\n\
      \ \"sum\": -2930218.747092165\n },\n {\n \"timestamp\": \"2025-07-16 00:00:00\"\
      ,\n \"max\": 9.86935138702393,\n \"min\": -466.966949462891,\n \"sum\": -4869006.952767938\n\
      \ },\n {\n \"timestamp\": \"2025-07-23 00:00:00\",\n \"max\": -79.1166152954102,\n\
      \ \"min\": -416.107727050781,\n \"sum\": -4550968.429283142\n },\n {\n \"timestamp\"\
      : \"2025-07-30 00:00:00\",\n \"max\": 206.594253540039,\n \"min\": -428.860229492188,\n\
      \ \"sum\": -3211479.5606954247\n },\n {\n \"timestamp\": \"2025-08-06 00:00:00\"\
      ,\n \"max\": 211.718780517578,\n \"min\": -428.881683349609,\n \"sum\": -1789749.3762937572\n\
      \ },\n {\n \"timestamp\": \"2025-08-13 00:00:00\",\n \"max\": 68.2974395751953,\n\
      \ \"min\": -23.84885597229,\n \"sum\": 120343.40388285261\n },\n {\n \"timestamp\"\
      : \"2025-08-20 00:00:00\",\n \"max\": 219.931503295898,\n \"min\": -8.17569255828857,\n\
      \ \"sum\": 955194.8288861046\n },\n {\n \"timestamp\": \"2025-08-27 00:00:00\"\
      ,\n \"max\": 183.314514160156,\n \"min\": -687.299377441406,\n \"sum\": -12165633.712079525\n\
      \ },\n {\n \"timestamp\": \"2025-09-03 00:00:00\",\n \"max\": 51.6008987426758,\n\
      \ \"min\": -627.613830566406,\n \"sum\": -16095338.66005943\n },\n {\n \"timestamp\"\
      : \"2025-09-10 00:00:00\",\n \"max\": 57.2205429077148,\n \"min\": -563.739929199219,\n\
      \ \"sum\": -10858557.12343351\n },\n {\n \"timestamp\": \"2025-09-17 00:00:00\"\
      ,\n \"max\": 205.345397949219,\n \"min\": -550.26513671875,\n \"sum\": -10393817.01633801\n\
      \ },\n {\n \"timestamp\": \"2025-09-24 00:00:00\",\n \"max\": 268.643463134766,\n\
      \ \"min\": -549.864868164063,\n \"sum\": -6616383.323891792\n },\n {\n \"timestamp\"\
      : \"2025-10-01 00:00:00\",\n \"max\": 318.965423583984,\n \"min\": -432.655151367188,\n\
      \ \"sum\": -1600749.2544672987\n },\n {\n \"timestamp\": \"2025-10-08 00:00:00\"\
      ,\n \"max\": -3.35211229324341,\n \"min\": -471.751831054688,\n \"sum\": -5144527.891113758\n\
      \ },\n {\n \"timestamp\": \"2025-10-15 00:00:00\",\n \"max\": 90.3368453979492,\n\
      \ \"min\": -471.285675048828,\n \"sum\": -3875047.637278557\n },\n {\n \"timestamp\"\
      : \"2025-10-22 00:00:00\",\n \"max\": 110.84740447998,\n \"min\": -483.147857666016,\n\
      \ \"sum\": -3056732.2498025894\n },\n {\n \"timestamp\": \"2025-10-29 00:00:00\"\
      ,\n \"max\": 109.893417358398,\n \"min\": -440.507598876953,\n \"sum\": -2343687.2623984218\n\
      \ },\n {\n \"timestamp\": \"2025-11-05 00:00:00\",\n \"max\": 120.950942993164,\n\
      \ \"min\": -401.896026611328,\n \"sum\": -2414128.2356422693\n },\n {\n \"timestamp\"\
      : \"2025-11-12 00:00:00\",\n \"max\": 100.14469909668,\n \"min\": -384.338897705078,\n\
      \ \"sum\": -1426443.203330338\n },\n {\n \"timestamp\": \"2025-11-19 00:00:00\"\
      ,\n \"max\": 120.508186340332,\n \"min\": 86.9833068847656,\n \"sum\": 362196.56188201904\n\
      \ },\n {\n \"timestamp\": \"2025-11-26 00:00:00\",\n \"max\": 120.065689086914,\n\
      \ \"min\": -473.767059326172,\n \"sum\": -3704030.113606751\n },\n {\n \"timestamp\"\
      : \"2025-12-03 00:00:00\",\n \"max\": -18.4274024963379,\n \"min\": -430.414184570312,\n\
      \ \"sum\": -3881328.2995967865\n },\n {\n \"timestamp\": \"2025-12-10 00:00:00\"\
      ,\n \"max\": -106.10661315918,\n \"min\": -416.067596435547,\n \"sum\": -1366852.111000061\n\
      \ }\n ]\n}"
  steps_score: 0.75
  input_tokens: 791569
  output_tokens: 15522
  total_tokens: 807091
  elapsed_sec: 205.36997318267822
```

### Output Keys

- `template_id`: the template id
- `question_id`: the question id
- `question_text`: the natural language query
- `status`: "success" or "error", indicating whether the evaluation succeeded
- `reference_steps`: (optional) copy of the expected steps in the Q&A dataset, if specified there. Additional key "matches" is added to those steps, which are matched 
- `reference_answer`: (optional) copy of the expected answer in the Q&A dataset, if specified there
- `actual_answer`: (optional) copy of the response text in the evaluation target, if specified there
- `answer_reference_claims_count`: (optional) number of claims extracted from the reference answer, if a reference answer and actual answer are available
- `answer_actual_claims_count`: (optional) number of claims extracted from the answer being evaluated, if a reference answer and actual answer are available
- `answer_matching_claims_count`: (optional) number of matching claims between the reference answer and the actual answer, if a reference answer and actual answer are available
- `answer_recall`: (optional) `answer_matching_claims_count / answer_reference_claims_count`
- `answer_precision`: (optional) `answer_matching_claims_count / answer_actual_claims_count`
- `answer_correctness_reason`: (optional) LLM reasoning in extracting and matching claims from the reference answer and the actual answer
- `answer_eval_error`: (optional) error message if answer evaluation failed
- `answer_f1`: (optional) Harmonic mean of `answer_recall` and `answer_precision`
- `answer_relevance`: (optional) The value representing how relevant is the actual answer to the question, computed using [RAGAS answer relevance](https://docs.ragas.io/en/v0.3.3/concepts/metrics/available_metrics/answer_relevance/)
- `answer_relevance_error`: (optional) error message if answer relevance evaluation failed
- `answer_relevance_cost`: (optional) The LLM use cost of computing `answer_relevance`, in US dollars
- `actual_steps`: (optional) copy of the steps in the evaluation target, if specified there
- `steps_score`: (optional) a real number between 0 and 1, see how step score is calculated in the section [Steps score](#Steps-score)
- `input_tokens`: (optional) input tokens usage
- `output_tokens`: (optional) output tokens usage
- `total_tokens`: (optional) total tokens usage
- `elapsed_sec`: (optional) elapsed seconds

All `actual_steps` with `name` "retrieval" contain:
- `retrieval_answer_recall`: (optional) recall of the retrieved context with respect to the reference answer, if evaluation succeeds
- `retrieval_answer_recall_reason`: (optional) LLM reasoning in evaluating `retrieval_answer_recall`
- `retrieval_answer_recall_error`: (optional) error message if `retrieval_answer_recall` evaluation fails
- `retrieval_answer_recall_cost`: cost of evaluating `retrieval_answer_recall`, in US dollars
- `retrieval_answer_precision`: (optional) precision of the retrieved context with respect to the reference answer, if evaluation succeeds
- `retrieval_answer_precision_error`: (optional) error message if `retrieval_answer_precision` evaluation fails
- `retrieval_answer_precision_cost`: cost of evaluating `retrieval_answer_precision`, in US dollars
- `retrieval_answer_f1`: (optional) F1 score of the retrieved context with respect to the reference answer, if `retrieval_answer_recall` and `retrieval_answer_precision` succeed
- `retrieval_answer_f1_cost`: The sum of `retrieval_answer_recall_cost` and `retrieval_answer_precision_cost`
- `retrieval_context_recall`: (optional) recall of the retrieved context with respect to the reference answer, if evaluation succeeds
- `retrieval_context_recall_error`: (optional) error message if `retrieval_context_recall` evaluation fails
- `retrieval_context_precision`: (optional) precision of the retrieved context with respect to the reference answer, if evaluation succeeds
- `retrieval_context_precision_error`: (optional) error message if `retrieval_context_precision` evaluation fails
- `retrieval_context_f1`: (optional) F1 score of the retrieved context with respect to the reference answer, if `retrieval_context_recall` and `retrieval_context_precision` succeed

#### Aggregates Keys

The `aggregates` object provides aggregated evaluation metrics. These aggregates support analysis of agent quality, 
token efficiency, and execution performance. Aggregates are computed:
1. per question template, and
1. over all questions in the dataset, using micro and macro averaging

Aggregates are:
- `per_template`: a dictionary mapping a template identifier to the following statistics:
  - `number_of_error_samples`: number of questions for this template, which resulted in error response
  - `number_of_success_samples`: number of questions for this template, which resulted in successful response
  - `sum`, `mean`, `median`, `min` and `max` statistics for the following metrics over all questions of this template for which the metrics exist:
    - `input_tokens`
    - `output_tokens`
    - `total_tokens`
    - `elapsed_sec`
    - `answer_recall`
    - `answer_precision`
    - `answer_f1`
    - `answer_relevance`
    - `steps_score`
    - `retrieval_answer_recall`
    - `retrieval_answer_precision`
    - `retrieval_answer_f1`
    - `retrieval_context_recall`
    - `retrieval_context_precision`
    - `retrieval_context_f1`
    - `steps`: includes:
      - `total`: for each step type how many times it was executed
      - `once_per_sample`: how many times each step was executed, counted only once per question
      - `empty_results`: how many times the step was executed and returned empty results
      - `errors`: how many times the step was executed and resulted in error
- `micro`: statistics across questions, regardless of template. It includes:
  - `number_of_error_samples`: total number of questions, which resulted in error response
  - `number_of_success_samples`: total number of questions, which resulted in successful response
  - `steps`: includes:
    - `total`: for each step type how many times it was executed
    - `once_per_sample`: how many times each step was executed, counted only once per question
    - `empty_results`: how many times the step was executed and returned empty results
    - `errors`: how many times the step was executed and resulted in error
  - `sum`, `mean`, `median`, `min` and `max` statistics for the following metrics, over all questions where the metrics exist:
    - `input_tokens`
    - `output_tokens`
    - `total_tokens`
    - `elapsed_sec`
    - `answer_recall`
    - `answer_precision`
    - `answer_f1`
    - `answer_relevance`
    - `answer_relevance_cost`
    - `retrieval_answer_recall`
    - `retrieval_answer_precision`
    - `retrieval_answer_f1`
    - `retrieval_context_recall`
    - `retrieval_context_precision`
    - `retrieval_context_f1`
    - `steps_score`
- `macro`: averages across templates, i.e., the mean of each metric per template, averaged. It includes the following means:
  - `input_tokens`
  - `output_tokens`
  - `total_tokens`
  - `elapsed_sec`
  - `answer_recall`
  - `answer_precision`
  - `answer_f1`
  - `answer_relevance`
  - `answer_relevance_cost`
  - `retrieval_answer_recall`
  - `retrieval_answer_precision`
  - `retrieval_answer_f1`
  - `retrieval_context_recall`
  - `retrieval_context_precision`
  - `retrieval_context_f1`
  - `steps_score`

#### Example Aggregates

```yaml
per_template:
  list_all_transformers_within_Substation_SUBSTATION:
    number_of_error_samples: 0
    number_of_success_samples: 10
    answer_recall:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_precision:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_f1:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_relevance:
      min: 0.9
      max: 0.9
      mean: 0.9
      median: 0.9
      sum: 0.9
    answer_relevance_cost:
      min: 0.0007
      max: 0.0007
      mean: 0.0007
      median: 0.0007
      sum: 0.0007
    steps:
      total:
        autocomplete_search: 10
        sparql_query: 8
      once_per_sample:
        autocomplete_search: 10
        sparql_query: 8
      empty_results:
        autocomplete_search: 2
    steps_score:
      sum: 8
      mean: 0.8
      median: 1
      min: 0
      max: 1
    input_tokens:
      sum: 2064559
      mean: 206455.9
      median: 221263.5
      min: 147171
      max: 221339
    output_tokens:
      sum: 1555
      mean: 155.5
      median: 177
      min: 46
      max: 212
    total_tokens:
      sum: 2066114
      mean: 206611.4
      median: 221439.5
      min: 147217
      max: 221551
    elapsed_sec:
      sum: 259.2278094291687
      mean: 25.92278094291687
      median: 9.677194952964783
      min: 5.529741525650024
      max: 55.4010910987854
  list_all_substations_within_bidding_zone_REGION:
    number_of_error_samples: 0
    number_of_success_samples: 10
    answer_recall:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_precision:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_f1:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_relevance:
      min: 0.9
      max: 0.9
      mean: 0.9
      median: 0.9
      sum: 0.9
    answer_relevance_cost:
      min: 0.0007
      max: 0.0007
      mean: 0.0007
      median: 0.0007
      sum: 0.0007
    steps:
      total:
        autocomplete_search: 10
      once_per_sample:
        autocomplete_search: 10
      empty_results:
        autocomplete_search: 10
    steps_score:
      sum: 0
      mean: 0
      median: 0
      min: 0
      max: 0
    input_tokens:
      sum: 1471880
      mean: 147188
      median: 147188
      min: 147188
      max: 147188
    output_tokens:
      sum: 571
      mean: 57.1
      median: 57
      min: 56
      max: 61
    total_tokens:
      sum: 1472451
      mean: 147245.1
      median: 147245
      min: 147244
      max: 147249
    elapsed_sec:
      sum: 185.5483124256134
      mean: 18.55483124256134
      median: 8.886059165000916
      min: 2.8653159141540527
      max: 47.51542258262634
  list_all_substations_that_are_connected_via_an_ac_line_or_a_dc_line_to_substation_named_SUBSTATION:
    number_of_error_samples: 1
    number_of_success_samples: 9
    answer_recall:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_precision:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_f1:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_relevance:
      min: 0.9
      max: 0.9
      mean: 0.9
      median: 0.9
      sum: 0.9
    answer_relevance_cost:
      min: 0.0007
      max: 0.0007
      mean: 0.0007
      median: 0.0007
      sum: 0.0007
    steps:
      total:
        autocomplete_search: 9
        sparql_query: 17
      once_per_sample:
        autocomplete_search: 9
        sparql_query: 9
      errors:
        sparql_query: 8
    steps_score:
      sum: 9
      mean: 1
      median: 1
      min: 1
      max: 1
    input_tokens:
      sum: 2601595
      mean: 289066.1111111111
      median: 297059
      min: 222528
      max: 298028
    output_tokens:
      sum: 6066
      mean: 674
      median: 700
      min: 363
      max: 805
    total_tokens:
      sum: 2607661
      mean: 289740.1111111111
      median: 297759
      min: 222891
      max: 298787
    elapsed_sec:
      sum: 354.82168316841125
      mean: 39.42463146315681
      median: 41.88556528091431
      min: 26.418761014938354
      max: 52.42662525177002
  list_all_ac_lines_that_traverse_bidding_zones_REGION1_and_REGION2:
    number_of_error_samples: 0
    number_of_success_samples: 10
    answer_recall:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_precision:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_f1:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_relevance:
      min: 0.9
      max: 0.9
      mean: 0.9
      median: 0.9
      sum: 0.9
    answer_relevance_cost:
      min: 0.0007
      max: 0.0007
      mean: 0.0007
      median: 0.0007
      sum: 0.0007
    steps:
      total:
        autocomplete_search: 20
      once_per_sample:
        autocomplete_search: 10
      empty_results:
        autocomplete_search: 20
    steps_score:
      sum: 0
      mean: 0
      median: 0
      min: 0
      max: 0
    input_tokens:
      sum: 1472540
      mean: 147254
      median: 147254
      min: 147254
      max: 147254
    output_tokens:
      sum: 1052
      mean: 105.2
      median: 105
      min: 105
      max: 107
    total_tokens:
      sum: 1473592
      mean: 147359.2
      median: 147359
      min: 147359
      max: 147361
    elapsed_sec:
      sum: 197.44370341300964
      mean: 19.744370341300964
      median: 18.030158162117004
      min: 15.56333041191101
      max: 26.422670125961304
micro:
  number_of_error_samples: 1
  number_of_success_samples: 39
  answer_recall:
    sum: 1.0
    mean: 1.0
    median: 1.0
    min: 1.0
    max: 1.0
  answer_precision:
    sum: 1.0
    mean: 1.0
    median: 1.0
    min: 1.0
    max: 1.0
  answer_f1:
    sum: 1.0
    mean: 1.0
    median: 1.0
    min: 1.0
    max: 1.0
  answer_relevance:
    min: 0.9
    max: 0.9
    mean: 0.9
    median: 0.9
    sum: 0.9
  answer_relevance_cost:
    min: 0.0007
    max: 0.0007
    mean: 0.0007
    median: 0.0007
    sum: 0.0007
  steps_score:
    sum: 17
    mean: 0.4358974358974359
    median: 0
    min: 0
    max: 1
  input_tokens:
    sum: 7610574
    mean: 195142.92307692306
    median: 147254
    min: 147171
    max: 298028
  output_tokens:
    sum: 9244
    mean: 237.02564102564102
    median: 105
    min: 46
    max: 805
  total_tokens:
    sum: 7619818
    mean: 195379.94871794872
    median: 147359
    min: 147217
    max: 298787
  elapsed_sec:
    sum: 997.041508436203
    mean: 25.565166882979565
    median: 18.32871961593628
    min: 2.8653159141540527
    max: 55.4010910987854
macro:
  answer_recall:
    mean: 1.0
  answer_precision:
    mean: 1.0
  answer_f1:
    mean: 1.0
  answer_relevance:
    mean: 0.9
  answer_relevance_cost:
    mean: 0.0007
  steps_score:
    mean: 0.45
  input_tokens:
    mean: 197491.0027777778
  output_tokens:
    mean: 247.95
  total_tokens:
    mean: 197738.9527777778
  elapsed_sec:
    mean: 25.911653497483996
```

### Steps score

The steps score is a real number in the interval [0, 1], which indicates how closely the actual steps match to the reference ones.
A score of 1 indicates a perfect match.

Going in reverse order of the reference groups and in reverse order of the actual steps, 
for each reference group we try to match each step in the group to an actual step.

If all steps from the current reference group are matched, we proceed to the previous group, 
but we only search among the actual steps before the earliest actual step already matched for the current group.
The intuition is that we don’t care about the execution order of steps within a reference group, 
but we do want the groups to be matched in order: steps from earlier reference groups must be matched before 
the steps from later reference groups.

If some of the steps in a reference group are not matched, we stop.

An actual step can match at most one reference step, and only if the actual step is successful 
(i.e., it didn’t result in an error).

There are a few ways a reference step can match an actual one. In all cases except for the "retrieval" steps,
the matching score is either 0 or 1. A score above 0 indicates a match.

- if both are named "sparql_query" and the "output_media_type" of the reference step is "application/sparql-results+json", 
then we try to match them using the [SPARQL queries comparison algorithm](#sparql-queries-comparison).
- if both are named "retrieval" and the reference step has "output", then we compute [recall@k](#context-recallk).
- if both are named "retrieve_time_series", then we check if the arguments of the steps are matching.
- if both are named "retrieve_data_points", then we check if the arguments of the steps are matching.
- if the reference step is named "iri_discovery" and the actual step name is "autocomplete_search",
then check if the IRI specified as "output" of the "iri_discovery" step is present in the "output" of the "autocomplete_search".
- if the reference and actual step names are the same and 
the "output_media_type" of the reference step is "application/json", then the steps match,
if the json outputs are the same. 
- we fallback to match the outputs of the two steps. 

The final steps score is the accumulated sum for all reference groups divided by their total number.
The score for an individual reference group is the accumulated score for each step in this group divided by their total number.

#### SPARQL queries comparison

The algorithm iterates over all subsets of columns in the actual result of the same size as in the reference result.
For each subset, it compares the set of columns (skipping optional columns).
It matches floating-point numbers up to a 1e-8 precision. It does not do this for special types such as duration.

The average time complexity is О(nr\*nc_ref!\*binomial(nc_act, nc_ref)), where

* *nr* is the number of rows in the actual result
* *nc_ref* is the number of columns in the reference result
* *nc_act* is the number of columns in the actual result

### Retrieval Evaluation

The following metrics are based on the content of retrieved documents.

#### Context Recall@k

The fraction of relevant items among the top *k* recommendations. It answers the question: "Of all items the user cares about, how many did we include in the first k spots?"
* **Formula**:
    $`
    \frac{\text{Number of relevant items in top k}}{\text{Number of relevant items}}
    `$
* **Calculation**: Count the number of relevant items in the top `k` retrieved results; divide that by the first 'k' relevant items.
* **Example**: Suppose there are 4 relevant documents for a given query. Suppose our system retrieves 3 of them in the top 5 results (`k=5`). Recall@5 is `3 / 4 = 0.75`.

```python
recall_at_k(
    relevant_docs={1, 3, 5, 6},
    retrieved_docs=[1, 4, 3, 5, 7],
    k=5
)  # => 0.75
```

#### Context Precision@k

Evaluates a ranked list of recommendations by looking at the precision at the position of each correctly retrieved item. It rewards systems for placing relevant items higher up in the list. It's more sophisticated than just looking at precision at a single cutoff because it considers the entire ranking.
* **Formula**:
    $`
    \frac{\sum_{k=1}^{n} (P(k) \times \text{rel}(k))}{\text{Number of relevant items}}
    `$,\
    where:
    * `P(k)` is the precision at rank `k`
    * `rel(k)` is 1 if the item at rank `k` is relevant and 0 otherwise.
* **Calculation**:
    1. For each retrieved item, if it is relevant, record the precision at that index (i.e., `number of hits / current rank`).
    2. Average all of these precision scores.
    3. Divide that average by the total number of relevant items.
* **Example**:
    * Suppose:
      * The relevant items are `1, 3, 5, 6`
      * Our system retrieves `1, 4, 3, 5, 7`
    * Calculation:
      * Item at index 1 (item 1) is relevant. Precision@1 = 1/1
      * Item at index 3 (item 2) is relevant. Precision@3 = 2/3
      * Item at index 4 (item 5) is relevant. Precision@4 = 3/4
      * AP = (1.0 + 2/3 + 3/4) / 3 = 0.8055...

```python
average_precision(
    relevant_docs={1, 3, 5, 6},
    retrieved_docs=[1, 4, 3, 5, 7]
) # ~=> 0.8056
```
