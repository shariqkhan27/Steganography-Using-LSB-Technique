"""
Advanced Steganography Encoder Module
Implements LSB encoding with encryption and security features
Fixed version - handles uint8 bounds correctly
"""

from PIL import Image
import numpy as np
import struct
from security import SecurityLayer
from utils import SteganographyUtils

class SteganographyEncoder:
    """
    High-security steganography encoder with advanced features
    """
    
    def __init__(self):
        self.security = SecurityLayer()
        self.utils = SteganographyUtils()
        self.bits_per_channel = 1  # Can be increased for higher capacity
    
    def encode(self, image_path: str, message: str, password: str, 
               output_path: str, bits_per_channel: int = 1) -> dict:
        """
        Encode a message into an image with encryption
        
        Args:
            image_path: Path to carrier image
            message: Secret message to hide
            password: Password for encryption
            output_path: Path for output stego image
            bits_per_channel: Number of LSBs to use per color channel
        
        Returns:
            Dictionary with encoding statistics
        """
        try:
            self.bits_per_channel = bits_per_channel
            
            # Load image
            img = Image.open(image_path)
            
            # Convert to RGB if necessary
            if img.mode not in ['RGB', 'RGBA']:
                img = img.convert('RGB')
            
            # Convert to RGB mode (drop alpha if exists)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Check format (PNG preferred for lossless)
            if not self.utils.is_lossless_format(image_path):
                print("Warning: Using lossy format may corrupt data. Converting to PNG.")
            
            # Encrypt the message
            encrypted_data = self.security.encrypt_message(
                message.encode('utf-8'), 
                password
            )
            
            # Prepare payload: [magic_number][data_length][metadata_lengths][salt][iv][tag][encrypted_data]
            magic = b'STEG'  # Magic identifier
            salt = encrypted_data['salt']
            iv = encrypted_data['iv']
            tag = encrypted_data['tag']
            data = encrypted_data['encrypted_data']
            
            # Create metadata
            metadata = struct.pack('>I', len(salt)) + salt
            metadata += struct.pack('>I', len(iv)) + iv
            metadata += struct.pack('>I', len(tag)) + tag
            
            # Construct final payload
            payload = magic
            payload += struct.pack('>I', len(metadata))
            payload += metadata
            payload += struct.pack('>I', len(data))
            payload += data
            
            # Check capacity
            capacity = self.utils.calculate_capacity(image_path, bits_per_channel)
            if len(payload) > capacity['usable_bytes']:
                raise ValueError(
                    f"Message too large! Capacity: {capacity['max_characters']} chars, "
                    f"Message size: {len(payload)} bytes"
                )
            
            # Convert payload to bits
            payload_bits = self.utils.bytes_to_bits(payload)
            
            # Embed data
            img_array = np.array(img, dtype=np.uint8)
            height, width, channels = img_array.shape
            
            # Embed length first (32 bits)
            length_bits = []
            payload_length = len(payload)
            for i in range(31, -1, -1):
                length_bits.append((payload_length >> i) & 1)
            
            # Combine length bits with payload bits
            all_bits = length_bits + payload_bits
            
            # Perform LSB embedding - FIXED VERSION
            bit_idx = 0
            total_bits = len(all_bits)
            
            # Use a copy of the array to avoid modification issues
            stego_array = img_array.copy()
            
            for y in range(height):
                for x in range(width):
                    for c in range(channels):
                        if bit_idx < total_bits:
                            # Get current pixel value (ensure it's int)
                            pixel_val = int(stego_array[y, x, c])
                            
                            # For 1-bit LSB (simplest and safest)
                            if bits_per_channel == 1:
                                # Clear the LSB
                                pixel_val = pixel_val & 0xFE  # Clear last bit
                                # Set the LSB to our bit
                                pixel_val = pixel_val | all_bits[bit_idx]
                                
                            else:
                                # For multiple bits per channel
                                # Create mask to clear the bits we want to use
                                mask = ~((1 << bits_per_channel) - 1) & 0xFF
                                
                                # Clear the LSBs we want to use
                                pixel_val = pixel_val & mask
                                
                                # Pack the bits we want to embed
                                embed_bits = 0
                                for b in range(bits_per_channel):
                                    if bit_idx + b < total_bits:
                                        embed_bits = (embed_bits << 1) | all_bits[bit_idx + b]
                                    else:
                                        embed_bits = embed_bits << 1  # Pad with 0
                                
                                # Embed the bits
                                pixel_val = pixel_val | embed_bits
                            
                            # Ensure value stays in uint8 range (0-255)
                            pixel_val = max(0, min(255, pixel_val))
                            
                            # Store back as uint8
                            stego_array[y, x, c] = np.uint8(pixel_val)
                            
                            bit_idx += bits_per_channel
                        else:
                            break
                    if bit_idx >= total_bits:
                        break
                if bit_idx >= total_bits:
                    break
            
            # Save as lossless PNG
            stego_img = Image.fromarray(stego_array, mode='RGB')
            
            # Always save as PNG to prevent data loss
            if not output_path.lower().endswith('.png'):
                output_path = output_path.rsplit('.', 1)[0] + '.png'
                print(f"Converting output to PNG format: {output_path}")
            
            stego_img.save(output_path, 'PNG', optimize=False)
            
            # Calculate statistics
            stats = {
                'message_length': len(message),
                'payload_size': len(payload),
                'bits_embedded': len(all_bits),
                'capacity_used': f"{len(payload)/capacity['usable_bytes']*100:.1f}%" if capacity['usable_bytes'] > 0 else "0%",
                'output_path': output_path
            }
            
            return stats
            
        except Exception as e:
            raise Exception(f"Encoding failed: {str(e)}")
    
    def encode_with_metadata(self, image_path: str, message: str, password: str,
                           output_path: str, metadata: dict = None) -> dict:
        """
        Encode message with additional metadata (filename, timestamp, etc.)
        """
        import json
        from datetime import datetime
        
        if metadata is None:
            metadata = {}
        
        metadata.update({
            'timestamp': datetime.now().isoformat(),
            'encoder_version': '2.0',
            'encoding_method': 'LSB-AES256-GCM'
        })
        
        # Prepend metadata to message
        full_message = json.dumps({
            'metadata': metadata,
            'content': message
        })
        
        return self.encode(image_path, full_message, password, output_path)