# -*- coding: utf-8 -*-
from tests.client import Client
from graphene_django.utils.testing import GraphQLTestCase
from tests.utils import VerifyResponseAssertionMixins
import json
import base64
import os
from django.conf import settings
from shutil import rmtree

from pathlib import Path

FILES_DIR = str(Path(__file__).resolve().parent) + "/files"

QUERY = """
mutation ($file: FileInput, $image: FileInput) {
  testFileCreate(input: {file: $file, image: $image}) {
    ok
    result {
      id
      file {
        filename
        size
        url
        content
      }
      image {
        filename
        size
        url
        content
      }
    }
  }
}
"""
with open(FILES_DIR + "/lorem.txt", "rb") as f:
    b64_lorem = base64.b64encode(f.read()).decode("utf-8")
with open(FILES_DIR + "/fork.jpg", "rb") as f:
    b64_img = base64.b64encode(f.read()).decode("utf-8")


class FileFieldTest(GraphQLTestCase, VerifyResponseAssertionMixins):

    def setUp(self):
        try:
            rmtree(settings.MEDIA_ROOT)
        except FileNotFoundError:
            pass

    def tearDown(self):
        try:
            rmtree(settings.MEDIA_ROOT)
        except FileNotFoundError:
            pass
        
    def test_main(self):

        client = Client()
        variables = {
            "file": {"filename": "lorem1.txt", "content": b64_lorem},
            "image": {"filename": "fork1.jpg", "content": b64_img},
        }
        expected_response = json.loads(
            """
            {
            "data": {
                "testFileCreate": {
                    "ok": true,
                    "result": {
                        "id": "1",
                        "file": {
                            "filename": "lorem1.txt",
                            "size": 2941,
                            "url": "/media/lorem1.txt"
                        },
                        "image": {
                            "url": "/media/fork1.jpg",
                            "size": 39116,
                            "filename": "fork1.jpg"
                        }
                    }
                }
            }
        }
        """
        )

        response = client.query(QUERY, variables=variables).json()
        self.verify_response(response, expected_response)
        self.assertTrue(
            response["data"]["testFileCreate"]["result"]["file"]["content"].startswith(
                "TG9yZW0gaXBzdW0gZG9sb3Igc2l0IGFtZXQsIG"
            )
        )
        self.assertTrue(
            response["data"]["testFileCreate"]["result"]["image"]["content"].startswith(
                "/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAMCAg"
            )
        )
