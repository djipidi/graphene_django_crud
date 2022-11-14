# -*- coding: utf-8 -*-
from tests.client import Client
from graphene_django.utils.testing import GraphQLTestCase
from tests.utils import VerifyResponseAssertionMixins
from .models import TestFkA, TestFkB, TestFkC

testFkA_Fragment = """
fragment testFkA on TestFkAType {
  id
  text
  testFkB{
    id
    text
    testFkC{
      id
      text
    }
  }
}
"""
testFkACreate_gql = (
    testFkA_Fragment
    + """
mutation testFkACreate($input: TestFkACreateInput!) {
    testFkACreate(input: $input) {
        ok
        result {
            ...testFkA
        }
    }
}
"""
)
testFkAUpdate_gql = (
    testFkA_Fragment
    + """
mutation testFkAUpdate($input: TestFkAUpdateInput!, $where: TestFkAWhereInput!) {
  testFkAUpdate(input: $input, where: $where) {
    ok
    result {
      ...testFkA
    }
  }
}
"""
)

testFkB_Fragment = """
fragment testFkB on TestFkBType {
  id
  text
  testFkAs{
    count
    data {
      id
      text
    }
  }
  testFkC{
    id
    text
  }
}
"""
testFkBCreate_gql = (
    testFkB_Fragment
    + """
mutation testFkBCreate($input: TestFkBCreateInput!) {
    testFkBCreate(input: $input) {
        ok
        result {
            ...testFkB
        }
    }
}
"""
)

testFkBUpdate_gql = (
    testFkB_Fragment
    + """
mutation testFkBUpdate($input: TestFkBUpdateInput!, $where: TestFkBWhereInput!) {
  testFkBUpdate(input: $input, where: $where) {
    ok
    result {
      ...testFkB
    }
  }
}
"""
)

testFkC_Fragment = """
fragment testFkC on TestFkCType {
  id
  text
  testfkbSet {
    count
    data {
      id
      text
      testFkAs {
        count
        data {
          id
          text
        }
      }
    }
  }
}
"""
testFkCCreate_gql = (
    testFkC_Fragment
    + """
mutation testFkCCreate($input: TestFkCCreateInput!) {
    testFkCCreate(input: $input) {
        ok
        result {
            ...testFkC
        }
    }
}
"""
)

testFkCUpdate_gql = (
    testFkC_Fragment
    + """
mutation testFkCUpdate($input: TestFkCUpdateInput!, $where: TestFkCWhereInput!) {
  testFkCUpdate(input: $input, where: $where) {
    ok
    result {
      ...testFkC
    }
  }
}
"""
)


class RelationShipForeignKeyTest(GraphQLTestCase, VerifyResponseAssertionMixins):
    def setUp(self):
        self.c1 = TestFkC.objects.create(text="c1")
        self.b1 = TestFkB.objects.create(text="b1", test_fk_c=self.c1)
        self.a1 = TestFkA.objects.create(text="a1", test_fk_b=self.b1)

    def test_create_1(self):
        client = Client()

        variables = {
            "input": {
                "text": "a2",
                "testFkB": {
                    "create": {"text": "b2", "testFkC": {"create": {"text": "c2"}}}
                },
            }
        }
        expected_response = {
            "data": {
                "testFkACreate": {
                    "ok": True,
                    "result": {
                        "text": "a2",
                        "testFkB": {"text": "b2", "testFkC": {"text": "c2"}},
                    },
                }
            }
        }
        response = client.query(testFkACreate_gql, variables=variables).json()
        self.verify_response(response, expected_response)

    def test_create_2(self):
        client = Client()

        variables = {
            "input": {
                "text": "a2",
                "testFkB": {"connect": {"id": {"exact": self.b1.pk}}},
            }
        }
        expected_response = {
            "data": {
                "testFkACreate": {
                    "ok": True,
                    "result": {
                        "text": "a2",
                        "testFkB": {
                            "id": str(self.b1.pk),
                            "text": "b1",
                            "testFkC": {"text": "c1"},
                        },
                    },
                }
            }
        }

        response = client.query(testFkACreate_gql, variables=variables).json()
        self.verify_response(response, expected_response)

    def test_create_3(self):
        client = Client()
        variables = {
            "input": {
                "text": "b2",
                "testFkC": {"create": {"text": "c2"}},
                "testFkAs": {
                    "connect": [{"id": {"exact": self.a1.pk}}],
                    "create": [{"text": "a2"}, {"text": "a3"}],
                },
            }
        }
        expected_response = {
            "data": {
                "testFkBCreate": {
                    "ok": True,
                    "result": {
                        "id": "2",
                        "text": "b2",
                        "testFkAs": {
                            "count": 3,
                            "data": [
                                {"id": str(self.a1.pk), "text": "a1"},
                                {"text": "a2"},
                                {"text": "a3"},
                            ],
                        },
                        "testFkC": {"text": "c2"},
                    },
                }
            }
        }

        response = client.query(testFkBCreate_gql, variables=variables).json()
        self.verify_response(response, expected_response)

    def test_create_4(self):
        client = Client()

        variables = {
            "input": {
                "text": "b3",
                "testFkC": {"connect": {"id": {"exact": self.c1.pk}}},
            }
        }
        expected_response = {
            "data": {
                "testFkBCreate": {
                    "ok": True,
                    "result": {
                        "text": "b3",
                        "testFkAs": {"count": 0, "data": []},
                        "testFkC": {"id": str(self.c1.pk), "text": "c1"},
                    },
                }
            }
        }
        response = client.query(testFkBCreate_gql, variables=variables).json()
        self.verify_response(response, expected_response)

    def test_create_5(self):
        client = Client()

        variables = {
            "input": {
                "text": "c3",
                "testfkbSet": {
                    "connect": [{"id": {"exact": self.b1.pk}}],
                    "create": [
                        {
                            "text": "b4",
                            "testFkAs": {
                                "connect": [
                                    {"id": {"exact": self.a1.pk}},
                                ],
                                "create": [
                                    {"text": "a5"},
                                    {"text": "a6"},
                                ],
                            },
                        }
                    ],
                },
            }
        }
        expected_response = {
            "data": {
                "testFkCCreate": {
                    "ok": True,
                    "result": {
                        "text": "c3",
                        "testfkbSet": {
                            "count": 2,
                            "data": [
                                {
                                    "id": str(self.b1.pk),
                                    "text": "b1",
                                    "testFkAs": {"count": 0, "data": []},
                                },
                                {
                                    "text": "b4",
                                    "testFkAs": {
                                        "count": 3,
                                        "data": [
                                            {"id": str(self.a1.pk), "text": "a1"},
                                            {"text": "a5"},
                                            {"text": "a6"},
                                        ],
                                    },
                                },
                            ],
                        },
                    },
                }
            }
        }

        response = client.query(testFkCCreate_gql, variables=variables).json()
        self.verify_response(response, expected_response)

    def test_update_1(self):
        client = Client()

        variables = {
            "input": {
                "text": "b1-bis",
                "testFkAs": {
                    "create": [
                        {"text": "a2"},
                        {"text": "a3"},
                    ],
                    "update": [
                        {
                            "where": {"id": {"exact": self.a1.pk}},
                            "input": {"text": "a1-bis"},
                        }
                    ],
                },
                "testFkC": {"disconnect": True},
            },
            "where": {"id": {"exact": self.b1.pk}},
        }
        expected_response = {
            "data": {
                "testFkBUpdate": {
                    "ok": True,
                    "result": {
                        "id": str(self.b1.pk),
                        "text": "b1-bis",
                        "testFkAs": {
                            "count": 3,
                            "data": [
                                {"id": "1", "text": "a1-bis"},
                                {"id": "2", "text": "a2"},
                                {"id": "3", "text": "a3"},
                            ],
                        },
                        "testFkC": None,
                    },
                }
            }
        }
        response = client.query(testFkBUpdate_gql, variables=variables).json()
        self.verify_response(response, expected_response)
        self.assertTrue(TestFkC.objects.filter(pk=self.c1.pk).exists())

    def test_update_2(self):
        client = Client()
        variables = {
            "input": {
                "text": "b1-bis",
                "testFkC": {"delete": True},
            },
            "where": {"id": {"exact": self.b1.pk}},
        }
        expected_response = {
            "data": {
                "testFkBUpdate": {
                    "ok": True,
                    "result": {
                        "id": str(self.b1.pk),
                        "text": "b1-bis",
                        "testFkAs": {
                            "count": 1,
                            "data": [
                                {"id": str(self.a1.pk), "text": "a1"},
                            ],
                        },
                        "testFkC": None,
                    },
                }
            }
        }
        response = client.query(testFkBUpdate_gql, variables=variables).json()
        self.verify_response(response, expected_response)
        self.assertFalse(TestFkC.objects.filter(pk=self.c1.pk).exists())

    def test_update_3(self):
        client = Client()

        variables = {
            "input": {
                "text": "c1-bis",
                "testfkbSet": {
                    "disconnect": [{"id": {"exact": self.b1.pk}}]
                },
            },
            "where": {"id": {"exact": self.c1.pk}},
        }
        expected_response = {
            "data": {
                "testFkCUpdate": {
                    "ok": True,
                    "result": {
                        "id": str(self.c1.pk),
                        "text": "c1-bis",
                        "testfkbSet": {
                            "count": 0,
                            "data": []
                        }
                    }
                }
            }
        }
        response = client.query(testFkCUpdate_gql, variables=variables).json()
        self.verify_response(response, expected_response)
        self.assertTrue(TestFkB.objects.filter(pk=self.b1.pk).exists())

    def test_update_4(self):
        client = Client()

        variables = {
            "input": {
                "text": "c1-bis",
                "testfkbSet": {
                    "delete": [{"id": {"exact": self.b1.pk}}]
                },
            },
            "where": {"id": {"exact": self.c1.pk}},
        }
        expected_response = {
            "data": {
                "testFkCUpdate": {
                    "ok": True,
                    "result": {
                        "id": str(self.c1.pk),
                        "text": "c1-bis",
                        "testfkbSet": {
                            "count": 0,
                            "data": []
                        }
                    }
                }
            }
        }
        response = client.query(testFkCUpdate_gql, variables=variables).json()
        self.verify_response(response, expected_response)
        self.assertFalse(TestFkB.objects.filter(pk=self.b1.pk).exists())