# -*- coding: utf-8 -*-
from tests.client import Client
from graphene_django.utils.testing import GraphQLTestCase
from tests.utils import VerifyResponseAssertionMixins
from .models import TestO2oA, TestO2oB, TestO2oC

testO2oA_Fragment = """
fragment testO2oA on TestO2oAType {
id
text
testO2oB {
    id
    text
    testO2oC {
    id
    text
    }
}
}
"""
testO2oACreate_gql = (
    testO2oA_Fragment
    + """
mutation testO2oACreate($input: TestO2oACreateInput!) {
    testO2oACreate(input: $input) {
        ok
        result {
            ...testO2oA
        }
    }
}
"""
)

testO2oAUpdate_gql = (
    testO2oA_Fragment
    + """
mutation testO2oAUpdate($input: TestO2oAUpdateInput!, $where: TestO2oAWhereInput!) {
    testO2oAUpdate(input: $input, where: $where) {
        ok
        result {
            ...testO2oA
        }
    }
}
"""
)


testO2oB_Fragment = """
fragment testO2oB on TestO2oBType {
id
text
testO2oA {
    id
    text
}
testO2oC {
    id
    text
}
}
"""
testO2oBCreate_gql = (
    testO2oB_Fragment
    + """
mutation testO2oBCreate($input: TestO2oBCreateInput!) {
    testO2oBCreate(input: $input) {
        ok
        result {
            ...testO2oB
        }
    }
}
"""
)

testO2oBUpdate_gql = (
    testO2oB_Fragment
    + """
mutation testO2oBUpdate($input: TestO2oBUpdateInput!, $where: TestO2oBWhereInput!) {
    testO2oBUpdate(input: $input, where: $where) {
        ok
        result {
            ...testO2oB
        }
    }
}
"""
)

testO2oC_Fragment = """
fragment testO2oC on TestO2oCType {
id
text
testo2ob {
    id
    text
    testO2oA {
    id
    text
    }
}
}
"""
testO2oCCreate_gql = (
    testO2oC_Fragment
    + """
mutation testO2oCCreate($input: TestO2oCCreateInput!) {
    testO2oCCreate(input: $input) {
        ok
        result {
            ...testO2oC
        }
    }
}
"""
)

testO2oCUpdate_gql = (
    testO2oC_Fragment
    + """
mutation testO2oCUpdate($input: TestO2oCUpdateInput!, $where: TestO2oCWhereInput!) {
    testO2oCUpdate(input: $input, where: $where) {
        ok
        result {
            ...testO2oC
        }
    }
}
"""
)


class RelationShipOneToOneTest(GraphQLTestCase, VerifyResponseAssertionMixins):
    def setUp(self):
        self.c1 = TestO2oC.objects.create(text="c1")
        self.b1 = TestO2oB.objects.create(text="b1", test_o2o_c=self.c1)
        self.a1 = TestO2oA.objects.create(text="a1", test_o2o_b=self.b1)

    def test_create_1(self):
        client = Client()

        variables = {
            "input": {
                "text": "a2",
                "testO2oB": {
                    "create": {"text": "b2", "testO2oC": {"create": {"text": "c2"}}}
                },
            }
        }
        expected_response = {
            "data": {
                "testO2oACreate": {
                    "ok": True,
                    "result": {
                        "text": "a2",
                        "testO2oB": {"text": "b2", "testO2oC": {"text": "c2"}},
                    },
                }
            }
        }

        response = client.query(testO2oACreate_gql, variables=variables).json()
        self.verify_response(response, expected_response)

    def test_create_2(self):
        client = Client()

        variables = {
            "input": {
                "text": "b2",
                "testO2oA": {"create": {"text": "a2"}},
                "testO2oC": {"create": {"text": "c2"}},
            }
        }
        expected_response = {
            "data": {
                "testO2oBCreate": {
                    "ok": True,
                    "result": {
                        "text": "b2",
                        "testO2oA": {"text": "a2"},
                        "testO2oC": {"text": "c2"},
                    },
                }
            }
        }

        response = client.query(testO2oBCreate_gql, variables=variables).json()
        self.verify_response(response, expected_response)

    def test_create_3(self):
        client = Client()

        variables = {
            "input": {
                "text": "c3",
                "testo2ob": {
                    "create": {
                        "text": "b3",
                        "testO2oA": {"connect": {"id": {"exact": self.a1.pk}}},
                    }
                },
            }
        }
        expected_response = {
            "data": {
                "testO2oCCreate": {
                    "ok": True,
                    "result": {
                        "text": "c3",
                        "testo2ob": {
                            "text": "b3",
                            "testO2oA": {"id": str(self.a1.pk), "text": "a1"},
                        },
                    },
                }
            }
        }

        response = client.query(testO2oCCreate_gql, variables=variables).json()
        self.verify_response(response, expected_response)

    def test_update_1(self):
        client = Client()

        variables = {
            "where": {"id": {"exact": self.b1.pk}},
            "input": {
                "text": "b1-bis",
                "testO2oC": {"disconnect": True},
            },
        }
        expected_response = {
            "data": {
                "testO2oBUpdate": {
                    "ok": True,
                    "result": {
                        "id": str(self.b1.pk),
                        "text": "b1-bis",
                        "testO2oC": None,
                    },
                }
            }
        }

        response = client.query(testO2oBUpdate_gql, variables=variables).json()
        self.verify_response(response, expected_response)
        self.assertTrue(TestO2oB.objects.filter(pk=self.b1.pk).exists())

    def test_update_2(self):
        client = Client()
        variables = {
            "where": {"id": {"exact": self.b1.pk}},
            "input": {
                "text": "b1-bis",
                "testO2oC": {"delete": True},
                "testO2oA": {"update": {"text": "a1-bis"}},
            },
        }
        expected_response = {
            "data": {
                "testO2oBUpdate": {
                    "ok": True,
                    "result": {
                        "id": str(self.b1.pk),
                        "text": "b1-bis",
                        "testO2oA": {"id": str(self.a1.pk), "text": "a1-bis"},
                        "testO2oC": None,
                    },
                }
            }
        }

        response = client.query(testO2oBUpdate_gql, variables=variables).json()

        self.verify_response(response, expected_response)
        self.assertFalse(TestO2oC.objects.filter(pk=self.c1.pk).exists())

    def test_update_3(self):
        client = Client()
        variables = {
            "where": {"id": {"exact": self.b1.pk}},
            "input": {
                "text": "b1-bis",
                "testo2ob": {"delete": True},
            },
        }
        expected_response = {
            "data": {
                "testO2oCUpdate": {
                    "ok": True,
                    "result": {
                        "id": "1",
                        "text": "b1-bis",
                        "testo2ob": None
                    }
                }
            }
        }
        response = client.query(testO2oCUpdate_gql, variables=variables).json()
        self.verify_response(response, expected_response)
        self.assertFalse(TestO2oB.objects.filter(pk=self.b1.pk).exists())

    def test_update_4(self):
        client = Client()
        variables = {
            "where": {"id": {"exact": self.b1.pk}},
            "input": {
                "text": "b1-bis",
                "testo2ob": {"disconnect": True},
            },
        }
        expected_response = {
            "data": {
                "testO2oCUpdate": {
                    "ok": True,
                    "result": {
                        "id": "1",
                        "text": "b1-bis",
                        "testo2ob": None
                    }
                }
            }
        }
        response = client.query(testO2oCUpdate_gql, variables=variables).json()
        self.verify_response(response, expected_response)

    def test_update_5(self):
        client = Client()
        variables = {
            "where": {"id": {"exact": self.a1.pk}},
            "input": {
                "text": "a1-bis",
                "testO2oB": {
                    "update": {
                        "text": "b1-bis",
                        "testO2oC": {
                            "update": {
                                "text": "c1-bis"
                            }
                        }
                    }
                },
            },
        }
        expected_response = {
            "data": {
                "testO2oAUpdate": {
                    "ok": True,
                    "result": {
                        "id": str(self.a1.pk),
                        "text": "a1-bis",
                        "testO2oB": {
                            "id": str(self.b1.pk),
                            "text": "b1-bis",
                            "testO2oC": {
                                "id": str(self.c1.pk),
                                "text": "c1-bis"
                            }
                        }
                    }
                }
            }
        }
        response = client.query(testO2oAUpdate_gql, variables=variables).json()
        self.verify_response(response, expected_response)
