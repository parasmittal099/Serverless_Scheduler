#!/usr/bin/env python3
"""Set up the LAN S3 store (SeaweedFS) the experiments use. Idempotent.

Why: the five S3-backed services (120, 210, 311, 504 x2) move tens to hundreds of
MB per job. Against AWS S3 they all share the lab's single ~89 Mbit/s uplink, so
their latency measured uplink contention, not scheduling (2026-10-12 smoke run:
S3 services 218 s median vs 4.6 s for the rest; 6 of 10 uploads timed out).
A site-local store removes that bottleneck. MinIO's community image is no longer
published, hence SeaweedFS (S3 API on :9000).

Run on utorda1 (needs docker). Credentials come from .env:
    MINIO_ROOT_USER / MINIO_ROOT_PASSWORD   the store's access key / secret
and the experiments then use AWS_ENDPOINT_URL, AWS_ACCESS_KEY_ID and
AWS_SECRET_ACCESS_KEY from .env (set to the same values), pushed to nodes with
playbooks/sync_env.yml. The real AWS key is kept as REAL_AWS_* and unused.

What it does:
  * writes seaweed/s3.json (identity with the credentials; `anonymous` may read
    only public/*), starts the container `seaweed` (restart unless-stopped);
  * creates the bucket peercomputebucket2 and a 1-day expiry on output/ (a dna-
    visualisation job leaves a 168 MB output);
  * re-hosts the uploader's 98 MB model under public/ (the function names its local
    file after the URL's last segment, so it must be a plain, unsigned URL).
"""

import json
import os
import re
import subprocess
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")
DATA = os.path.join(HOME, "seaweed")
BUCKET = "peercomputebucket2"
MODEL_URL = "https://download.pytorch.org/models/resnet50-19c8e357.pth"
MODEL_KEY = "public/resnet50-19c8e357.pth"


def env_vars():
    text = open(os.path.join(ROOT, ".env")).read()
    got = dict(re.findall(r"^(?:export )?(MINIO_ROOT_USER|MINIO_ROOT_PASSWORD)=(.*)$", text, re.M))
    if len(got) != 2:
        raise SystemExit("set MINIO_ROOT_USER and MINIO_ROOT_PASSWORD in .env first")
    return got["MINIO_ROOT_USER"], got["MINIO_ROOT_PASSWORD"]


def main():
    user, password = env_vars()
    os.makedirs(os.path.join(DATA, "data"), exist_ok=True)
    os.chmod(DATA, 0o700)  # the credentials file below is readable by the container's user
    cfg = {"identities": [
        {"name": "peercompute", "credentials": [{"accessKey": user, "secretKey": password}],
         "actions": ["Admin", "Read", "Write", "List", "Tagging"]},
        {"name": "anonymous", "actions": [f"Read:{BUCKET}/public/*"]},
    ]}
    cfg_path = os.path.join(DATA, "s3.json")
    with open(cfg_path, "w") as f:
        json.dump(cfg, f)
    os.chmod(cfg_path, 0o644)

    subprocess.run(["docker", "rm", "-f", "seaweed"], capture_output=True)
    subprocess.run(
        ["docker", "run", "-d", "--name", "seaweed", "--restart", "unless-stopped",
         "-p", "9000:8333", "-v", f"{DATA}/data:/data", "-v", f"{cfg_path}:/etc/seaweedfs/s3.json:ro",
         "chrislusf/seaweedfs", "server", "-dir=/data", "-s3", "-s3.port=8333",
         "-s3.config=/etc/seaweedfs/s3.json"], check=True)

    import boto3
    s3 = boto3.client("s3", endpoint_url="http://127.0.0.1:9000", aws_access_key_id=user,
                      aws_secret_access_key=password, region_name="ap-south-1")
    for _ in range(30):  # the master needs ~20 s to elect itself
        try:
            s3.create_bucket(Bucket=BUCKET)
            break
        except s3.exceptions.BucketAlreadyOwnedByYou:
            break
        except Exception:
            time.sleep(3)
    s3.put_bucket_lifecycle_configuration(Bucket=BUCKET, LifecycleConfiguration={"Rules": [
        {"ID": "expire-output", "Status": "Enabled", "Filter": {"Prefix": "output/"},
         "Expiration": {"Days": 1}}]})
    tmp = "/tmp/_resnet.pth"
    urllib.request.urlretrieve(MODEL_URL, tmp)
    s3.upload_file(tmp, BUCKET, MODEL_KEY)
    os.remove(tmp)
    print(f"ready: http://<this host>:9000/{BUCKET}  (model at /{MODEL_KEY})")


if __name__ == "__main__":
    main()
