"""
AES-GCM encryption with Argon2id KDF for SecureFile.
Includes AAD (Associated Data) for payload integrity.
"""
import os
from struct import pack, unpack
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type

MAGIC = b"SFIL"
VERSION = 1
KDF_ARGON2ID = 1

# KDF parameters
ARGON2_TIME = 2
ARGON2_MEMORY = 64 * 1024  # 64 MiB
ARGON2_PARALLELISM = 2
KEY_LEN = 32  # AES-256
SALT_LEN = 16
NONCE_LEN = 12

def _derive_key(password: str, salt: bytes) -> bytes:
    password_bytes = password.encode("utf-8") if isinstance(password, str) else password
    return hash_secret_raw(
        secret=password_bytes,
        salt=salt,
        time_cost=ARGON2_TIME,
        memory_cost=ARGON2_MEMORY,
        parallelism=ARGON2_PARALLELISM,
        hash_len=KEY_LEN,
        type=Type.ID,
    )

def encrypt_bytes(plaintext: bytes, password: str) -> bytes:
    if not isinstance(plaintext, (bytes, bytearray)):
        raise TypeError("plaintext must be bytes")

    salt = os.urandom(SALT_LEN)
    key = _derive_key(password, salt)
    nonce = os.urandom(NONCE_LEN)
    aesgcm = AESGCM(key)

    # Header used as Associated Data (AAD) to prevent tampering
    header = (
        MAGIC + 
        bytes([VERSION]) + 
        bytes([KDF_ARGON2ID]) + 
        bytes([len(salt)]) + salt + 
        bytes([len(nonce)]) + nonce
    )
    
    ciphertext = aesgcm.encrypt(nonce, plaintext, header)
    return header + pack(">I", len(ciphertext)) + ciphertext

def _parse_blob_header(blob: bytes) -> Tuple[int, int, bytes, bytes, bytes, bytes]:
    off = 0
    if len(blob) < 4 or blob[0:4] != MAGIC:
        raise ValueError("Not a SecureFile blob (MAGIC mismatch)")
    off += 4
    
    version = blob[off]; off += 1
    kdf_id = blob[off]; off += 1
    
    salt_len = blob[off]; off += 1
    salt = blob[off : off + salt_len]; off += salt_len
    
    nonce_len = blob[off]; off += 1
    nonce = blob[off : off + nonce_len]; off += nonce_len
    
    header_aad = blob[:off]
    
    (ct_len,) = unpack(">I", blob[off : off + 4]); off += 4
    ciphertext = blob[off : off + ct_len]
    
    return version, kdf_id, salt, nonce, ciphertext, header_aad

def decrypt_bytes(blob: bytes, password: str) -> bytes:
    version, kdf_id, salt, nonce, ciphertext, header_aad = _parse_blob_header(blob)
    if kdf_id != KDF_ARGON2ID:
        raise ValueError(f"Unsupported KDF id: {kdf_id}")
        
    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    
    # Decrypt and authenticate header AAD
    plaintext = aesgcm.decrypt(nonce, ciphertext, header_aad)
    return plaintext