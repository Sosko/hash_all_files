from hashlib import md5, sha1, sha256

SUPPORTED_HASHES = {
    "md5": md5,
    "sha1": sha1,
    "sha256": sha256
}

MAX_LENGTH_QUEUE = 100
