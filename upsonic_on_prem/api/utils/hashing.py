import hashlib

def string_to_sha256(input_string: str) -> str:
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_string.encode('utf-8'))
    return sha256_hash.hexdigest()




