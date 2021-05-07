# -*- coding: utf-8 -*-
import pytest
from tests.client import Client
from tests.utils import verify_response
import json


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


def test_foreignkey():
    client = Client()

    variables = {
        "input": {
            "text": "a1",
            "testFkB": {
                "create": {"text": "b1", "testFkC": {"create": {"text": "c1"}}}
            },
        }
    }
    expected_response = {
        "data": {
            "testFkACreate": {
                "ok": True,
                "result": {
                    "text": "a1",
                    "testFkB": {"text": "b1", "testFkC": {"text": "c1"}},
                },
            }
        }
    }
    response = client.query(testFkACreate_gql, variables=variables).json()
    verify_response(expected_response, response)

    a1_id = response["data"]["testFkACreate"]["result"]["id"]
    b1_id = response["data"]["testFkACreate"]["result"]["testFkB"]["id"]
    c1_id = response["data"]["testFkACreate"]["result"]["testFkB"]["testFkC"]["id"]

    variables = {
        "input": {"text": "a2", "testFkB": {"connect": {"id": {"equals": b1_id}}}}
    }
    expected_response = {
        "data": {
            "testFkACreate": {
                "ok": True,
                "result": {
                    "id": "2",
                    "text": "a2",
                    "testFkB": {"id": b1_id, "text": "b1", "testFkC": {"text": "c1"}},
                },
            }
        }
    }

    response = client.query(testFkACreate_gql, variables=variables).json()
    verify_response(expected_response, response)
    a2_id = response["data"]["testFkACreate"]["result"]["id"]

    variables = {
        "input": {
            "text": "b2",
            "testFkC": {"create": {"text": "c2"}},
            "testFkAs": {
                "connect": [{"id": {"equals": a1_id}}],
                "create": [{"text": "a3"}, {"text": "a4"}],
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
                            {"id": a1_id, "text": "a1"},
                            {"text": "a3"},
                            {"text": "a4"},
                        ],
                    },
                    "testFkC": {"text": "c2"},
                },
            }
        }
    }

    response = client.query(testFkBCreate_gql, variables=variables).json()
    verify_response(expected_response, response)
    b2_id = response["data"]["testFkBCreate"]["result"]["id"]
    c2_id = response["data"]["testFkBCreate"]["result"]["testFkC"]["id"]
    a3_id = response["data"]["testFkBCreate"]["result"]["testFkAs"]["data"][1]["id"]
    a4_id = response["data"]["testFkBCreate"]["result"]["testFkAs"]["data"][2]["id"]

    variables = {
        "input": {
            "text": "b3",
            "testFkC": {"connect": {"id": {"equals": c1_id}}},
        }
    }
    expected_response = {
        "data": {
            "testFkBCreate": {
                "ok": True,
                "result": {
                    "text": "b3",
                    "testFkAs": {"count": 0, "data": []},
                    "testFkC": {"id": c1_id, "text": "c1"},
                },
            }
        }
    }
    response = client.query(testFkBCreate_gql, variables=variables).json()
    verify_response(expected_response, response)
    b3_id = response["data"]["testFkBCreate"]["result"]["id"]

    variables = {
        "input": {
            "text": "c3",
            "testfkbSet": {
                "connect": [{"id": {"equals": b1_id}}],
                "create": [
                    {
                        "text": "b4",
                        "testFkAs": {
                            "connect": [
                                {"id": {"equals": a1_id}},
                                {"id": {"equals": a2_id}},
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
                                "id": b1_id,
                                "text": "b1",
                                "testFkAs": {"count": 0, "data": []},
                            },
                            {
                                "text": "b4",
                                "testFkAs": {
                                    "count": 4,
                                    "data": [
                                        {"id": a1_id, "text": "a1"},
                                        {"id": a2_id, "text": "a2"},
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
    verify_response(expected_response, response)

    c3_id = response["data"]["testFkCCreate"]["result"]["id"]
    b4_id = response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][1]["id"]
    a5_id = response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][1][
        "testFkAs"
    ]["data"][2]["id"]
    a6_id = response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][1][
        "testFkAs"
    ]["data"][3]["id"]


testO2oA_Fragment = """
fragment testO2oA on TestO2oAType {
  id
  text
  TestO2oB {
    id
    text
    TestO2oC {
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


testO2oB_Fragment = """
fragment testO2oB on TestO2oBType {
  id
  text
  testO2oA {
    id
    text
  }
  TestO2oC {
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


def test_onetoone():
    client = Client()

    variables = {
        "input": {
            "text": "a1",
            "TestO2oB": {
                "create": {"text": "b1", "TestO2oC": {"create": {"text": "c1"}}}
            },
        }
    }
    expected_response = {
        "data": {
            "testO2oACreate": {
                "ok": True,
                "result": {
                    "text": "a1",
                    "TestO2oB": {"text": "b1", "TestO2oC": {"text": "c1"}},
                },
            }
        }
    }

    response = client.query(testO2oACreate_gql, variables=variables).json()
    verify_response(expected_response, response)
    a1_id = response["data"]["testO2oACreate"]["result"]["id"]
    b1_id = response["data"]["testO2oACreate"]["result"]["TestO2oB"]["id"]
    c1_id = response["data"]["testO2oACreate"]["result"]["TestO2oB"]["TestO2oC"]["id"]

    variables = {
        "input": {
            "text": "b2",
            "testO2oA": {"create": {"text": "a2"}},
            "TestO2oC": {"create": {"text": "c2"}},
        }
    }
    expected_response = {
        "data": {
            "testO2oBCreate": {
                "ok": True,
                "result": {
                    "text": "b2",
                    "testO2oA": {"text": "a2"},
                    "TestO2oC": {"text": "c2"},
                },
            }
        }
    }

    response = client.query(testO2oBCreate_gql, variables=variables).json()
    verify_response(expected_response, response)

    b2_id = response["data"]["testO2oBCreate"]["result"]["id"]
    a2_id = response["data"]["testO2oBCreate"]["result"]["testO2oA"]["id"]
    c2_id = response["data"]["testO2oBCreate"]["result"]["TestO2oC"]["id"]

    variables = {
        "input": {
            "text": "c3",
            "testo2ob": {
                "create": {
                    "text": "b3",
                    "testO2oA": {"connect": {"id": {"equals": a1_id}}},
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
                    "testo2ob": {"text": "b3", "testO2oA": {"id": a1_id, "text": "a1"}},
                },
            }
        }
    }

    response = client.query(testO2oCCreate_gql, variables=variables).json()
    verify_response(expected_response, response)

    c3_id = response["data"]["testO2oCCreate"]["result"]["id"]
    b3_id = response["data"]["testO2oCCreate"]["result"]["testo2ob"]["id"]

    variables = {
        "where": {"id": {"equals": b3_id}},
        "input": {
            "text": "b3-bis",
            "TestO2oC": {
                "disconnect": True
            },
        }
    }
    expected_response = {
        "data": {
            "testO2oBUpdate": {
                "ok": True,
                "result": {
                    "id": b3_id,
                    "text": "b3-bis",
                    "TestO2oC": None
                }
            }
        }
    }

    response = client.query(testO2oBUpdate_gql, variables=variables).json()
    verify_response(expected_response, response)

    variables = {
        "where": {"id": {"equals": b2_id}},
        "input": {
            "text": "b2-bis",
            "TestO2oC": {
                "delete": True
            },
        }
    }
    expected_response = {
        "data": {
            "testO2oBUpdate": {
                "ok": True,
                "result": {
                    "id": b2_id,
                    "text": "b2-bis",
                    "TestO2oC": None
                }
            }
        }
    }

    response = client.query(testO2oBUpdate_gql, variables=variables).json()
    verify_response(expected_response, response)

    variables = {
        "where": {"id": {"equals": c1_id}},
        "input": {
            "text": "c1-bis",
            "testo2ob": {
                "disconnect": True
            },
        }
    }
    expected_response = {
        "data": {
            "testO2oCUpdate": {
                "ok": True,
                "result": {
                    "id": c1_id,
                    "text": "c1-bis",
                    "testo2ob": None
                }
            }
        }
    }


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


def test_manytomany():
    client = Client()

    variables = {
        "input": {
            "text": "a1",
            "testM2mBs": {
                "create": [
                    {
                        "text": "b1",
                        "testM2mCs": {"create": [{"text": "c1"}, {"text": "c2"}]},
                    },
                    {
                        "text": "b2",
                        "testM2mCs": {"create": [{"text": "c3"}, {"text": "c4"}]},
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
                    "text": "a1",
                    "testM2mBs": {
                        "count": 2,
                        "data": [
                            {
                                "text": "b1",
                                "testM2mCs": {
                                    "count": 2,
                                    "data": [{"text": "c1"}, {"text": "c2"}],
                                },
                            },
                            {
                                "text": "b2",
                                "testM2mCs": {
                                    "count": 2,
                                    "data": [{"text": "c3"}, {"text": "c4"}],
                                },
                            },
                        ],
                    },
                },
            }
        }
    }

    response = client.query(testM2mACreate_gql, variables=variables).json()
    verify_response(expected_response, response)

    a1_id = response["data"]["testM2mACreate"]["result"]["id"]
    b1_id = response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["id"]
    b2_id = response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["id"]
    c1_id = response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0][
        "testM2mCs"
    ]["data"][0]["id"]
    c2_id = response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0][
        "testM2mCs"
    ]["data"][1]["id"]
    c3_id = response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1][
        "testM2mCs"
    ]["data"][0]["id"]
    c4_id = response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1][
        "testM2mCs"
    ]["data"][1]["id"]

    variables = {
        "input": {
            "text": "a2",
            "testM2mBs": {
                "connect": [
                    {"id": {"equals": b1_id}},
                    {"id": {"equals": b2_id}},
                ],
                "create": [
                    {
                        "text": "b3",
                        "testM2mCs": {
                            "connect": [
                                {"id": {"equals": c1_id}},
                                {"id": {"equals": c2_id}},
                                {"id": {"equals": c3_id}},
                                {"id": {"equals": c4_id}},
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
                        "count": 3,
                        "data": [
                            {
                                "id": b1_id,
                                "text": "b1",
                                "testM2mCs": {
                                    "count": 2,
                                    "data": [
                                        {"id": c1_id, "text": "c1"},
                                        {"id": c2_id, "text": "c2"},
                                    ],
                                },
                            },
                            {
                                "id": b2_id,
                                "text": "b2",
                                "testM2mCs": {
                                    "count": 2,
                                    "data": [
                                        {"id": c3_id, "text": "c3"},
                                        {"id": c4_id, "text": "c4"},
                                    ],
                                },
                            },
                            {
                                "text": "b3",
                                "testM2mCs": {
                                    "count": 4,
                                    "data": [
                                        {"id": c1_id, "text": "c1"},
                                        {"id": c2_id, "text": "c2"},
                                        {"id": c3_id, "text": "c3"},
                                        {"id": c4_id, "text": "c4"},
                                    ],
                                },
                            },
                        ],
                    },
                },
            }
        }
    }
    response = client.query(testM2mACreate_gql, variables=variables).json()
    verify_response(expected_response, response)

    a2_id = response["data"]["testM2mACreate"]["result"]["id"]
    b3_id = response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][2]["id"]

    variables = {
        "input": {
            "text": "c5",
            "testm2mbSet": {
                "create": [
                    {
                        "text": "b4",
                        "testM2mAs": {
                            "create": [{"text": "a3"}],
                            "connect": [{"id": {"equals": a1_id}}],
                        },
                    }
                ],
                "connect": [{"id": {"equals": b1_id}}],
            },
        }
    }
    expected_response = {
        "data": {
            "testM2mCCreate": {
                "ok": True,
                "result": {
                    "text": "c5",
                    "testm2mbSet": {
                        "count": 2,
                        "data": [
                            {
                                "id": b1_id,
                                "text": "b1",
                                "testM2mAs": {
                                    "count": 2,
                                    "data": [
                                        {"id": a1_id, "text": "a1"},
                                        {"id": a2_id, "text": "a2"},
                                    ],
                                },
                            },
                            {
                                "text": "b4",
                                "testM2mAs": {
                                    "count": 2,
                                    "data": [
                                        {"id": a1_id, "text": "a1"},
                                        {"text": "a3"},
                                    ],
                                },
                            },
                        ],
                    },
                },
            }
        }
    }

    response = client.query(testM2mCCreate_gql, variables=variables).json()
    verify_response(expected_response, response)

    c5_id = response["data"]["testM2mCCreate"]["result"]["id"]
    b4_id = response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][1]["id"]
    a3_id = response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][1][
        "testM2mAs"
    ]["data"][1]["id"]
