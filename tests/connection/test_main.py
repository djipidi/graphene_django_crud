# -*- coding: utf-8 -*-
from graphene_django.utils.testing import GraphQLTestCase
from tests.client import Client
from tests.utils import VerifyResponseAssertionMixins
import json
from .models import *


class ConnectionTest(GraphQLTestCase, VerifyResponseAssertionMixins):

    def setUp(self):
        for i in range(10):
            a = TestConnA()
            a.text = str(i)
            a.nb = i
            a.save()
            for j in range(10):
                b = TestConnB()
                b.text = str(j)
                b.nb = j
                b.test_conn_a = a
                b.save()
                c = TestConnC()
                c.text = str(j)
                c.nb = j
                c.test_conn_a = a
                c.save()

    def test_main(self):
        client = Client()
        query = """
            query{
                testConnAs(limit:2, offset:2){
                count
                nbAvg
                data{
                id
                nb
                text
                testConnBs(first:2, offset:2){
                    totalCount
                    nbAvg
                    edges{
                    node{
                        id
                        nb
                        text
                    }
                    }
                }
                testConnCs(limit:2, offset:2){
                    id
                    nb
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
                "testConnAs": {
                    "count": 10,
                    "nbAvg": 4.5,
                    "data": [
                        {
                            "id": "3",
                            "nb": 2,
                            "text": "2",
                            "testConnBs": {
                                "totalCount": 10,
                                "nbAvg": 4.5,
                                "edges": [
                                    {
                                        "node": {
                                            "id": "VGVzdENvbm5CVHlwZToyMw==",
                                            "nb": 2,
                                            "text": "2"
                                        }
                                    },
                                    {
                                        "node": {
                                            "id": "VGVzdENvbm5CVHlwZToyNA==",
                                            "nb": 3,
                                            "text": "3"
                                        }
                                    }
                                ]
                            },
                            "testConnCs": [
                                {
                                    "id": "23",
                                    "nb": 2,
                                    "text": "2"
                                },
                                {
                                    "id": "24",
                                    "nb": 3,
                                    "text": "3"
                                }
                            ]
                        },
                        {
                            "id": "4",
                            "nb": 3,
                            "text": "3",
                            "testConnBs": {
                                "totalCount": 10,
                                "nbAvg": 4.5,
                                "edges": [
                                    {
                                        "node": {
                                            "id": "VGVzdENvbm5CVHlwZTozMw==",
                                            "nb": 2,
                                            "text": "2"
                                        }
                                    },
                                    {
                                        "node": {
                                            "id": "VGVzdENvbm5CVHlwZTozNA==",
                                            "nb": 3,
                                            "text": "3"
                                        }
                                    }
                                ]
                            },
                            "testConnCs": [
                                {
                                    "id": "33",
                                    "nb": 2,
                                    "text": "2"
                                },
                                {
                                    "id": "34",
                                    "nb": 3,
                                    "text": "3"
                                }
                            ]
                        }
                    ]
                }
            }
        }
        """
        )
        response = client.query(query).json()
        self.verify_response(response, expected_response)
