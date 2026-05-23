"""
Utility functions for steganography operations
Includes capacity checking, image analysis, and helper functions
"""

from PIL import Image
import numpy as np
from io import BytesIO
import struct

class SteganographyUtils:
    """Utility class for steganography operations"""
    
    @staticmethod
    def calculate_capacity(image_path: str, bits_per_channel: int = 1) -> dict:
        """
        Calculate maximum data capacity of an image
        Returns detailed capacity information
        """
        try:
            img = Image.open(image_path)
            
            # Convert to RGB if needed (for accurate channel count)
            if img.mode not in ['RGB', 'RGBA']:
                img = img.convert('RGB')
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            pixels = img.width * img.height
            channels = len(img.getbands())
            
            # Total bits available
            total_bits = pixels * channels * bits_per_channel
            total_bytes = total_bits // 8
            
            # Account for metadata overhead (salt + iv + tag + length prefix + magic)
            metadata_overhead = 32 + 16 + 32 + 4 + 4 + 4 + 4  # Approximate overhead
            usable_bytes = max(0, total_bytes - metadata_overhead)
            
            return {
                'image_size': f"{img.width}x{img.height}",
                'pixels': pixels,
                'channels': channels,
                'total_bits': total_bits,
                'total_bytes': total_bytes,
                'metadata_overhead': metadata_overhead,
                'usable_bytes': usable_bytes,
                'max_characters': usable_bytes,  # Assuming 1 byte per char
                'bits_per_channel': bits_per_channel
            }
        except Exception as e:
            raise Exception(f"Capacity calculation failed: {str(e)}")
    
    @staticmethod
    def image_difference(img1_path: str, img2_path: str) -> dict:
        """
        Analyze difference between original and stego image
        Returns statistical analysis for steganalysis resistance
        """
        try:
            img1 = Image.open(img1_path)
            img2 = Image.open(img2_path)
            
            # Convert both to same mode and size
            if img1.mode != 'RGB':
                img1 = img1.convert('RGB')
            if img2.mode != 'RGB':
                img2 = img2.convert('RGB')
            
            # Resize if dimensions differ
            if img1.size != img2.size:
                img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
            
            arr1 = np.array(img1, dtype=np.int16)
            arr2 = np.array(img2, dtype=np.int16)
            
            diff = np.abs(arr1 - arr2)
            
            return {
                'max_pixel_diff': int(np.max(diff)),
                'mean_pixel_diff': float(np.mean(diff)),
                'std_pixel_diff': float(np.std(diff)),
                'pixels_changed': int(np.sum(diff > 0)),
                'percent_changed': float(np.sum(diff > 0) / diff.size * 100)
            }
        except Exception as e:
            raise Exception(f"Image analysis failed: {str(e)}")
    
    @staticmethod
    def bytes_to_bits(data: bytes) -> list:
        """Convert bytes to list of bits"""
        bits = []
        for byte in data:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        return bits
    
    @staticmethod
    def bits_to_bytes(bits: list) -> bytes:
        """Convert list of bits to bytes"""
        bytes_data = bytearray()
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte = 0
                for j in range(8):
                    byte = (byte << 1) | (bits[i + j] & 1)
                bytes_data.append(byte)
        return bytes(bytes_data)
    
    @staticmethod
    def is_lossless_format(image_path: str) -> bool:
        """Check if image format is lossless"""
        try:
            img = Image.open(image_path)
            return img.format in ['PNG', 'BMP', 'TIFF']
        except:
            return False