# -*- coding: utf-8 -*-
import pytest
from tests.client import Client
from tests.utils import verify_response
import json

from django.contrib.auth.models import User


QUERY_GET_ALL_USERS = """
query{users{data{id, username}}}
"""

user_fragment = """
fragment user on UserType {
  id
  username
  password
  firstName
  lastName
  isStaff
  isSuperuser
  groups{
    count
    data{
      id
      name
    }
  }
}
"""
users_gql = (
    user_fragment
    + """
query users($where:UserWhereInput) {
  users(where:$where) {
    count
    data{
      ...user
    }
  }
}
"""
)
userCreate_gql = (
    user_fragment
    + """
mutation userCreate($input: UserCreateInput!) {
  userCreate(input: $input) {
    ok
    result {
      ...user
    }
  }
}
"""
)
userUpdate_gql = (
    user_fragment
    + """
mutation userUpdate($input: UserUpdateInput!, $where: UserWhereInput!) {
  userUpdate(input: $input, where:$where) {
    ok
    result {
      ...user
    }
  }
}
"""
)

group_fragment = """
fragment group on GroupType {
  id
  name
  userSet {
    count
    data {
      id
      username
      password
      firstName
      lastName
      isStaff
      isSuperuser
    }
  }
}
"""
groupCreate_gql = (
    group_fragment
    + """
mutation groupCreate($input: GroupCreateInput!) {
  groupCreate(input: $input) {
    ok
    result {
      ...group
    }
  }
}
"""
)

groupUdate_gql = (
    group_fragment
    + """
mutation groupUpdate($input: GroupUpdateInput!, $where:GroupWhereInput!) {
  groupUpdate(input: $input, where:$where) {
    ok
    result {
      ...group
    }
  }
}
"""
)


def test_main():

    client = Client()

    variables = {
        "input": {
            "name": "g1",
            "userSet": {
                "create": [
                    {
                        "username": "u1",
                        "password": "u1pwd",
                        "firstName": "u1fn",
                        "lastName": "u1ln",
                    },
                    {
                        "username": "u2",
                        "password": "u2pwd",
                        "firstName": "u2fn",
                        "lastName": "u2ln",
                    },
                ]
            },
        }
    }
    expected_response = {
        "data": {
            "groupCreate": {
                "ok": True,
                "result": {
                    "name": "g1",
                    "userSet": {
                        "count": 2,
                        "data": [
                            {
                                "username": "u1",
                                "firstName": "u1fn",
                                "lastName": "u1ln",
                                "isStaff": False,
                                "isSuperuser": False,
                            },
                            {
                                "username": "u2",
                                "firstName": "u2fn",
                                "lastName": "u2ln",
                                "isStaff": False,
                                "isSuperuser": False,
                            },
                        ],
                    },
                },
            }
        }
    }

    response = client.query(groupCreate_gql, variables=variables).json()
    verify_response(expected_response, response)
    assert (
        response["data"]["groupCreate"]["result"]["userSet"]["data"][0]["password"]
        != "u1pwd"
    )
    assert (
        response["data"]["groupCreate"]["result"]["userSet"]["data"][1]["password"]
        != "u2pwd"
    )

    g1_id = response["data"]["groupCreate"]["result"]["id"]
    u1_id = response["data"]["groupCreate"]["result"]["userSet"]["data"][0]["id"]
    u2_id = response["data"]["groupCreate"]["result"]["userSet"]["data"][1]["id"]

    variables = {
        "input": {
            "username": "u3",
            "password": "u3pwd",
            "firstName": "u3fn",
            "lastName": "u3ln",
            "groups": {
                "connect": [
                    {"AND": [{"id": {"equals": g1_id}}, {"name": {"equals": "g1"}}]},
                ],
                "create": [
                    {
                        "name": "g2",
                        "userSet": {
                            "connect": [
                                {
                                    "AND": [
                                        {"id": {"equals": u1_id}},
                                        {"username": {"equals": "u1"}},
                                    ]
                                },
                                {"id": {"equals": u2_id}},
                            ],
                            "create": [
                                {
                                    "username": "u4",
                                    "password": "u4pwd",
                                    "firstName": "u4fn",
                                    "lastName": "u4ln",
                                },
                                {
                                    "username": "u5",
                                    "password": "u5pwd",
                                    "firstName": "u5fn",
                                    "lastName": "u5ln",
                                },
                            ],
                        },
                    }
                ],
            },
        }
    }
    expected_response = {
        "data": {
            "userCreate": {
                "ok": True,
                "result": {
                    "username": "u3",
                    "firstName": "u3fn",
                    "lastName": "u3ln",
                    "isStaff": False,
                    "isSuperuser": False,
                    "groups": {
                        "count": 2,
                        "data": [{"id": g1_id, "name": "g1"}, {"name": "g2"}],
                    },
                },
            }
        }
    }

    response = client.query(userCreate_gql, variables=variables).json()
    verify_response(expected_response, response)
    assert response["data"]["userCreate"]["result"]["password"] != "u3pwd"
    u3_id = response["data"]["userCreate"]["result"]["id"]
    g2_id = response["data"]["userCreate"]["result"]["groups"]["data"][1]["id"]

    variables = {
        "where": {"id": {"equals": g2_id}},
        "input": {
            "name": "g2_update",
            "userSet": {
                "connect": [{"id": {"equals": u2_id}}],
                "disconnect": [{"id": {"equals": u1_id}}],
                "delete": [{"id": {"equals": u3_id}}],
            },
        },
    }
    expected_response = {
        "data": {
            "groupUpdate": {
                "ok": True,
                "result": {
                    "id": g2_id,
                    "name": "g2_update",
                    "userSet": {
                        "count": 3,
                        "data": [
                            {
                                "id": u2_id,
                                "username": "u2",
                                "firstName": "u2fn",
                                "lastName": "u2ln",
                                "isStaff": False,
                                "isSuperuser": False,
                            },
                            {
                                "username": "u4",
                                "firstName": "u4fn",
                                "lastName": "u4ln",
                                "isStaff": False,
                                "isSuperuser": False,
                            },
                            {
                                "username": "u5",
                                "firstName": "u5fn",
                                "lastName": "u5ln",
                                "isStaff": False,
                                "isSuperuser": False,
                            },
                        ],
                    },
                },
            }
        }
    }

    response = client.query(groupUdate_gql, variables=variables).json()
    verify_response(expected_response, response)

    assert (
        response["data"]["groupUpdate"]["result"]["userSet"]["data"][0]["password"]
        != "u2pwd"
    )
    assert (
        response["data"]["groupUpdate"]["result"]["userSet"]["data"][1]["password"]
        != "u4pwd"
    )
    assert (
        response["data"]["groupUpdate"]["result"]["userSet"]["data"][2]["password"]
        != "u5pwd"
    )

    u4_id = response["data"]["groupUpdate"]["result"]["userSet"]["data"][1]["id"]
    u5_id = response["data"]["groupUpdate"]["result"]["userSet"]["data"][2]["id"]

    variables = {"where": {"groups": {"id": {"in": [g1_id, g2_id]}}}}
    expected_response = {
        "data": {
            "users": {
                "count": 4,
                "data": [
                    {
                        "id": u1_id,
                        "username": "u1",
                        "firstName": "u1fn",
                        "lastName": "u1ln",
                        "isStaff": False,
                        "isSuperuser": False,
                        "groups": {"count": 1, "data": [{"id": g1_id, "name": "g1"}]},
                    },
                    {
                        "id": u2_id,
                        "username": "u2",
                        "firstName": "u2fn",
                        "lastName": "u2ln",
                        "isStaff": False,
                        "isSuperuser": False,
                        "groups": {
                            "count": 2,
                            "data": [
                                {"id": g1_id, "name": "g1"},
                                {"id": g2_id, "name": "g2_update"},
                            ],
                        },
                    },
                    {
                        "id": u4_id,
                        "username": "u4",
                        "firstName": "u4fn",
                        "lastName": "u4ln",
                        "isStaff": False,
                        "isSuperuser": False,
                        "groups": {
                            "count": 1,
                            "data": [{"id": "2", "name": "g2_update"}],
                        },
                    },
                    {
                        "id": u5_id,
                        "username": "u5",
                        "firstName": "u5fn",
                        "lastName": "u5ln",
                        "isStaff": False,
                        "isSuperuser": False,
                        "groups": {
                            "count": 1,
                            "data": [{"id": g2_id, "name": "g2_update"}],
                        },
                    },
                ],
            }
        }
    }

    response = client.query(users_gql, variables=variables).json()
    verify_response(expected_response, response)

    variables = {
        "where": {
            "AND": [
                {"username": {"contains": "u"}},
                {
                    "OR": [
                        {"groups": {"id": {"equals": g2_id}}},
                        {"groups": {"user": {"isSuperuser": {"exact": True}}}},
                    ]
                },
            ]
        }
    }
    expected_response = {
        "data": {
            "users": {
                "count": 3,
                "data": [
                    {
                        "id": u2_id,
                        "username": "u2",
                        "firstName": "u2fn",
                        "lastName": "u2ln",
                        "isStaff": False,
                        "isSuperuser": False,
                        "groups": {
                            "count": 2,
                            "data": [
                                {"id": g1_id, "name": "g1"},
                                {"id": g2_id, "name": "g2_update"},
                            ],
                        },
                    },
                    {
                        "id": u4_id,
                        "username": "u4",
                        "firstName": "u4fn",
                        "lastName": "u4ln",
                        "isStaff": False,
                        "isSuperuser": False,
                        "groups": {
                            "count": 1,
                            "data": [{"id": g2_id, "name": "g2_update"}],
                        },
                    },
                    {
                        "id": u5_id,
                        "username": "u5",
                        "firstName": "u5fn",
                        "lastName": "u5ln",
                        "isStaff": False,
                        "isSuperuser": False,
                        "groups": {
                            "count": 1,
                            "data": [{"id": g2_id, "name": "g2_update"}],
                        },
                    },
                ],
            }
        }
    }
    response = client.query(users_gql, variables=variables).json()
    verify_response(expected_response, response)
