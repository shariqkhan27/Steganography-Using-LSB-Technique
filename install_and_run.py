"""
Setup script for Steganography Project
Handles dependency installation and verification
"""

import subprocess
import sys
import importlib

def check_and_install():
    """Check and install required packages"""
    
    print("=" * 60)
    print("🔧 Steganography System Setup")
    print("=" * 60)
    
    # Required packages
    packages = {
        'PIL': 'Pillow',
        'numpy': 'numpy',
    }
    
    # First, upgrade pip
    print("\n📦 Upgrading pip...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ pip upgraded successfully")
    except:
        print("⚠️  Could not upgrade pip")
    
    # Install required packages
    for import_name, package_name in packages.items():
        print(f"\n📦 Checking {package_name}...")
        try:
            importlib.import_module(import_name)
            print(f"✅ {package_name} is already installed")
        except ImportError:
            print(f"📥 Installing {package_name}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
                print(f"✅ {package_name} installed successfully")
            except:
                print(f"❌ Failed to install {package_name}")
                print(f"   Try manually: pip install {package_name}")
                return False
    
    # Try to import and verify
    print("\n🔍 Verifying installations...")
    
    try:
        from PIL import Image
        print("✅ Pillow (PIL) - OK")
    except:
        print("❌ Pillow (PIL) - Failed")
        return False
    
    try:
        import numpy
        print("✅ NumPy - OK")
    except:
        print("❌ NumPy - Failed")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Setup Complete! All dependencies are ready.")
    print("=" * 60)
    print("\n🚀 To start the application, run:")
    print("   python main.py")
    print("\n📖 For command-line usage:")
    print("   python main.py --help")
    print()
    
    return True

if __name__ == "__main__":
    success = check_and_install()
    
    if success:
        # Ask if user wants to launch GUI
        try:
            response = input("Would you like to launch the GUI now? (y/n): ")
            if response.lower() == 'y':
                print("\n🚀 Launching Steganography System...")
                subprocess.run([sys.executable, 'main.py'])
        except KeyboardInterrupt:
            print("\n\n👋 Setup complete. Run 'python main.py' when ready.")