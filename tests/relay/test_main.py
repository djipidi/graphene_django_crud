# -*- coding: utf-8 -*-
from tests.client import Client
from graphene_django.utils.testing import GraphQLTestCase
from tests.utils import VerifyResponseAssertionMixins
import json
from .models import TestRelayA, TestRelayB


class RelayTest(GraphQLTestCase, VerifyResponseAssertionMixins):

    def test_main(self):

        client = Client()

        for i in range(10):
            b = TestRelayB(text=str(i))
            b.save()
            for j in range(10):
                TestRelayA(text=str(i) + "-" + str(j), test_relay_b=b).save()

        query = """
        {
            testRelayBs(offset: 5, first: 1) {
                pageInfo {
                hasNextPage
                hasPreviousPage
                startCursor
                endCursor
                }
                edges {
                cursor
                node {
                    id
                    text
                    testRelayAs(offset: 5, first: 1) {
                    pageInfo {
                        hasNextPage
                        hasPreviousPage
                        startCursor
                        endCursor
                    }
                    edges {
                        cursor
                        node {
                        id
                        text
                        }
                    }
                    }
                }
                }
            }
        }
        """

        expected_response = json.loads(
            """
                {
                    "data": {
                        "testRelayBs": {
                            "pageInfo": {
                                "hasNextPage": true,
                                "hasPreviousPage": false,
                                "startCursor": "YXJyYXljb25uZWN0aW9uOjU=",
                                "endCursor": "YXJyYXljb25uZWN0aW9uOjU="
                            },
                            "edges": [
                                {
                                    "cursor": "YXJyYXljb25uZWN0aW9uOjU=",
                                    "node": {
                                        "id": "VGVzdFJlbGF5QlR5cGU6Ng==",
                                        "text": "5",
                                        "testRelayAs": {
                                            "pageInfo": {
                                                "hasNextPage": true,
                                                "hasPreviousPage": false,
                                                "startCursor": "YXJyYXljb25uZWN0aW9uOjU=",
                                                "endCursor": "YXJyYXljb25uZWN0aW9uOjU="
                                            },
                                            "edges": [
                                                {
                                                    "cursor": "YXJyYXljb25uZWN0aW9uOjU=",
                                                    "node": {
                                                        "id": "VGVzdFJlbGF5QVR5cGU6NTY=",
                                                        "text": "5-5"
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            """
        )

        response = client.query(query).json()
        self.verify_response(response, expected_response)

        b5_id = response["data"]["testRelayBs"]["edges"][0]["node"]["id"]
        a5_5_id = response["data"]["testRelayBs"]["edges"][0]["node"]["testRelayAs"][
            "edges"
        ][0]["node"]["id"]

        query = """
            query node ($id: ID!){
                node(id:$id){
                    ... on TestRelayAType{
                    id
                    text
                    testRelayB{
                        id
                        text
                    }
                    }
                }
            } 
        """
        expected_response = json.loads(
            """
            {
                "data": {
                    "node": {
                        "id": "VGVzdFJlbGF5QVR5cGU6NTY=",
                        "text": "5-5",
                        "testRelayB": {
                            "id": "VGVzdFJlbGF5QlR5cGU6Ng==",
                            "text": "5"
                        }
                    }
                }
            }
        """
        )
        response = client.query(query, variables={"id": a5_5_id}).json()
        self.verify_response(response, expected_response)

        query = """
            mutation testRelayACreate($input: TestRelayACreateInput!){
                testRelayACreate(input:$input){
                    ok
                    result{
                    id
                    text
                    testRelayB{
                        id
                        text
                    }
                    }
                }
            }
        """
        variables = {"input": {"text": "11", "testRelayB": {"create": {"text": "11"}}}}

        expected_response = json.loads(
            """
        {
            "data": {
                "testRelayACreate": {
                    "ok": true,
                    "result": {
                        "id": "VGVzdFJlbGF5QVR5cGU6MTAx",
                        "text": "11",
                        "testRelayB": {
                            "id": "VGVzdFJlbGF5QlR5cGU6MTE=",
                            "text": "11"
                        }
                    }
                }
            }
        }
        """
        )
        response = client.query(query, variables=variables).json()
        self.verify_response(response, expected_response)
        a_11_id = response["data"]["testRelayACreate"]["result"]["id"]
        b_11_id = response["data"]["testRelayACreate"]["result"]["testRelayB"]["id"]
        query = """
            mutation testRelayAUpdate($input: TestRelayAUpdateInput!, $where: TestRelayAWhereInput!){
            testRelayAUpdate(input:$input, where:$where){
                ok
                result{
                id
                text
                testRelayB{
                    id
                    text
                }
                }
            }
            }
        """

        variables = {
            "where": {"id": {"exact": a_11_id}},
            "input": {
                "text": "11-bis",
            },
        }

        expected_response = json.loads(
            """
        {
            "data": {
                "testRelayAUpdate": {
                    "ok": true,
                    "result": {
                        "id": "VGVzdFJlbGF5QVR5cGU6MTAx",
                        "text": "11-bis",
                        "testRelayB": {
                            "id": "VGVzdFJlbGF5QlR5cGU6MTE=",
                            "text": "11"
                        }
                    }
                }
            }
        }

        """
        )
        response = client.query(query, variables=variables).json()
        self.verify_response(response, expected_response)
