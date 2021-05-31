import requests
import json

query = """
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

variables = {
    "file": {"upload": None},
    "image": {"upload": None},
}

operations = json.dumps({"query": query, "variables": variables})


data = {
    "operations": operations,
    "map": json.dumps(
        {
            "0": ["variables.file.upload"],
            "1": ["variables.image.upload"],
        }
    ),
}
files = {
    "0": ("lorem2.txt", open("files/lorem.txt", "rb"), "text/plain"),
    "1": ("fork2.jpg", open("files/fork.jpg", "rb"), "text/plain"),
}

r = requests.post("http://127.0.0.1:1234/graphql/", files=files, data=data)

print(json.dumps(json.loads(r.text), indent=4))
