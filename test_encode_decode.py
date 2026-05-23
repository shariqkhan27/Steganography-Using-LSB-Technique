"""
Test script to verify encoding and decoding work correctly
"""

import os
from encoder import SteganographyEncoder
from decoder import SteganographyDecoder

def test_steganography():
    """Test the complete encode/decode cycle"""
    
    print("=" * 60)
    print("STEGANOGRAPHY SYSTEM TEST")
    print("=" * 60)
    
    # Initialize
    encoder = SteganographyEncoder()
    decoder = SteganographyDecoder()
    
    # Test parameters
    test_image = "test_input.png"  # Make sure this exists
    test_message = "Hello World! This is a secret message. 🔐"
    test_password = "test123"
    output_image = "test_output.png"
    
    print(f"\n📁 Input image: {test_image}")
    print(f"📝 Message: {test_message}")
    print(f"🔑 Password: {test_password}")
    print(f"📤 Output: {output_image}")
    
    # Check if test image exists
    if not os.path.exists(test_image):
        print(f"\n❌ Error: Test image '{test_image}' not found!")
        print("Please place a PNG image named 'test_input.png' in the project folder")
        return
    
    try:
        # Encode
        print("\n" + "=" * 60)
        print("ENCODING...")
        print("=" * 60)
        
        stats = encoder.encode(test_image, test_message, test_password, output_image)
        
        print("✅ Encoding successful!")
        print(f"   Message length: {stats['message_length']} chars")
        print(f"   Payload size: {stats['payload_size']} bytes")
        print(f"   Bits embedded: {stats['bits_embedded']}")
        print(f"   Capacity used: {stats['capacity_used']}")
        
        # Check output file
        if os.path.exists(output_image):
            output_size = os.path.getsize(output_image)
            print(f"   Output file size: {output_size:,} bytes")
        else:
            print("❌ Output file was not created!")
            return
        
        # Decode with correct password
        print("\n" + "=" * 60)
        print("DECODING (correct password)...")
        print("=" * 60)
        
        result = decoder.decode(output_image, test_password)
        
        if result['success']:
            print("✅ Decoding successful!")
            print(f"   Extracted message: {result['message']}")
            print(f"   Metadata: {result.get('metadata', {})}")
            
            # Verify message
            if result['message'] == test_message:
                print("\n✅✅✅ TEST PASSED: Messages match perfectly!")
            else:
                print(f"\n❌❌❌ TEST FAILED: Messages don't match!")
                print(f"   Expected: {test_message}")
                print(f"   Got: {result['message']}")
        else:
            print(f"❌ Decoding failed: {result.get('error')}")
        
        # Decode with wrong password
        print("\n" + "=" * 60)
        print("DECODING (wrong password)...")
        print("=" * 60)
        
        result_wrong = decoder.decode(output_image, "wrongpassword")
        
        if not result_wrong['success']:
            print(f"✅ Correctly rejected wrong password: {result_wrong.get('error')}")
        else:
            print("❌ Should have rejected wrong password!")
        
        # Test capacity checker
        print("\n" + "=" * 60)
        print("CAPACITY CHECK...")
        print("=" * 60)
        
        from utils import SteganographyUtils
        utils = SteganographyUtils()
        capacity = utils.calculate_capacity(test_image)
        
        print(f"   Image: {capacity['image_size']}")
        print(f"   Max characters: {capacity['max_characters']:,}")
        print(f"   Usable bytes: {capacity['usable_bytes']:,}")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_steganography()