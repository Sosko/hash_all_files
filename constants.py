import hashlib

SUPPORTED_HASHES = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256
}

MAX_LENGTH_QUEUE = 100
