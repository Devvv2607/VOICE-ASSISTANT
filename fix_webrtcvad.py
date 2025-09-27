"""
Quick fix for webrtcvad compilation issues.
This script removes webrtcvad and installs scipy instead for Python-only VAD.
"""

import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 WEBRTCVAD COMPILATION FIX")
    print("=" * 60)
    print("This will remove webrtcvad and use Python-only VAD instead.")
    print()
    
    # Uninstall webrtcvad if it exists
    print("🗑️  Removing problematic webrtcvad...")
    subprocess.run("pip uninstall webrtcvad -y", shell=True, capture_output=True)
    
    # Install scipy for signal processing
    success = run_command("pip install scipy==1.10.1", "Installing SciPy for signal processing")
    
    # Install other required packages
    packages = [
        "numpy==1.24.3",
        "sounddevice==0.4.6"
    ]
    
    for package in packages:
        run_command(f"pip install {package}", f"Installing {package.split('==')[0]}")
    
    print("\n" + "=" * 60)
    if success:
        print("✅ WEBRTCVAD FIX COMPLETED!")
        print("Your audio system now uses Python-only voice activity detection.")
        print("No Visual C++ build tools required!")
    else:
        print("⚠️  Some issues encountered, but basic functionality should work.")
    
    print("=" * 60)
    print("\n💡 You can now continue with the installation:")
    print("   python install_advanced.py")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()