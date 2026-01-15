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
