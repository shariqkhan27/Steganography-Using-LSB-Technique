"""
Advanced Steganography Decoder Module
Extracts and decrypts hidden messages from images
Completely reworked for reliability
"""

from PIL import Image
import numpy as np
import struct
from security import SecurityLayer
from utils import SteganographyUtils

class SteganographyDecoder:
    """
    Advanced decoder for extracting hidden messages
    """
    
    def __init__(self):
        self.security = SecurityLayer()
        self.utils = SteganographyUtils()
    
    def decode(self, image_path: str, password: str) -> dict:
        """
        Extract and decrypt message from stego image
        
        Args:
            image_path: Path to stego image
            password: Password for decryption
            
        Returns:
            Dictionary with extracted message and metadata
        """
        try:
            # Load image
            img = Image.open(image_path)
            
            # Convert to RGB if necessary
            if img.mode not in ['RGB', 'RGBA']:
                img = img.convert('RGB')
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Convert to numpy array
            img_array = np.array(img, dtype=np.uint8)
            height, width, channels = img_array.shape
            
            print(f"Image loaded: {width}x{height}, {channels} channels")
            
            # First, extract all LSBs from the entire image
            all_bits = []
            
            for y in range(height):
                for x in range(width):
                    for c in range(channels):
                        # Extract only the LSB (1 bit per channel)
                        pixel_val = int(img_array[y, x, c])
                        bit = pixel_val & 1
                        all_bits.append(bit)
            
            print(f"Extracted {len(all_bits)} bits total")
            
            # Check if we have enough bits for at least the length header
            if len(all_bits) < 32:
                return {
                    'success': False,
                    'error': 'Image too small to contain hidden data'
                }
            
            # Convert first 32 bits to 4 bytes (length header)
            length_bytes = self._bits_to_bytes(all_bits[:32])
            
            # Unpack the length
            payload_length = struct.unpack('>I', length_bytes)[0]
            
            print(f"Payload length from header: {payload_length} bytes")
            
            # Validate payload length
            max_possible_bytes = (len(all_bits) - 32) // 8
            
            if payload_length <= 0:
                return {
                    'success': False,
                    'error': 'No hidden data found (invalid length)'
                }
            
            if payload_length > max_possible_bytes:
                return {
                    'success': False,
                    'error': f'Image doesn\'t contain enough data. Expected {payload_length} bytes but only {max_possible_bytes} available'
                }
            
            # Calculate total bits needed
            total_bits_needed = 32 + (payload_length * 8)
            
            # Check if we have enough bits
            if total_bits_needed > len(all_bits):
                return {
                    'success': False,
                    'error': 'Corrupted data: not enough bits in image'
                }
            
            # Extract the exact number of bits needed for the payload
            payload_bits = all_bits[32:total_bits_needed]
            
            # Convert bits to bytes
            payload = self._bits_to_bytes(payload_bits)
            
            print(f"Payload extracted: {len(payload)} bytes")
            
            # Now parse the payload structure
            pos = 0
            
            # Check for magic number (4 bytes)
            if len(payload) < 4:
                return {
                    'success': False,
                    'error': 'Payload too small for magic number'
                }
            
            magic = payload[pos:pos+4]
            print(f"Magic number: {magic}")
            
            if magic != b'STEG':
                return {
                    'success': False,
                    'error': 'No steganographic data found. This image may not contain hidden data or was encoded with a different tool.'
                }
            pos += 4
            
            # Get metadata length (4 bytes)
            if pos + 4 > len(payload):
                return {
                    'success': False,
                    'error': 'Corrupted data: cannot read metadata length'
                }
            
            metadata_length = struct.unpack('>I', payload[pos:pos+4])[0]
            pos += 4
            
            print(f"Metadata length: {metadata_length} bytes")
            
            # Validate metadata length
            if metadata_length < 12 or metadata_length > len(payload) - pos:
                return {
                    'success': False,
                    'error': f'Invalid metadata length: {metadata_length}'
                }
            
            # Parse metadata section
            metadata_section = payload[pos:pos+metadata_length]
            meta_pos = 0
            
            # Extract salt
            if meta_pos + 4 > len(metadata_section):
                return {
                    'success': False,
                    'error': 'Corrupted metadata: cannot read salt length'
                }
            
            salt_length = struct.unpack('>I', metadata_section[meta_pos:meta_pos+4])[0]
            meta_pos += 4
            
            # Validate salt length
            if salt_length < 8 or salt_length > 256:
                return {
                    'success': False,
                    'error': f'Invalid salt length: {salt_length}'
                }
            
            if meta_pos + salt_length > len(metadata_section):
                return {
                    'success': False,
                    'error': 'Corrupted metadata: salt extends beyond section'
                }
            
            salt = metadata_section[meta_pos:meta_pos+salt_length]
            meta_pos += salt_length
            
            # Extract IV
            if meta_pos + 4 > len(metadata_section):
                return {
                    'success': False,
                    'error': 'Corrupted metadata: cannot read IV length'
                }
            
            iv_length = struct.unpack('>I', metadata_section[meta_pos:meta_pos+4])[0]
            meta_pos += 4
            
            # Validate IV length
            if iv_length < 8 or iv_length > 256:
                return {
                    'success': False,
                    'error': f'Invalid IV length: {iv_length}'
                }
            
            if meta_pos + iv_length > len(metadata_section):
                return {
                    'success': False,
                    'error': 'Corrupted metadata: IV extends beyond section'
                }
            
            iv = metadata_section[meta_pos:meta_pos+iv_length]
            meta_pos += iv_length
            
            # Extract tag
            if meta_pos + 4 > len(metadata_section):
                return {
                    'success': False,
                    'error': 'Corrupted metadata: cannot read tag length'
                }
            
            tag_length = struct.unpack('>I', metadata_section[meta_pos:meta_pos+4])[0]
            meta_pos += 4
            
            # Validate tag length
            if tag_length < 8 or tag_length > 256:
                return {
                    'success': False,
                    'error': f'Invalid tag length: {tag_length}'
                }
            
            if meta_pos + tag_length > len(metadata_section):
                return {
                    'success': False,
                    'error': 'Corrupted metadata: tag extends beyond section'
                }
            
            tag = metadata_section[meta_pos:meta_pos+tag_length]
            
            pos += metadata_length
            
            # Get encrypted data length
            if pos + 4 > len(payload):
                return {
                    'success': False,
                    'error': 'Corrupted data: cannot read data length'
                }
            
            data_length = struct.unpack('>I', payload[pos:pos+4])[0]
            pos += 4
            
            # Validate data length
            if data_length <= 0 or pos + data_length > len(payload):
                return {
                    'success': False,
                    'error': f'Invalid data length: {data_length}'
                }
            
            encrypted_data = payload[pos:pos+data_length]
            
            print(f"Encrypted data: {len(encrypted_data)} bytes")
            print(f"Salt: {len(salt)} bytes, IV: {len(iv)} bytes, Tag: {len(tag)} bytes")
            
            # Decrypt message
            try:
                decrypted_message = self.security.decrypt_message(
                    encrypted_data, salt, iv, tag, password
                )
                print(f"Decrypted message: {len(decrypted_message)} bytes")
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Decryption failed. Wrong password or corrupted data: {str(e)}'
                }
            
            # Try to parse as JSON (for metadata support)
            import json
            try:
                message_str = decrypted_message.decode('utf-8')
                print(f"Decoded string: {message_str[:50]}...")
                
                message_json = json.loads(message_str)
                return {
                    'success': True,
                    'metadata': message_json.get('metadata', {}),
                    'message': message_json.get('content', ''),
                    'raw_message': message_str
                }
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Not JSON, just return as plain text
                try:
                    message_str = decrypted_message.decode('utf-8')
                    return {
                        'success': True,
                        'metadata': {},
                        'message': message_str,
                        'raw_message': message_str
                    }
                except:
                    return {
                        'success': False,
                        'error': 'Failed to decode message as text'
                    }
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'Decoding error: {str(e)}'
            }
    
    def _bits_to_bytes(self, bits: list) -> bytes:
        """
        Convert list of bits to bytes
        """
        if len(bits) % 8 != 0:
            # Pad with zeros if not multiple of 8
            bits = bits + [0] * (8 - (len(bits) % 8))
        
        bytes_data = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bits):
                    byte = (byte << 1) | (bits[i + j] & 1)
                else:
                    byte = (byte << 1)  # Pad with 0
            bytes_data.append(byte)
        
        return bytes(bytes_data)
    
    def detect_hidden_data(self, image_path: str) -> bool:
        """
        Detect if image contains hidden data (steganalysis)
        """
        try:
            img = Image.open(image_path)
            if img.mode not in ['RGB', 'RGBA']:
                img = img.convert('RGB')
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            img_array = np.array(img, dtype=np.uint8)
            height, width, channels = img_array.shape
            
            # Extract first 64 bits
            bits = []
            count = 0
            for y in range(min(height, 3)):
                for x in range(min(width, 30)):
                    for c in range(channels):
                        if count < 64:
                            pixel_val = int(img_array[y, x, c])
                            bits.append(pixel_val & 1)
                            count += 1
                        else:
                            break
                    if count >= 64:
                        break
                if count >= 64:
                    break
            
            if len(bits) >= 64:
                # Convert first 32 bits to get length
                length_bytes = self._bits_to_bytes(bits[:32])
                length = struct.unpack('>I', length_bytes)[0]
                
                # Check if length is reasonable
                max_bytes = (height * width * channels) // 8
                if 4 < length < max_bytes:
                    # Convert next 32 bits to check magic number
                    magic_bytes = self._bits_to_bytes(bits[32:64])
                    if magic_bytes == b'STEG':
                        return True
            
            return False
            
        except Exception as e:
            print(f"Detection error: {e}")
            return False