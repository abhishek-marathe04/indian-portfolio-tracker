"""AES-256-GCM encryption for sensitive fields (PAN numbers)."""
import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# A fixed salt is acceptable here because the encryption key is derived from a
# user-controlled secret (ENCRYPTION_KEY env var).  Changing the salt invalidates
# all existing encrypted values, so we keep it constant.
_KDF_SALT = b"portfolio_tracker_pan_v1"


def _derive_key(secret: str) -> bytes:
    """Derive a 32-byte AES-256 key from the ENCRYPTION_KEY env var."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=_KDF_SALT,
        iterations=100_000,
    )
    return kdf.derive(secret.encode())


def _get_key() -> bytes:
    secret = os.getenv("ENCRYPTION_KEY")
    if not secret:
        raise RuntimeError(
            "ENCRYPTION_KEY is not set in .env — cannot encrypt/decrypt PAN numbers."
        )
    return _derive_key(secret)


def encrypt(plaintext: str) -> str:
    """Encrypt *plaintext* with AES-256-GCM and return a base64 string.

    Format: base64( nonce(12 bytes) || ciphertext+tag )
    """
    key = _get_key()
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("ascii")


def decrypt(token: str) -> str:
    """Decrypt a base64 token produced by :func:`encrypt`."""
    key = _get_key()
    raw = base64.b64decode(token.encode("ascii"))
    nonce, ciphertext = raw[:12], raw[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
