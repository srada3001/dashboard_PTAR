"""Downloads the database that replaces production's (scripts/gcp/replace-db.sh) from the service's
bucket, with the instance's own credentials (metadata server), and checks it before using it.

Usage: python docker/fetch_seed.py BUCKET OBJECT TARGET [SHA256]
"""

import hashlib
import json
import os
import shutil
import sqlite3
import sys
import urllib.parse
import urllib.request

METADATA_TOKEN = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"


def access_token():
    request = urllib.request.Request(METADATA_TOKEN, headers={"Metadata-Flavor": "Google"})
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)["access_token"]


def download(bucket, name, target):
    url = f"https://storage.googleapis.com/storage/v1/b/{bucket}/o/{urllib.parse.quote(name, safe='')}?alt=media"
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token()}"})
    digest = hashlib.sha256()
    with urllib.request.urlopen(request, timeout=600) as response, open(target, "wb") as file:
        while chunk := response.read(1 << 20):
            digest.update(chunk)
            file.write(chunk)
    return digest.hexdigest()


def main(bucket, name, target, expected_sha256=""):
    partial = target + ".download"
    sha256 = download(bucket, name, partial)
    if expected_sha256 and sha256 != expected_sha256:
        os.remove(partial)
        sys.exit(f"La base descargada ({name}) no coincide con la subida: huella {sha256}.")
    connection = sqlite3.connect(partial)
    try:
        healthy = connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    finally:
        connection.close()
    if not healthy:
        sys.exit(f"La base descargada ({name}) está dañada.")
    shutil.move(partial, target)
    print(f"Base reemplazada con gs://{bucket}/{name}.")


if __name__ == "__main__":
    main(*sys.argv[1:])
