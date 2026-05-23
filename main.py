"""
Main entry point for the Advanced Steganography System
Supports both GUI and command-line interfaces
"""

import sys
import argparse
from gui_standard import SteganographyApp
from encoder import SteganographyEncoder
from decoder import SteganographyDecoder
from utils import SteganographyUtils

def gui_mode():
    """Launch GUI interface"""
    print("🚀 Launching Advanced Steganography System GUI...")
    app = SteganographyApp()
    app.run()

def cli_mode():
    """Command-line interface mode"""
    parser = argparse.ArgumentParser(
        description="Advanced Steganography System - Hide messages in images"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Encode command
    encode_parser = subparsers.add_parser('encode', help='Encode a message')
    encode_parser.add_argument('image', help='Carrier image path')
    encode_parser.add_argument('message', help='Message to hide')
    encode_parser.add_argument('password', help='Encryption password')
    encode_parser.add_argument('-o', '--output', default='output.png', help='Output image path')
    encode_parser.add_argument('-b', '--bits', type=int, default=1, help='Bits per channel (1-4)')
    
    # Decode command
    decode_parser = subparsers.add_parser('decode', help='Decode a message')
    decode_parser.add_argument('image', help='Stego image path')
    decode_parser.add_argument('password', help='Decryption password')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze image capacity')
    analyze_parser.add_argument('image', help='Image to analyze')
    
    # Detect command
    detect_parser = subparsers.add_parser('detect', help='Detect hidden data')
    detect_parser.add_argument('image', help='Image to check')
    
    args = parser.parse_args()
    
    if args.command == 'encode':
        encoder = SteganographyEncoder()
        try:
            print("🔒 Encoding message...")
            stats = encoder.encode(args.image, args.message, args.password, args.output, args.bits)
            print("✅ Encoding successful!")
            print(f"Message length: {stats['message_length']} characters")
            print(f"Payload size: {stats['payload_size']} bytes")
            print(f"Output saved to: {stats['output_path']}")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == 'decode':
        decoder = SteganographyDecoder()
        try:
            print("🔓 Decoding message...")
            result = decoder.decode(args.image, args.password)
            if result['success']:
                print("✅ Decoded message:")
                print("-" * 40)
                print(result['message'])
                print("-" * 40)
            else:
                print(f"❌ Error: {result['error']}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == 'analyze':
        utils = SteganographyUtils()
        try:
            capacity = utils.calculate_capacity(args.image)
            print(f"\n📊 Image Capacity Analysis for: {args.image}")
            print(f"Dimensions: {capacity['image_size']}")
            print(f"Max message size: {capacity['max_characters']:,} characters")
            print(f"Total capacity: {capacity['usable_bytes']:,} bytes")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == 'detect':
        decoder = SteganographyDecoder()
        try:
            has_data = decoder.detect_hidden_data(args.image)
            if has_data:
                print("⚠️  Hidden data detected in image!")
            else:
                print("✅ No hidden data detected.")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    else:
        # No command provided, launch GUI
        gui_mode()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_mode()
    else:
        gui_mode()