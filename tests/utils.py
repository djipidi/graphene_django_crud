class VerifyResponseAssertionMixins:
    def verify_response(self, response, expected_response):
        if isinstance(expected_response, dict):
            self.assertIsInstance(response, dict)
            iterator = expected_response.items()
        elif isinstance(expected_response, list):
            self.assertIsInstance(response, list)
            self.assertEqual(len(expected_response), len(response), msg="len(list) didn't match")
            iterator = enumerate(expected_response)
        else:
            self.assertEqual(expected_response, response, msg=(
                "values didn't match :" + str(expected_response) + " == " + str(response)
            ))
            return

        for key, value in iterator:
            if isinstance(value, (dict, list)):
                self.verify_response(response[key], value)
            else:
                self.assertEqual(value, response[key], msg=(
                    "values didn't match :" + str(value) + " == " + str(response[key])
                ))

def verify_response(expected_response, response):
    assert False