from tests.client import Client
from graphene_django.utils.testing import GraphQLTestCase

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


class SchemaTestCase(GraphQLTestCase):

    QUERY_GET_TYPE = """
        fragment type on __Type {
          kind
          name
          ofType{
            kind
            name
          }
        }
        
        fragment inputValue on __InputValue {
          name
          type {
            ...type
          }
        }
        
        fragment field on __Field {
          name
          type {
            ...type
          }
          args {
            ...inputValue
          }
        }
        
        query ($name: String!) {
          __type(name: $name) {
            name
            fields {
              ...field
            }
            inputFields {
              ...inputValue
            }
          }
        }
    """

    def get_type(self, name):
        client = Client()
        response = client.query(self.QUERY_GET_TYPE, variables={"name": name}).json()
        return response["data"]["__type"]

    def get_field_by_name(self, type, name, input_field=False):
        fields_key = "inputFields" if input_field else "fields"
        return next(filter(lambda field: field["name"] == name, type[fields_key]))

    def assertFieldEqual(self, type_name, field_name, field_meta, input_type=False):
        gql_type = self.get_type(type_name)
        field = self.get_field_by_name(gql_type, field_name, input_field=input_type)
        self.assertDictEqual(field, field_meta)

    def runtest_fields_of_type(self, type_name, fields_to_test, input_type=False):
        gql_type = self.get_type(type_name)
        for ref_field in fields_to_test:
            with self.subTest(field=ref_field):
                field = self.get_field_by_name(
                    gql_type, ref_field["name"], input_field=input_type
                )
                self.assertDictEqual(field, ref_field)

    def assertTypeIsComposeOfFields(self, type_name, field_names, input_type=False):
        fields_key = "inputFields" if input_type else "fields"
        gql_type = self.get_type(type_name)
        self.assertEqual(len(field_names),len(gql_type[fields_key]))
        for field in gql_type[fields_key]:
            self.assertIn(field["name"], field_names)



