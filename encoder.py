"""
Advanced Steganography Encoder Module
Implements LSB encoding with encryption and security features
Includes self-destruct flag embedded inside the image
"""

from PIL import Image
import numpy as np
import struct
from security import SecurityLayer
from utils import SteganographyUtils

# Self-destruct flag constants
# We reserve the LAST 8 pixels (24 bits) of the image for the flag
# Flag layout: [8 bits ALIVE marker] [8 bits POISONED marker] [8 bits reserved]
FLAG_ALIVE    = 0b10101010   # 0xAA — data is intact
FLAG_POISONED = 0b11111111   # 0xFF — data has been destroyed


class SteganographyEncoder:
    """
    High-security steganography encoder with self-destruct support
    """

    def __init__(self):
        self.security = SecurityLayer()
        self.utils = SteganographyUtils()
        self.bits_per_channel = 1

    # ------------------------------------------------------------------ #
    #  Flag helpers                                                        #
    # ------------------------------------------------------------------ #

    def _write_flag_bits(self, img_array: np.ndarray, flag_byte: int) -> np.ndarray:
        """
        Write an 8-bit flag into the LSBs of the last 8 pixels' red channel.
        These pixels are at the very end of the flattened image, making them
        easy to locate without any offset arithmetic.
        """
        arr = img_array.copy()
        height, width, _ = arr.shape
        total_pixels = height * width

        bits = [(flag_byte >> (7 - i)) & 1 for i in range(8)]

        written = 0
        for idx in range(total_pixels - 8, total_pixels):
            y, x = divmod(idx, width)
            pixel_val = int(arr[y, x, 0])          # red channel only
            pixel_val = (pixel_val & 0xFE) | bits[written]
            arr[y, x, 0] = np.uint8(pixel_val)
            written += 1

        return arr

    def _read_flag_bits(self, img_array: np.ndarray) -> int:
        """
        Read the 8-bit flag back from the last 8 pixels' red channel LSBs.
        Returns the flag byte as an integer.
        """
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

    # ------------------------------------------------------------------ #
    #  Main encode                                                         #
    # ------------------------------------------------------------------ #

    def encode(self, image_path: str, message: str, password: str,
               output_path: str, bits_per_channel: int = 1) -> dict:
        """
        Encode a message into an image with encryption + self-destruct flag.
        The last 8 pixels are reserved for the integrity flag (FLAG_ALIVE).
        One wrong decryption attempt will flip the flag to FLAG_POISONED and
        overwrite all payload LSBs with random noise.
        """
        try:
            self.bits_per_channel = bits_per_channel

            img = Image.open(image_path)
            if img.mode not in ['RGB', 'RGBA']:
                img = img.convert('RGB')
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            if not self.utils.is_lossless_format(image_path):
                print("Warning: Lossy format detected. Converting to PNG.")

            # Encrypt message
            encrypted_data = self.security.encrypt_message(
                message.encode('utf-8'), password
            )

            magic    = b'STEG'
            salt     = encrypted_data['salt']
            iv       = encrypted_data['iv']
            tag      = encrypted_data['tag']
            data     = encrypted_data['encrypted_data']

            metadata  = struct.pack('>I', len(salt)) + salt
            metadata += struct.pack('>I', len(iv))   + iv
            metadata += struct.pack('>I', len(tag))  + tag

            payload  = magic
            payload += struct.pack('>I', len(metadata))
            payload += metadata
            payload += struct.pack('>I', len(data))
            payload += data

            # Capacity check (subtract 8 pixels reserved for flag)
            capacity = self.utils.calculate_capacity(image_path, bits_per_channel)
            reserved_bytes = 1   # 8 bits = 1 byte reserved for flag
            available = capacity['usable_bytes'] - reserved_bytes

            if len(payload) > available:
                raise ValueError(
                    f"Message too large! Available: {available} bytes, "
                    f"Needed: {len(payload)} bytes"
                )

            payload_bits = self.utils.bytes_to_bits(payload)

            img_array = np.array(img, dtype=np.uint8)
            height, width, channels = img_array.shape

            # Build length prefix (32 bits)
            length_bits = []
            for i in range(31, -1, -1):
                length_bits.append((len(payload) >> i) & 1)

            all_bits   = length_bits + payload_bits
            bit_idx    = 0
            total_bits = len(all_bits)

            stego_array = img_array.copy()

            # How many pixels to keep free at the end for the flag
            flag_pixel_start = (height * width) - 8

            pixel_counter = 0
            for y in range(height):
                for x in range(width):
                    if pixel_counter >= flag_pixel_start:
                        break                          # leave flag zone untouched
                    for c in range(channels):
                        if bit_idx < total_bits:
                            pixel_val = int(stego_array[y, x, c])
                            if bits_per_channel == 1:
                                pixel_val = (pixel_val & 0xFE) | all_bits[bit_idx]
                            else:
                                mask      = ~((1 << bits_per_channel) - 1) & 0xFF
                                pixel_val = pixel_val & mask
                                embed     = 0
                                for b in range(bits_per_channel):
                                    if bit_idx + b < total_bits:
                                        embed = (embed << 1) | all_bits[bit_idx + b]
                                    else:
                                        embed <<= 1
                                pixel_val = pixel_val | embed
                            pixel_val = max(0, min(255, pixel_val))
                            stego_array[y, x, c] = np.uint8(pixel_val)
                            bit_idx += bits_per_channel
                    pixel_counter += 1
                if pixel_counter >= flag_pixel_start:
                    break

            # Write ALIVE flag into the reserved zone
            stego_array = self._write_flag_bits(stego_array, FLAG_ALIVE)

            # Save as PNG
            if not output_path.lower().endswith('.png'):
                output_path = output_path.rsplit('.', 1)[0] + '.png'
                print(f"Converting output to PNG: {output_path}")

            Image.fromarray(stego_array, mode='RGB').save(output_path, 'PNG', optimize=False)

            stats = {
                'message_length': len(message),
                'payload_size':   len(payload),
                'bits_embedded':  len(all_bits),
                'capacity_used':  f"{len(payload)/available*100:.1f}%" if available > 0 else "0%",
                'output_path':    output_path
            }
            return stats

        except Exception as e:
            raise Exception(f"Encoding failed: {str(e)}")

    def encode_with_metadata(self, image_path: str, message: str, password: str,
                             output_path: str, metadata: dict = None) -> dict:
        import json
        from datetime import datetime

        if metadata is None:
            metadata = {}

        metadata.update({
            'timestamp':       datetime.now().isoformat(),
            'encoder_version': '2.1',
            'encoding_method': 'LSB-AES256-GCM-SelfDestruct'
        })

        full_message = json.dumps({'metadata': metadata, 'content': message})
        return self.encode(image_path, full_message, password, output_path)
