"""Where the export files are kept: the exports/ folder of the bucket in production (Cloud Storage,
with the instance's own credentials from the metadata server, as docker/fetch_seed.py does), and
the exports/ folder of the repository when developing (ignored by git)."""

import json
import shutil
import urllib.parse
import urllib.request
from pathlib import Path

from django.conf import settings

CHUNK = 1 << 20
METADATA_TOKEN = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Folder:
    def __init__(self, path):
        self.path = Path(path)

    def save(self, name, source):
        self.path.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, self.path / name)

    def chunks(self, name):
        with open(self.path / name, "rb") as file:
            while chunk := file.read(CHUNK):
                yield chunk


class Bucket:
    PREFIX = "exports/"

    def __init__(self, bucket):
        self.bucket = bucket

    @staticmethod
    def token():
        request = urllib.request.Request(METADATA_TOKEN, headers={"Metadata-Flavor": "Google"})
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.load(response)["access_token"]

    def save(self, name, source):
        query = urllib.parse.urlencode({"uploadType": "media", "name": self.PREFIX + name})
        url = f"https://storage.googleapis.com/upload/storage/v1/b/{self.bucket}/o?{query}"
        size = Path(source).stat().st_size
        with open(source, "rb") as file:
            request = urllib.request.Request(url, data=file, method="POST", headers={
                "Authorization": f"Bearer {self.token()}", "Content-Type": XLSX, "Content-Length": str(size),
            })
            with urllib.request.urlopen(request, timeout=600):
                pass

    def chunks(self, name):
        quoted = urllib.parse.quote(self.PREFIX + name, safe="")
        url = f"https://storage.googleapis.com/storage/v1/b/{self.bucket}/o/{quoted}?alt=media"
        request = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.token()}"})
        with urllib.request.urlopen(request, timeout=60) as response:
            while chunk := response.read(CHUNK):
                yield chunk


def storage():
    if settings.EXPORTS_BUCKET:
        return Bucket(settings.EXPORTS_BUCKET)
    return Folder(settings.EXPORTS_DIR)
