from graphrag_eval.steps.iri_discovery import do_iri_discovery_steps_equal


def test_do_iri_discovery_steps_equal():
    reference_step = {
        "name": "iri_discovery",
        "output": "urn:uuid:83aa03e5-5fd0-431c-b8dd-acc08c21ed6a",
        "args": {
            "query": "NO1",
        }
    }
    assert do_iri_discovery_steps_equal(reference_step, reference_step) == False

    actual_step = {
        "name": "autocomplete_search",
        "args": {
            "query": "NO1",
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
        "output": "{\"head\":{\"vars\":[\"iri\",\"name\",\"class\",\"rank\"]},\"results\":{\"bindings\":[{\"iri\":{\"type\":\"uri\",\"value\":\"urn:uuid:83aa03e5-5fd0-431c-b8dd-acc08c21ed6a\"},\"name\":{\"type\":\"literal\",\"value\":\"NO1\"},\"class\":{\"type\":\"uri\",\"value\":\"https://cim4.eu/ns/nc#BiddingZone\"},\"rank\":{\"datatype\":\"http://www.w3.org/2001/XMLSchema#float\",\"type\":\"literal\",\"value\":\"0.01489\"}}]}}"
    }
    assert do_iri_discovery_steps_equal(reference_step, actual_step) == True

    actual_step = {
        "name": "autocomplete_search",
        "args": {
            "query": "NO1",
            "result_class": "nc:BiddingZone",
            "limit": 5,
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
        "output": "{\"head\":{\"vars\":[\"iri\",\"name\",\"class\",\"rank\"]},\"results\":{\"bindings\":[{\"iri\":{\"type\":\"uri\",\"value\":\"urn:uuid:83aa03e5-5fd0-431c-b8dd-acc08c21ed6a\"},\"name\":{\"type\":\"literal\",\"value\":\"NO1\"},\"class\":{\"type\":\"uri\",\"value\":\"https://cim4.eu/ns/nc#BiddingZone\"},\"rank\":{\"datatype\":\"http://www.w3.org/2001/XMLSchema#float\",\"type\":\"literal\",\"value\":\"0.01489\"}}]}}"
    }
    assert do_iri_discovery_steps_equal(reference_step, actual_step) == True

    actual_step = {
        "name": "autocomplete_search",
        "args": {
            "query": "NO1",
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
        "output": "{\"head\":{\"vars\":[\"iri\",\"name\",\"class\",\"rank\"]},\"results\":{\"bindings\":[]}}"
    }
    assert do_iri_discovery_steps_equal(reference_step, actual_step) == False

    reference_step = {
        "name": "iri_discovery",
        "output": "urn:uuid:734aa25e-9549-11ec-b226-48ba4eadba68",
        "args": {
            "query": "734aa25e",
        }
    }
    actual_step = {
        "name": "sparql_query",
        "args": {
            "query": "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> "
                     "PREFIX cimr: <https://cim.ucaiug.io/rules#> "
                     "SELECT ?entity ?class { "
                     "  ?entity cimr:mridSignificantPart ?id ; a ?class . "
                     "  FILTER (?id =  \"734aa25e\"^^xsd:string) "
                     "}",
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
        "output": "{\n  \"head\": {\n    \"vars\": [\n      \"entity\",\n      \"class\"\n    ]\n  },\n  \"results\": {\n    \"bindings\": [\n      {\n        \"entity\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:734aa25e-9549-11ec-b226-48ba4eadba68\"\n        },\n        \"class\": {\n          \"type\": \"uri\",\n          \"value\": \"https://cim.ucaiug.io/ns#IdentifiedObject\"\n        }\n      },\n      {\n        \"entity\": {\n          \"type\": \"uri\",\n          \"value\": \"urn:uuid:734aa25e-9549-11ec-b226-48ba4eadba68\"\n        },\n        \"class\": {\n          \"type\": \"uri\",\n          \"value\": \"https://cim.ucaiug.io/ns#TopologicalIsland\"\n        }\n      }\n    ]\n  }\n}"
    }
    assert do_iri_discovery_steps_equal(reference_step, actual_step) == True
