# -*- coding: utf-8 -*-
import pytest
from tests.client import Client
from tests.utils import verify_response
import json
from .models import *

from pathlib import Path


def test_main():

    client = Client()
