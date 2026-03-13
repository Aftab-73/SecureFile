import tempfile
from PIL import Image
from securefile.crypto import encrypt_bytes, decrypt_bytes
from securefile.steg import embed_bytes_into_png, extract_bytes_from_png
import os

def test_encrypt_embed_extract_decrypt(tmp_path):
    w = 128; h = 128
    img = Image.new("RGB", (w,h), color=(120,130,140))
    cover = tmp_path/"cover.png"
    img.save(cover)

    payload = b"hello securefilr test"
    pwd = "testpassword"

    encrypted = encrypt_bytes(payload, pwd)
    stego = tmp_path/"stego.png"
    embed_bytes_into_png(encrypted, str(cover), str(stego))
    extracted = extract_bytes_from_png(str(stego))
    decrypted = decrypt_bytes(extracted, pwd)
    assert decrypted == payload
