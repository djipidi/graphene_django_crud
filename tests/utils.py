def verify_response(expected_response, response):
    if isinstance(expected_response, dict):
        assert isinstance(response, dict)
        iterator = expected_response.items()
    elif isinstance(expected_response, list):
        assert isinstance(response, list)
        assert len(expected_response) == len(response), (
            "len(list) didn't match :" + str(expected_response) + " == " + str(response)
        )
        iterator = enumerate(expected_response)
    else:
        assert expected_response == response, (
            "values didn't match :" + str(expected_response) + " == " + str(response)
        )
        return

    for key, value in iterator:
        if isinstance(value, (dict, list)):
            verify_response(value, response[key])
        else:
            assert value == response[key], (
                "values didn't match :" + str(value) + " == " + str(response[key])
            )
