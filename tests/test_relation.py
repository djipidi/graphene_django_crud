# -*- coding: utf-8 -*-
import pytest
from tests.client import Client


testFkA_Fragment = '''
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
'''
testFkACreate_gql = testFkA_Fragment + '''
mutation testFkACreate($input: TestFkACreateInput!) {
    testFkACreate(input: $input) {
        ok
        result {
            ...testFkA
        }
    }
}
'''
testFkAUpdate_gql = testFkA_Fragment + '''
mutation testFkAUpdate($input: TestFkAUpdateInput!, $where: TestFkAWhereInput!) {
  testFkAUpdate(input: $input, where: $where) {
    ok
    result {
      ...testFkA
    }
  }
}
'''

testFkB_Fragment = '''
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
'''
testFkBCreate_gql = testFkB_Fragment + '''
mutation testFkBCreate($input: TestFkBCreateInput!) {
    testFkBCreate(input: $input) {
        ok
        result {
            ...testFkB
        }
    }
}
'''

testFkBUpdate_gql = testFkB_Fragment + '''
mutation testFkBUpdate($input: TestFkBUpdateInput!, $where: TestFkBWhereInput!) {
  testFkBUpdate(input: $input, where: $where) {
    ok
    result {
      ...testFkB
    }
  }
}
'''

testFkC_Fragment = '''
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
'''
testFkCCreate_gql = testFkC_Fragment + '''
mutation testFkCCreate($input: TestFkCCreateInput!) {
    testFkCCreate(input: $input) {
        ok
        result {
            ...testFkC
        }
    }
}
'''

testFkCUpdate_gql = testFkC_Fragment + '''
mutation testFkCUpdate($input: TestFkCUpdateInput!, $where: TestFkCWhereInput!) {
  testFkCUpdate(input: $input, where: $where) {
    ok
    result {
      ...testFkC
    }
  }
}
'''

def test_foreignkey():
    client = Client()


    variables = {
        "input": {
            "text": "a1",
            "testFkB": {
                "create": {
                    "text": "b1",
                    "testFkC": {
                        "create": {
                            "text": "c1"
                        }
                    }
                }
            }
        }
    }

    response = client.query(testFkACreate_gql, variables=variables).json()

    assert response["data"]["testFkACreate"]["ok"] == True
    a1_id = response["data"]["testFkACreate"]["result"]["id"]
    assert response["data"]["testFkACreate"]["result"]["text"] == "a1"
    b1_id = response["data"]["testFkACreate"]["result"]["testFkB"]["id"]
    assert response["data"]["testFkACreate"]["result"]["testFkB"]["text"] == "b1"
    c1_id = response["data"]["testFkACreate"]["result"]["testFkB"]["testFkC"]["id"]
    assert response["data"]["testFkACreate"]["result"]["testFkB"]["testFkC"]["text"] == "c1"


    variables = {
        "input": {
            "text": "a2",
            "testFkB": {
                "connect": {
                    "id":{"equals":b1_id}
                }
            }
        }
    }

    response = client.query(testFkACreate_gql, variables=variables).json()

    assert response["data"]["testFkACreate"]["ok"] == True
    a2_id = response["data"]["testFkACreate"]["result"]["id"]
    assert response["data"]["testFkACreate"]["result"]["text"] == "a2"
    assert response["data"]["testFkACreate"]["result"]["testFkB"]["id"] == b1_id
    assert response["data"]["testFkACreate"]["result"]["testFkB"]["text"] == "b1"
    assert response["data"]["testFkACreate"]["result"]["testFkB"]["testFkC"]["id"] == c1_id
    assert response["data"]["testFkACreate"]["result"]["testFkB"]["testFkC"]["text"] == "c1"


    variables = {
        "input": {
            "text": "b2",
            "testFkC": {
                "create": 
                    {"text": "c2"}
            },
            "testFkAs": {
                "connect": [
                    {"id": {"equals": a1_id}}
                ],
                "create": [
                    { "text": "a3"},
                    {"text": "a4"}
                ],
            }
        }
    }

    response = client.query(testFkBCreate_gql, variables=variables).json()

    assert response["data"]["testFkBCreate"]["ok"] == True
    b2_id =  response["data"]["testFkBCreate"]["result"]["id"]
    assert response["data"]["testFkBCreate"]["result"]["text"] == "b2"
    assert response["data"]["testFkBCreate"]["result"]["testFkAs"]["count"] == 3
    assert len(response["data"]["testFkBCreate"]["result"]["testFkAs"]["data"]) == 3
    c2_id = response["data"]["testFkBCreate"]["result"]["testFkC"]["id"]
    assert response["data"]["testFkBCreate"]["result"]["testFkC"]["text"] == "c2"
    response["data"]["testFkBCreate"]["result"]["testFkAs"]["data"][0]["id"] == a1_id 
    assert response["data"]["testFkBCreate"]["result"]["testFkAs"]["data"][0]["text"] == "a1"
    a3_id = response["data"]["testFkBCreate"]["result"]["testFkAs"]["data"][1]["id"]
    assert response["data"]["testFkBCreate"]["result"]["testFkAs"]["data"][1]["text"] == "a3"
    a4_id = response["data"]["testFkBCreate"]["result"]["testFkAs"]["data"][2]["id"]
    assert response["data"]["testFkBCreate"]["result"]["testFkAs"]["data"][2]["text"] == "a4"


    variables = {
        "input": {
            "text": "b3",
            "testFkC": {
                "connect": { 
                    "id": {"equals": c1_id}
                }
            },
        }
    }

    response = client.query(testFkBCreate_gql, variables=variables).json()


    assert response["data"]["testFkBCreate"]["ok"] == True
    b3_id = response["data"]["testFkBCreate"]["result"]["id"]
    assert response["data"]["testFkBCreate"]["result"]["text"] == "b3"
    assert response["data"]["testFkBCreate"]["result"]["testFkAs"]["count"] == 0
    assert len(response["data"]["testFkBCreate"]["result"]["testFkAs"]["data"]) == 0
    assert response["data"]["testFkBCreate"]["result"]["testFkC"]["id"] == c1_id
    assert response["data"]["testFkBCreate"]["result"]["testFkC"]["text"] == "c1"


    variables = {
        "input": {
            "text": "c3",
            "testfkbSet": {
            "connect": [
                {"id": {"equals": b1_id}}
            ],
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
                        ]
                    }
                }
            ]
            }
        }
    }

    response = client.query(testFkCCreate_gql, variables=variables).json()

    assert response["data"]["testFkCCreate"]["ok"] == True
    c3_id = response["data"]["testFkCCreate"]["result"]["id"]
    assert response["data"]["testFkCCreate"]["result"]["text"] == "c3"
    assert response["data"]["testFkCCreate"]["result"]["testfkbSet"]["count"] == 2
    assert len(response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"]) == 2
    assert response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][0]["id"] == b1_id
    assert response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][0]["text"] == "b1"
    b4_id = response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][1]["id"]
    assert response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][1]["text"] == "b4"
    assert response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][0]["testFkAs"]["count"] == 0
    assert len(response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][0]["testFkAs"]["data"]) == 0
    assert response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][1]["testFkAs"]["count"] == 4
    assert len(response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][1]["testFkAs"]["data"]) == 4
    assert response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][1]["testFkAs"]["data"][0]["id"] == a1_id
    assert response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][1]["testFkAs"]["data"][0]["text"] == "a1"
    assert response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][1]["testFkAs"]["data"][1]["id"] == a2_id
    assert response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][1]["testFkAs"]["data"][1]["text"] == "a2"
    a6_id = response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][1]["testFkAs"]["data"][2]["id"]
    assert response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][1]["testFkAs"]["data"][2]["text"] == "a5"
    a6_id = response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][1]["testFkAs"]["data"][3]["id"]
    assert response["data"]["testFkCCreate"]["result"]["testfkbSet"]["data"][1]["testFkAs"]["data"][3]["text"] == "a6"



testO2oA_Fragment = '''
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
'''
testO2oACreate_gql = testO2oA_Fragment + '''
mutation testO2oACreate($input: TestO2oACreateInput!) {
    testO2oACreate(input: $input) {
        ok
        result {
            ...testO2oA
        }
    }
}
'''


testO2oB_Fragment = '''
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
'''
testO2oBCreate_gql = testO2oB_Fragment + '''
mutation testO2oBCreate($input: TestO2oBCreateInput!) {
    testO2oBCreate(input: $input) {
        ok
        result {
            ...testO2oB
        }
    }
}
'''

testO2oC_Fragment = '''
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
'''
testO2oCCreate_gql = testO2oC_Fragment + '''
mutation testO2oCCreate($input: TestO2oCCreateInput!) {
    testO2oCCreate(input: $input) {
        ok
        result {
            ...testO2oC
        }
    }
}
'''
def test_onetoone():
    client = Client()

    variables = {
        "input": {
            "text": "a1",
            "TestO2oB": {
                "create": {
                    "text": "b1",
                    "TestO2oC": {
                        "create": {
                            "text": "c1"
                        }
                    }
                }
            }
        }
    }

    response = client.query(testO2oACreate_gql, variables=variables).json()
    assert response["data"]["testO2oACreate"]["ok"]
    assert response["data"]["testO2oACreate"]["result"]["text"] == "a1"
    a1_id = response["data"]["testO2oACreate"]["result"]["id"]
    assert a1_id is not None
    assert response["data"]["testO2oACreate"]["result"]["TestO2oB"]["text"] == "b1"
    b1_id = response["data"]["testO2oACreate"]["result"]["TestO2oB"]["id"]
    assert b1_id is not None
    assert response["data"]["testO2oACreate"]["result"]["TestO2oB"]["TestO2oC"]["text"] == "c1"
    c1_id = response["data"]["testO2oACreate"]["result"]["TestO2oB"]["TestO2oC"]["id"]
    assert c1_id is not None

    variables = {
        "input": {
            "text": "b2",
            "testO2oA": {"create": {"text": "a2"}},
            "TestO2oC": {"create": {"text": "c2"}}
        }
    }

    response = client.query(testO2oBCreate_gql, variables=variables).json()

    assert response["data"]["testO2oBCreate"]["ok"]
    assert response["data"]["testO2oBCreate"]["result"]["text"] == "b2"
    b2_id = response["data"]["testO2oBCreate"]["result"]["id"]
    assert b2_id is not None
    assert response["data"]["testO2oBCreate"]["result"]["testO2oA"]["text"] == "a2"
    a2_id = response["data"]["testO2oBCreate"]["result"]["testO2oA"]["id"]
    assert a2_id is not None
    assert response["data"]["testO2oBCreate"]["result"]["TestO2oC"]["text"] == "c2"
    c2_id = response["data"]["testO2oBCreate"]["result"]["TestO2oC"]["id"]
    assert c2_id is not None

    variables = {
        "input": {
            "text": "c3",
            "testo2ob": {
                "create": {
                    "text": "b3",
                    "testO2oA": {
                        "connect": {
                            "id": {"equals": a1_id}
                        }
                    }
                }
            }
        }
    }

    response = client.query(testO2oCCreate_gql, variables=variables).json()

    assert response["data"]["testO2oCCreate"]["ok"]
    assert response["data"]["testO2oCCreate"]["result"]["text"] == "c3"
    c3_id = response["data"]["testO2oCCreate"]["result"]["id"]
    assert c3_id is not None
    assert response["data"]["testO2oCCreate"]["result"]["testo2ob"]["text"] == "b3"
    b3_id = response["data"]["testO2oCCreate"]["result"]["testo2ob"]["id"]
    assert b3_id is not None
    assert response["data"]["testO2oCCreate"]["result"]["testo2ob"]["testO2oA"]["text"] == "a1"
    assert response["data"]["testO2oCCreate"]["result"]["testo2ob"]["testO2oA"]["id"] == a1_id

testM2mA_Fragment = '''
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
'''
testM2mACreate_gql = testM2mA_Fragment + '''
mutation testM2mACreate($input: TestM2mACreateInput!) {
  testM2mACreate(input: $input) {
    ok
    result {
      ...testM2mA
    }
  }
}
'''

testM2mC_Fragment = '''
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
'''
testM2mCCreate_gql = testM2mC_Fragment + '''
mutation testM2mCCreate($input: TestM2mCCreateInput!) {
  testM2mCCreate(input: $input) {
    ok
    result {
      ...testM2mC
    }
  }
}
'''

def test_manytomany():
    client = Client()

    variables = {
        "input": {
            "text": "a1",
            "testM2mBs": {
                "create": [
                    {
                        "text": "b1",
                        "testM2mCs": {
                            "create": [
                                {"text": "c1"},
                                {"text": "c2"}
                            ]
                        }
                    },
                    {
                        "text": "b2",
                        "testM2mCs": {
                            "create": [
                                {"text": "c3"},
                                {"text": "c4"}
                            ]
                        }
                    },
                ]
            }
        }
    }

    response = client.query(testM2mACreate_gql, variables=variables).json()

    assert response["data"]["testM2mACreate"]["ok"] == True
    a1_id = response["data"]["testM2mACreate"]["result"]["id"]
    assert response["data"]["testM2mACreate"]["result"]["text"] == "a1"
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["count"] == 2
    assert len(response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"]) == 2
    b1_id = response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["id"]
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["text"] == "b1"
    b2_id = response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["id"]
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["text"] == "b2"
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["testM2mCs"]["count"] == 2
    assert len(response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["testM2mCs"]["data"]) == 2
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["testM2mCs"]["count"] == 2
    assert len(response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["testM2mCs"]["data"]) == 2
    c1_id = response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["testM2mCs"]["data"][0]["id"]
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["testM2mCs"]["data"][0]["text"] == "c1"
    c2_id = response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["testM2mCs"]["data"][1]["id"]
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["testM2mCs"]["data"][1]["text"] == "c2"
    c3_id = response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["testM2mCs"]["data"][0]["id"]
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["testM2mCs"]["data"][0]["text"] == "c3"
    c4_id = response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["testM2mCs"]["data"][1]["id"]
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["testM2mCs"]["data"][1]["text"] == "c4"

    variables = {
        "input": {
            "text": "a2",
            "testM2mBs": {
                "connect" : [
                    {"id":{"equals":b1_id}},
                    {"id":{"equals":b2_id}},
                ],
                "create" : [{
                    "text": "b3",
                    "testM2mCs": {
                        "connect" : [
                            {"id":{"equals":c1_id}},
                            {"id":{"equals":c2_id}},
                            {"id":{"equals":c3_id}},
                            {"id":{"equals":c4_id}},
                        ]
                    }
                }]
            }
        }
    }
    response = client.query(testM2mACreate_gql, variables=variables).json()

    assert response["data"]["testM2mACreate"]["ok"] == True
    a2_id = response["data"]["testM2mACreate"]["result"]["id"]
    assert response["data"]["testM2mACreate"]["result"]["text"] == "a2"
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["count"] == 3
    assert len(response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"]) == 3
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["id"] == b1_id
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["text"] == "b1"
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["id"] == b2_id
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["text"] == "b2"
    b3_id = response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][2]["id"]
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][2]["text"] == "b3"
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["testM2mCs"]["count"] == 2
    assert len(response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["testM2mCs"]["data"]) == 2
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["testM2mCs"]["count"] == 2
    assert len(response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["testM2mCs"]["data"]) == 2
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][2]["testM2mCs"]["count"] == 4
    assert len(response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][2]["testM2mCs"]["data"]) == 4
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["testM2mCs"]["data"][0]["id"] == c1_id
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["testM2mCs"]["data"][0]["text"] == "c1"
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["testM2mCs"]["data"][1]["id"] == c2_id
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][0]["testM2mCs"]["data"][1]["text"] == "c2"
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["testM2mCs"]["data"][0]["id"] == c3_id
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["testM2mCs"]["data"][0]["text"] == "c3"
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["testM2mCs"]["data"][1]["id"] == c4_id
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][1]["testM2mCs"]["data"][1]["text"] == "c4"
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][2]["testM2mCs"]["data"][0]["id"] == c1_id
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][2]["testM2mCs"]["data"][0]["text"] == "c1"
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][2]["testM2mCs"]["data"][1]["id"] == c2_id
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][2]["testM2mCs"]["data"][1]["text"] == "c2"
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][2]["testM2mCs"]["data"][2]["id"] == c3_id
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][2]["testM2mCs"]["data"][2]["text"] == "c3"
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][2]["testM2mCs"]["data"][3]["id"] == c4_id
    assert response["data"]["testM2mACreate"]["result"]["testM2mBs"]["data"][2]["testM2mCs"]["data"][3]["text"] == "c4"


    variables = {
    "input": {
        "text": "c5",
        "testm2mbSet": {
            "create": [
                {
                    "text": "b4",
                    "testM2mAs": {
                        "create": [
                            {"text": "a3"}
                        ],
                        "connect": [
                            {"id":{"equals":a1_id}}
                        ]
                    }
                }
            ],
            "connect": [
                {"id":{"equals":b1_id}}
            ]
        }
    }
    }

    response = client.query(testM2mCCreate_gql, variables=variables).json()

    assert response["data"]["testM2mCCreate"]["ok"] == True
    c5_id = response["data"]["testM2mCCreate"]["result"]["id"]
    assert response["data"]["testM2mCCreate"]["result"]["text"] == "c5"
    assert response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["count"] == 2
    assert len(response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"]) == 2
    assert response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][0]["id"] == b1_id
    assert response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][0]["text"] == "b1"
    b4_id = response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][1]["id"]
    assert response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][1]["text"] == "b4"
    assert response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][0]["testM2mAs"]["count"] == 2
    assert len(response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][0]["testM2mAs"]["data"]) == 2
    assert response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][1]["testM2mAs"]["count"] == 2
    assert len(response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][1]["testM2mAs"]["data"]) == 2
    assert response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][0]["testM2mAs"]["data"][0]["id"] == a1_id
    assert response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][0]["testM2mAs"]["data"][0]["text"] == "a1"
    assert response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][0]["testM2mAs"]["data"][1]["id"] == a2_id
    assert response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][0]["testM2mAs"]["data"][1]["text"] == "a2"
    assert response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][1]["testM2mAs"]["data"][0]["id"] == a1_id
    assert response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][1]["testM2mAs"]["data"][0]["text"] == "a1"
    a3_id = response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][1]["testM2mAs"]["data"][1]["id"]
    assert response["data"]["testM2mCCreate"]["result"]["testm2mbSet"]["data"][1]["testM2mAs"]["data"][1]["text"] == "a3"