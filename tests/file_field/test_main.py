# -*- coding: utf-8 -*-
import pytest
from tests.client import Client
from tests.utils import verify_response
import json
from .models import TestFile
import base64

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


def test_main():

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
    verify_response(expected_response, response)
    assert response["data"]["testFileCreate"]["result"]["file"]["content"].startswith(
        "TG9yZW0gaXBzdW0gZG9sb3Igc2l0IGFtZXQsIG"
    )
    assert response["data"]["testFileCreate"]["result"]["image"]["content"].startswith(
        "/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAMCAg"
    )
