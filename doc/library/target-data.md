### Responses to evaluate

Given a question, if the question-answering system successfully responds, to evaluate the response, call `run_evaluation()` with the response formatted as in the example below. (On the other hand, if an error occurs while generating a response, format it as in [Target Input on Error](#target-input-on-error).)

```json
{
    "question_id": "f91fc938d606e5f6089912bebfaf114b",
    "input_tokens": 298028,
    "output_tokens": 725,
    "total_tokens": 298753,
    "elapsed_sec": 46.48961806297302,
    "actual_steps": [
        {
            "name": "retrieval",
            "args": {
                "query": "transformers Substation OSLO",
                "k": 2
            },
            "id": "call_3",
            "status": "success",
            "output": "[\n  {\n    \"id\": \"http://example.com/resource/doc/1\",\n    \"text\": \"Transformer OSLO T1 is in Substation Oslo.\"\n  },\n  {\n    \"id\": \"http://example.com/resource/doc/2\",\n    \"text\": \"Transformer OSLO T2 is in Substation Oslo.\"\n  }\n]",
            "execution_timestamp": "2025-12-17T09:15:53Z"
        },
        {
            "name": "autocomplete_search",
            "args": {
                "query": "STAVANGER",
                "result_class": "cim:Substation"
            },
            "id": "call_7amIsfEGelOnVZ1DWtgtc0hc",
            "status": "success",
            "output": "{\n  \"head\": {\n    \"vars\": [\n      \"iri\",\n      \"name\",\n      \"rank\"\n    ]\n  },\n  \"results\": {\n    \"bindings\": [\n      {\n        \"iri\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769664-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"name\": {\n          \"type\": \"literal\",\n          \"value\": \"STAVANGER\"\n        },\n        \"rank\": {\n          \"datatype\": \"http://www.w3.org/2001/XMLSchema#float\",\n          \"type\": \"literal\",\n          \"value\": \"0.00976\"\n        }\n      }\n    ]\n  }\n}",
            "execution_timestamp": "2025-12-17T09:15:58Z"
        },
        {
            "name": "sparql_query",
            "args": {
                "query": "SELECT DISTINCT ?substation2 ?substation2Name ?line ?lineName WHERE {\n  # Substation STAVANGER\n  BIND(urn:uuid:f1769664-9aeb-11e5-91da-b8763fd99c5f AS ?substation1) .\n\n  # Find lines connected to STAVANGER\n  ?line a cim:Line ;\n        cimex:connectedThroughPart ?substation1, ?substation2 ;\n        cim:IdentifiedObject.name ?lineName .\n\n  # Ensure the connected substation is different from STAVANGER\n  ?substation2 a cim:Substation ;\n               cim:IdentifiedObject.name ?substation2Name .\n  FILTER(?substation1 != ?substation2)\n}"
            },
            "id": "call_DbMkZ8kv3qkf49wNNdREkpRN",
            "status": "error",
            "error": "Error: ValueError('The following prefixes are undefined: urn')\n Please fix your mistakes.",
            "execution_timestamp": "2025-12-17T09:16:03Z"
        },
        {
            "name": "sparql_query",
            "args": {
                "query": "SELECT DISTINCT ?substation2 ?substation2Name ?line ?lineName WHERE {\n  # Substation STAVANGER\n  BIND(<urn:uuid:f1769664-9aeb-11e5-91da-b8763fd99c5f> AS ?substation1) .\n\n  # Find lines connected to STAVANGER\n  ?line a cim:Line ;\n        cimex:connectedThroughPart ?substation1, ?substation2 ;\n        cim:IdentifiedObject.name ?lineName .\n\n  # Ensure the connected substation is different from STAVANGER\n  ?substation2 a cim:Substation ;\n               cim:IdentifiedObject.name ?substation2Name .\n  FILTER(?substation1 != ?substation2)\n}"
            },
            "id": "call_Qm1mzX7g5q9SVPrR2QzEMTp3",
            "status": "success",
            "output": "{\n  \"head\": {\n    \"vars\": [\n      \"substation2\",\n      \"substation2Name\",\n      \"line\",\n      \"lineName\"\n    ]\n  },\n  \"results\": {\n    \"bindings\": [\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f176965a-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"KRISTIANSAND\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:47332c85-17a4-7a41-abd5-2b92e4b800ed\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 300KRISTIAN-STAVANGE\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769614-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"DAGALI\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:c5f535a5-f053-a948-9cee-f6a7b07c7d4f\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420DAGALI-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769682-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"KVILLDAL\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:c5f535a5-f053-a948-9cee-f6a7b07c7d4f\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420DAGALI-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769688-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"HAGAFOSS\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:c5f535a5-f053-a948-9cee-f6a7b07c7d4f\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420DAGALI-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"OSLO\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:a93b83d7-8a39-ef48-8c29-36de1ac0eaf5\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420SYSLE-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769648-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"SYSLE\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:a93b83d7-8a39-ef48-8c29-36de1ac0eaf5\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420SYSLE-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769682-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"KVILLDAL\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:a93b83d7-8a39-ef48-8c29-36de1ac0eaf5\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420SYSLE-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769688-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"HAGAFOSS\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:a93b83d7-8a39-ef48-8c29-36de1ac0eaf5\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420SYSLE-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f176962a-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"AURLAND\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:293e49bc-c995-fc46-a69c-380876b317a1\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420AURLAND-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769682-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"KVILLDAL\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:293e49bc-c995-fc46-a69c-380876b317a1\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420AURLAND-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769688-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"HAGAFOSS\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:293e49bc-c995-fc46-a69c-380876b317a1\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420AURLAND-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769624-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"SIMA\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:293e49bc-c995-fc46-a69c-380876b317a1\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420AURLAND-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769642-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"SYLLING\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:163037f6-cf93-054e-8a6d-3f58de83b6a3\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420SYLLING-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f176963c-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"OSLO\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:163037f6-cf93-054e-8a6d-3f58de83b6a3\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420SYLLING-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769682-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"KVILLDAL\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:163037f6-cf93-054e-8a6d-3f58de83b6a3\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420SYLLING-HAGAFOSS\"\n        }\n      },\n      {\n        \"substation2\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:f1769688-9aeb-11e5-91da-b8763fd99c5f\"\n        },\n        \"substation2Name\": {\n          \"type\": \"literal\",\n          \"value\": \"HAGAFOSS\"\n        },\n        \"line\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:163037f6-cf93-054e-8a6d-3f58de83b6a3\"\n        },\n        \"lineName\": {\n          \"type\": \"literal\",\n          \"value\": \"LC 420SYLLING-HAGAFOSS\"\n        }\n      }\n    ]\n  }\n}",
            "execution_timestamp": "2025-12-17T09:16:08Z"
        }
    ],
    "actual_answer": "The substations connected to the substation \"STAVANGER\" via AC or DC lines are:\n\n1. **KRISTIANSAND** via line \"LC 300KRISTIAN-STAVANGE\"\n2. **DAGALI** via line \"LC 420DAGALI-HAGAFOSS\"\n3. **KVILLDAL** via lines:\n   - \"LC 420DAGALI-HAGAFOSS\"\n   - \"LC 420SYSLE-HAGAFOSS\"\n   - \"LC 420AURLAND-HAGAFOSS\"\n   - \"LC 420SYLLING-HAGAFOSS\"\n4. **HAGAFOSS** via lines:\n   - \"LC 420DAGALI-HAGAFOSS\"\n   - \"LC 420SYSLE-HAGAFOSS\"\n   - \"LC 420AURLAND-HAGAFOSS\"\n   - \"LC 420SYLLING-HAGAFOSS\"\n5. **OSLO** via lines:\n   - \"LC 420SYSLE-HAGAFOSS\"\n   - \"LC 420SYLLING-HAGAFOSS\"\n6. **SYSLE** via line \"LC 420SYSLE-HAGAFOSS\"\n7. **AURLAND** via line \"LC 420AURLAND-HAGAFOSS\"\n8. **SIMA** via line \"LC 420AURLAND-HAGAFOSS\"\n9. **SYLLING** via line \"LC 420SYLLING-HAGAFOSS\""
}
```

#### Target Input on Error

If an error occurs while the question-answering system is generating a response, and you want to tally this error, the input to `run_evaluate()` should be like:

```json
{
    "question_id": "a8daaf98b84b4f6b0e0052fb942bf6b6",
    "error": "Error message",
    "status": "error"
}
```
