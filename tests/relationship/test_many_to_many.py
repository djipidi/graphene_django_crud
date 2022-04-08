# -*- coding: utf-8 -*-
from tests.client import Client
from graphene_django.utils.testing import GraphQLTestCase
from tests.utils import VerifyResponseAssertionMixins
from .models import TestM2mA, TestM2mB, TestM2mC

testM2mA_Fragment = """
fragment testM2mA on TestM2mAType {
  id
  text
  testM2mBs {
    count
    data {
      id
      text
      testM2mCs {
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
testM2mACreate_gql = (
    testM2mA_Fragment
    + """
mutation testM2mACreate($input: TestM2mACreateInput!) {
  testM2mACreate(input: $input) {
    ok
    result {
      ...testM2mA
    }
  }
}
"""
)

testM2mAUpdate_gql = (
    testM2mA_Fragment
    + """
mutation testM2mACreate($input: TestM2mAUpdateInput!, $where: TestM2mAWhereInput!) {
  testM2mAUpdate(input: $input, where: $where) {
    ok
    result {
      ...testM2mA
    }
  }
}
"""
)

testM2mC_Fragment = """
fragment testM2mC on TestM2mCType {
  id
  text
  testm2mbSet {
    count
    data {
      id
      text
      testM2mAs {
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
testM2mCCreate_gql = (
    testM2mC_Fragment
    + """
mutation testM2mCCreate($input: TestM2mCCreateInput!) {
  testM2mCCreate(input: $input) {
    ok
    result {
      ...testM2mC
    }
  }
}
"""
)

testM2mCUpdate_gql = (
    testM2mA_Fragment
    + """
mutation testM2mCCreate($input: TestM2mCCreateInput!, $where TestM2mCWhereInput!) {
  testM2mACreate(input: $input, where: $where) {
    ok
    result {
      ...testM2mC
    }
  }
}
"""
)

class RelationShipManyToManyTest(GraphQLTestCase, VerifyResponseAssertionMixins):
    def setUp(self):
        self.c1 = TestM2mC.objects.create(text="c1")
        self.b1 = TestM2mB.objects.create(text="b1")
        self.a1 = TestM2mA.objects.create(text="a1")
        self.a1.test_m2m_bs.add(self.b1)
        self.b1.test_m2m_cs.add(self.c1)

    def test_create_1(self):
        client = Client()

        variables = {
            "input": {
                "text": "a2",
                "testM2mBs": {
                    "create": [
                        {
                            "text": "b2",
                            "testM2mCs": {"create": [{"text": "b2-c1"}, {"text": "b2-c2"}]},
                        },
                        {
                            "text": "b3",
                            "testM2mCs": {"create": [{"text": "b3-c1"}, {"text": "b3-c2"}]},
                        },
                    ]
                },
            }
        }
        expected_response = {
            "data": {
                "testM2mACreate": {
                    "ok": True,
                    "result": {
                        "text": "a2",
                        "testM2mBs": {
                            "count": 2,
                            "data": [
                                {
                                    "text": "b2",
                                    "testM2mCs": {
                                        "count": 2,
                                        "data": [{"text": "b2-c1"}, {"text": "b2-c2"}],
                                    },
                                },
                                {
                                    "text": "b3",
                                    "testM2mCs": {
                                        "count": 2,
                                        "data": [{"text": "b3-c1"}, {"text": "b3-c2"}],
                                    },
                                },
                            ],
                        },
                    },
                }
            }
        }

        response = client.query(testM2mACreate_gql, variables=variables).json()
        self.verify_response(response, expected_response)

    def test_create_2(self):
        client = Client()

        variables = {
            "input": {
                "text": "a2",
                "testM2mBs": {
                    "connect": [
                        {"id": {"exact": self.b1.pk}},
                    ],
                    "create": [
                        {
                            "text": "b2",
                            "testM2mCs": {
                                "connect": [
                                    {"id": {"exact": self.c1.pk}},
                                ]
                            },
                        }
                    ],
                },
            }
        }

        expected_response = {
            "data": {
                "testM2mACreate": {
                    "ok": True,
                    "result": {
                        "text": "a2",
                        "testM2mBs": {
                            "count": 2,
                            "data": [
                                {
                                    "id": str(self.b1.pk),
                                    "text": "b1",
                                    "testM2mCs": {
                                        "count": 1,
                                        "data": [
                                            {
                                                "id": str(self.c1.pk),
                                                "text": "c1"
                                            }
                                        ]
                                    }
                                },
                                {
                                    "text": "b2",
                                    "testM2mCs": {
                                        "count": 1,
                                        "data": [
                                            {
                                                "id": str(self.c1.pk),
                                                "text": "c1"
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
        response = client.query(testM2mACreate_gql, variables=variables).json()
        self.verify_response(response, expected_response)

    def test_create_3(self):
        client = Client()
        variables = {
            "input": {
                "text": "c2",
                "testm2mbSet": {
                    "create": [
                        {
                            "text": "b2",
                            "testM2mAs": {
                                "create": [{"text": "a2"}],
                                "connect": [{"id": {"exact": self.a1.pk}}],
                            },
                        }
                    ],
                    "connect": [{"id": {"exact": self.b1.pk}}],
                },
            }
        }
        expected_response = {
            "data": {
                "testM2mCCreate": {
                    "ok": True,
                    "result": {
                        "text": "c2",
                        "testm2mbSet": {
                            "count": 2,
                            "data": [
                                {
                                    "id": str(self.b1.pk),
                                    "text": "b1",
                                    "testM2mAs": {
                                        "count": 1,
                                        "data": [
                                            {
                                                "id": str(self.a1.pk),
                                                "text": "a1"
                                            }
                                        ]
                                    }
                                },
                                {
                                    "text": "b2",
                                    "testM2mAs": {
                                        "count": 2,
                                        "data": [
                                            {
                                                "id": str(self.a1.pk),
                                                "text": "a1"
                                            },
                                            {
                                                "text": "a2"
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
        response = client.query(testM2mCCreate_gql, variables=variables).json()
        self.verify_response(response, expected_response)

    def test_update_1(self):
        client = Client()
        variables = {
            "input": {
                "text": "a1-bis",
                "testM2mBs" : {
                    "update": [
                        {
                            "input" : {
                                "text":"b1-bis",
                                "testM2mCs": {
                                    "update": [
                                        {
                                            "input":{"text": "c1-bis"},
                                            "where": {"id":{"exact":self.c1.pk}}
                                        }
                                    ]
                                }
                            },
                            "where": {"id":{"exact":self.b1.pk}}
                        }
                    ]
                }
            },
            "where":{"id":{"exact":self.a1.pk}}
        }
        expected_response = {
            "data": {
                "testM2mAUpdate": {
                    "ok": True,
                    "result": {
                        "id": str(self.a1.pk),
                        "text": "a1-bis",
                        "testM2mBs": {
                            "count": 1,
                            "data": [
                                {
                                    "id": str(self.b1.pk),
                                    "text": "b1-bis",
                                    "testM2mCs": {
                                        "count": 1,
                                        "data": [
                                            {
                                                "id": str(self.c1.pk),
                                                "text": "c1-bis"
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
        response = client.query(testM2mAUpdate_gql, variables=variables).json()
        self.verify_response(response, expected_response)