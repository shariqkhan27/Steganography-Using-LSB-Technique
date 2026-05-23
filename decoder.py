"""
Advanced Steganography Decoder Module
Extracts and decrypts hidden messages from images.
Self-destruct: one wrong password attempt overwrites all payload LSBs
with random noise and marks the image as poisoned.
"""

from PIL import Image
import numpy as np
import struct
import os
from security import SecurityLayer
from utils import SteganographyUtils

# Must match constants in encoder.py
FLAG_ALIVE    = 0b10101010   # 0xAA
FLAG_POISONED = 0b11111111   # 0xFF


class SteganographyDecoder:
    """
    Advanced decoder with self-destruct capability.
    """

    def __init__(self):
        self.security = SecurityLayer()
        self.utils    = SteganographyUtils()

    # ------------------------------------------------------------------ #
    #  Flag helpers (mirrors encoder)                                      #
    # ------------------------------------------------------------------ #

    def _read_flag(self, img_array: np.ndarray) -> int:
        height, width, _ = img_array.shape
        total_pixels = height * width
        bits = []
        for idx in range(total_pixels - 8, total_pixels):
            y, x = divmod(idx, width)
            bits.append(int(img_array[y, x, 0]) & 1)
        value = 0
        for b in bits:
            value = (value << 1) | b
        return value

    def _write_flag(self, img_array: np.ndarray, flag_byte: int) -> np.ndarray:
        arr = img_array.copy()
        height, width, _ = arr.shape
        total_pixels = height * width
        bits = [(flag_byte >> (7 - i)) & 1 for i in range(8)]
        for i, idx in enumerate(range(total_pixels - 8, total_pixels)):
            y, x = divmod(idx, width)
            v = (int(arr[y, x, 0]) & 0xFE) | bits[i]
            arr[y, x, 0] = np.uint8(v)
        return arr

    # ------------------------------------------------------------------ #
    #  Self-destruct                                                       #
    # ------------------------------------------------------------------ #

    def _destroy_payload(self, image_path: str, img_array: np.ndarray) -> None:
        """
        Overwrite every payload LSB with random noise and set the POISONED
        flag, then save the image back in place.
        """
        print("⚠️  Self-destruct triggered: overwriting payload LSBs with noise...")

        height, width, channels = img_array.shape
        destroyed = img_array.copy()
        flag_pixel_start = (height * width) - 8

        # Generate random bits for the entire payload zone
        pixel_counter = 0
        for y in range(height):
            for x in range(width):
                if pixel_counter >= flag_pixel_start:
                    break
                for c in range(channels):
                    noise_bit = int(np.random.randint(0, 2))
                    v = (int(destroyed[y, x, c]) & 0xFE) | noise_bit
                    destroyed[y, x, c] = np.uint8(v)
                pixel_counter += 1
            if pixel_counter >= flag_pixel_start:
                break

        # Write POISONED flag
        destroyed = self._write_flag(destroyed, FLAG_POISONED)

        # Save back to the same path (overwrite)
        Image.fromarray(destroyed, mode='RGB').save(image_path, 'PNG', optimize=False)
        print("💀 Image payload destroyed. File saved back.")

    # ------------------------------------------------------------------ #
    #  Public decode                                                       #
    # ------------------------------------------------------------------ #

    def decode(self, image_path: str, password: str) -> dict:
        """
        Extract and decrypt message from stego image.

        Self-destruct logic:
          - If flag == POISONED  → reject immediately (already destroyed).
          - If flag == ALIVE     → attempt decryption.
              • Success          → return message normally.
              • Wrong password   → destroy payload, return error.
        """
        try:
            img = Image.open(image_path)
            if img.mode not in ['RGB', 'RGBA']:
                img = img.convert('RGB')
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            img_array = np.array(img, dtype=np.uint8)
            height, width, channels = img_array.shape

            print(f"Image loaded: {width}x{height}, {channels} channels")

            # ── 1. Check self-destruct flag ──────────────────────────────
            flag = self._read_flag(img_array)
            print(f"Integrity flag: {bin(flag)} ({flag})")

            if flag == FLAG_POISONED:
                return {
                    'success': False,
                    'error':   (
                        '🔥 SELF-DESTRUCT TRIGGERED\n'
                        'A previous wrong password attempt has permanently destroyed '
                        'the hidden data in this image. The message cannot be recovered.'
                    )
                }

            if flag != FLAG_ALIVE:
                return {
                    'success': False,
                    'error':   'No steganographic data found (missing integrity flag).'
                }

            # ── 2. Extract LSBs (excluding flag zone) ────────────────────
            flag_pixel_start = (height * width) - 8
            all_bits = []
            pixel_counter = 0

            for y in range(height):
                for x in range(width):
                    if pixel_counter >= flag_pixel_start:
                        break
                    for c in range(channels):
                        all_bits.append(int(img_array[y, x, c]) & 1)
                    pixel_counter += 1
                if pixel_counter >= flag_pixel_start:
                    break

            print(f"Extracted {len(all_bits)} bits")

            if len(all_bits) < 32:
                return {'success': False, 'error': 'Image too small to contain hidden data'}

            # ── 3. Parse length header ───────────────────────────────────
            length_bytes   = self._bits_to_bytes(all_bits[:32])
            payload_length = struct.unpack('>I', length_bytes)[0]
            print(f"Payload length: {payload_length} bytes")

            max_possible = (len(all_bits) - 32) // 8
            if payload_length <= 0:
                return {'success': False, 'error': 'No hidden data found (invalid length)'}
            if payload_length > max_possible:
                return {
                    'success': False,
                    'error':   f'Image doesn\'t contain enough data ({payload_length} needed, {max_possible} available)'
                }

            total_bits_needed = 32 + payload_length * 8
            if total_bits_needed > len(all_bits):
                return {'success': False, 'error': 'Corrupted data: not enough bits'}

            payload = self._bits_to_bytes(all_bits[32:total_bits_needed])
            print(f"Payload extracted: {len(payload)} bytes")

            # ── 4. Parse magic ───────────────────────────────────────────
            pos = 0
            if len(payload) < 4:
                return {'success': False, 'error': 'Payload too small for magic number'}

            magic = payload[pos:pos + 4]
            if magic != b'STEG':
                return {
                    'success': False,
                    'error':   'No steganographic data found (wrong magic number).'
                }
            pos += 4

            # ── 5. Parse metadata ────────────────────────────────────────
            if pos + 4 > len(payload):
                return {'success': False, 'error': 'Corrupted: cannot read metadata length'}

            metadata_length = struct.unpack('>I', payload[pos:pos + 4])[0]
            pos += 4

            if metadata_length < 12 or metadata_length > len(payload) - pos:
                return {'success': False, 'error': f'Invalid metadata length: {metadata_length}'}

            meta = payload[pos:pos + metadata_length]
            mp   = 0

            def read_field(section, offset, name):
                if offset + 4 > len(section):
                    raise ValueError(f'Corrupted metadata: cannot read {name} length')
                flen = struct.unpack('>I', section[offset:offset + 4])[0]
                offset += 4
                if flen < 8 or flen > 256:
                    raise ValueError(f'Invalid {name} length: {flen}')
                if offset + flen > len(section):
                    raise ValueError(f'Corrupted metadata: {name} extends beyond section')
                return section[offset:offset + flen], offset + flen

            try:
                salt, mp = read_field(meta, mp, 'salt')
                iv,   mp = read_field(meta, mp, 'IV')
                tag,  mp = read_field(meta, mp, 'tag')
            except ValueError as ve:
                return {'success': False, 'error': str(ve)}

            pos += metadata_length

            if pos + 4 > len(payload):
                return {'success': False, 'error': 'Corrupted: cannot read data length'}

            data_length = struct.unpack('>I', payload[pos:pos + 4])[0]
            pos += 4

            if data_length <= 0 or pos + data_length > len(payload):
                return {'success': False, 'error': f'Invalid data length: {data_length}'}

            encrypted_data = payload[pos:pos + data_length]
            print(f"Encrypted data: {len(encrypted_data)} bytes | Salt: {len(salt)} | IV: {len(iv)} | Tag: {len(tag)}")

            # ── 6. Decrypt ───────────────────────────────────────────────
            try:
                decrypted = self.security.decrypt_message(
                    encrypted_data, salt, iv, tag, password
                )
                print(f"Decrypted: {len(decrypted)} bytes")

            except Exception as e:
                # ── WRONG PASSWORD → self-destruct ───────────────────────
                print(f"Decryption failed ({e}). Triggering self-destruct.")
                self._destroy_payload(image_path, img_array)

                return {
                    'success': False,
                    'destroyed': True,
                    'error': (
                        '🔥 WRONG PASSWORD — SELF-DESTRUCT ACTIVATED\n'
                        'The hidden message has been permanently erased from the image. '
                        'No further attempts are possible.'
                    )
                }

            # ── 7. Decode text ───────────────────────────────────────────
            import json
            try:
                msg_str  = decrypted.decode('utf-8')
                msg_json = json.loads(msg_str)
                return {
                    'success':     True,
                    'metadata':    msg_json.get('metadata', {}),
                    'message':     msg_json.get('content', ''),
                    'raw_message': msg_str
                }
            except (json.JSONDecodeError, UnicodeDecodeError):
                try:
                    msg_str = decrypted.decode('utf-8')
                    return {'success': True, 'metadata': {}, 'message': msg_str, 'raw_message': msg_str}
                except Exception:
                    return {'success': False, 'error': 'Failed to decode message as text'}

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': f'Decoding error: {str(e)}'}

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _bits_to_bytes(self, bits: list) -> bytes:
        if len(bits) % 8 != 0:
            bits = bits + [0] * (8 - len(bits) % 8)
        result = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | (bits[i + j] & 1)
            result.append(byte)
        return bytes(result)

    def detect_hidden_data(self, image_path: str) -> dict:
        """
        Detect if image contains hidden data and report its status.
        Returns dict with 'found' (bool), 'poisoned' (bool), 'message' (str).
        """
        try:
            img = Image.open(image_path)
            if img.mode not in ['RGB', 'RGBA']:
                img = img.convert('RGB')
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            img_array = np.array(img, dtype=np.uint8)
            height, width, channels = img_array.shape

            flag = self._read_flag(img_array)

            if flag == FLAG_POISONED:
                return {
                    'found':    True,
                    'poisoned': True,
                    'message':  '💀 Image contains destroyed steganographic data (self-destruct was triggered).'
                }

            if flag != FLAG_ALIVE:
                return {
                    'found':    False,
                    'poisoned': False,
                    'message':  'No steganographic data detected.'
                }

            # Also verify magic number
            bits = []
            count = 0
            for y in range(height):
                for x in range(width):
                    for c in range(channels):
                        if count < 64:
                            bits.append(int(img_array[y, x, c]) & 1)
                            count += 1

            if len(bits) >= 64:
                magic = self._bits_to_bytes(bits[32:64])
                if magic == b'STEG':
                    return {
                        'found':    True,
                        'poisoned': False,
                        'message':  '✅ Active steganographic data found. Data is intact and protected.'
                    }

            return {
                'found':    False,
                'poisoned': False,
                'message':  'No steganographic data detected.'
            }

        except Exception as e:
            return {'found': False, 'poisoned': False, 'message': f'Detection error: {e}'}
