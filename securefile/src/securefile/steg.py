"""
Optimized Max Capacity LSB steganography for PNG images.
Uses Pillow's PixelAccess for memory-efficient processing.
"""
from PIL import Image
import os

def capacity_in_bytes(pil_image: Image.Image) -> int:
    w, h = pil_image.size
    return (w * h * 3) // 2

def _bytes_to_4bit_chunks(data: bytes):
    for b in data:
        yield (b >> 4) & 0x0F
        yield b & 0x0F

def _4bit_chunks_to_bytes(chunks_iter, num_chunks):
    out = bytearray()
    byte = 0
    is_high_nibble = True
    count = 0
    
    for chunk in chunks_iter:
        if count >= num_chunks: break
        if is_high_nibble:
            byte = (chunk << 4)
            is_high_nibble = False
        else:
            byte |= (chunk & 0x0F)
            out.append(byte)
            byte = 0
            is_high_nibble = True
        count += 1
    return bytes(out)

def embed_bytes_into_png(payload: bytes, cover_path: str, out_path: str):
    if not os.path.exists(cover_path):
        raise FileNotFoundError(f"Cover image not found: {cover_path}")

    img = Image.open(cover_path).convert("RGBA")
    max_bytes = capacity_in_bytes(img)
    total_len = len(payload)
    
    full_data = total_len.to_bytes(4, "big") + payload

    if len(full_data) > max_bytes:
        raise ValueError(f"File too big! Need {len(full_data)/1024/1024:.2f} MB, "
                         f"Capacity is {max_bytes/1024/1024:.2f} MB.")

    total_chunks = len(full_data) * 2
    data_chunks = _bytes_to_4bit_chunks(full_data)
    chunks_embedded = 0
    MASK = 0xF0
    
    # Memory efficient direct pixel access
    pixels = img.load()
    w, h = img.size

    for y in range(h):
        for x in range(w):
            if chunks_embedded >= total_chunks:
                break
                
            r, g, b, a = pixels[x, y]
            
            if chunks_embedded < total_chunks:
                r = (r & MASK) | next(data_chunks, 0)
                chunks_embedded += 1
            if chunks_embedded < total_chunks:
                g = (g & MASK) | next(data_chunks, 0)
                chunks_embedded += 1
            if chunks_embedded < total_chunks:
                b = (b & MASK) | next(data_chunks, 0)
                chunks_embedded += 1

            pixels[x, y] = (r, g, b, a)
            
        if chunks_embedded >= total_chunks:
            break

    out_dir = os.path.dirname(out_path)
    if out_dir: os.makedirs(out_dir, exist_ok=True)
    img.save(out_path, "PNG")

def extract_bytes_from_png(stego_path: str) -> bytes:
    if not os.path.exists(stego_path):
        raise FileNotFoundError(f"Stego image not found: {stego_path}")

    img = Image.open(stego_path).convert("RGBA")
    pixels = img.load()
    w, h = img.size

    def chunk_iter():
        for y in range(h):
            for x in range(w):
                r, g, b, a = pixels[x, y]
                yield r & 0x0F
                yield g & 0x0F
                yield b & 0x0F

    chunk_gen = chunk_iter()
    header_chunks = []
    
    for _ in range(8):
        try:
            header_chunks.append(next(chunk_gen))
        except StopIteration:
            raise ValueError("Image too small (no header found)")
            
    len_data = _4bit_chunks_to_bytes(iter(header_chunks), 8)
    payload_len = int.from_bytes(len_data, "big")
    
    total_payload_chunks = payload_len * 2
    return _4bit_chunks_to_bytes(chunk_gen, total_payload_chunks)