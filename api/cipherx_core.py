"""CipherX core: password-based file encryption (AES-256-GCM + PBKDF2-HMAC-SHA256).

File format:  MAGIC(6) | salt(16) | nonce(12) | ciphertext + GCM tag(16)
MAGIC + salt + nonce are authenticated as associated data, so any change to the
header, the ciphertext or a wrong password makes decryption fail.
"""
import os
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MAGIC = b"CIPHX1"
SALT_LEN, NONCE_LEN, TAG_LEN = 16, 12, 16
ITERATIONS = 600_000  # OWASP / NIST SP 800-132 guidance for PBKDF2-HMAC-SHA256
EXT = ".cipherx"


class CipherXError(Exception):
    """Raised for wrong password, tampered data or invalid files."""


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS)
    return kdf.derive(password.encode("utf-8"))


def encrypt_bytes(data: bytes, password: str) -> bytes:
    if not password:
        raise CipherXError("Enter a password.")
    salt, nonce = os.urandom(SALT_LEN), os.urandom(NONCE_LEN)
    header = MAGIC + salt + nonce
    ct = AESGCM(derive_key(password, salt)).encrypt(nonce, data, header)
    return header + ct


def decrypt_bytes(blob: bytes, password: str) -> bytes:
    hl = len(MAGIC) + SALT_LEN + NONCE_LEN
    if len(blob) < hl + TAG_LEN or not blob.startswith(MAGIC):
        raise CipherXError("This is not a valid CipherX encrypted file.")
    header, ct = blob[:hl], blob[hl:]
    salt, nonce = header[len(MAGIC):len(MAGIC) + SALT_LEN], header[len(MAGIC) + SALT_LEN:]
    try:
        return AESGCM(derive_key(password, salt)).decrypt(nonce, ct, header)
    except InvalidTag:
        raise CipherXError("Wrong password, or the file was modified or damaged.")
