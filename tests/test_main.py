# -*- coding: utf-8 -*-
import pytest
from tests.client import Client
from django.contrib.auth.models import User

QUERY_GET_ALL_USERS = '''
query{users{data{id, username}}}
'''
def test_main():
    USER_LEN = 10
    for i in range(USER_LEN):
        u = User(username="user" + str(i), password="Secret.123")
        u.save()

    client = Client()
    response = client.query(QUERY_GET_ALL_USERS).json()
    assert len(response["data"]["users"]["data"]) == USER_LEN



