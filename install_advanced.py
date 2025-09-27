"""
Advanced Windows installer for Jarvis AI Assistant.
This installer sets up the new audio pipeline: sounddevice + Whisper + gTTS.
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr[:500]}...")  # Limit error output
        return False


def install_torch():
    """Install PyTorch (required for Whisper)."""
    print("🔥 Installing PyTorch for Whisper...")
    torch_packages = [
        "torch",
        "torchaudio",
    ]
    
    for package in torch_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Failed to install {package}, trying with --index-url...")
            # Try with PyTorch index
            cmd = f"pip install {package} --index-url https://download.pytorch.org/whl/cpu"
            if not run_command(cmd, f"Installing {package} with PyTorch index"):
                print(f"⚠️  {package} installation failed, continuing...")
    return True


def install_audio_packages():
    """Install advanced audio packages."""
    audio_packages = [
        "openai-whisper==20231117",
        "sounddevice==0.4.6",
        "numpy==1.24.3",
        "gtts==2.4.0",
        "pygame==2.5.2",
        "scipy==1.10.1"
    ]
    
    print("🎤 Installing advanced audio packages...")
    for package in audio_packages:
        if not run_command(f"pip install {package}", f"Installing {package.split('==')[0]}"):
            print(f"⚠️  Failed to install {package}, continuing...")
    return True


def install_ai_packages():
    """Install AI and core packages."""
    ai_packages = [
        "google-generativeai==0.3.2",
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "nltk==3.8.1",
        "pytz==2023.3",
        "python-dotenv==1.0.0",
        "pydantic==2.5.0",
        "typing-extensions==4.8.0"
    ]
    
    print("🧠 Installing AI and core packages...")
    for package in ai_packages:
        if not run_command(f"pip install {package}", f"Installing {package.split('==')[0]}"):
            print(f"⚠️  Failed to install {package}, continuing...")
    return True


def install_google_packages():
    """Install Google API packages."""
    google_packages = [
        "google-auth==2.17.3",
        "google-auth-oauthlib==1.0.0", 
        "google-auth-httplib2==0.2.0",
        "google-api-python-client==2.88.0"
    ]
    
    print("📅 Installing Google API packages...")
    for package in google_packages:
        if not run_command(f"pip install {package}", f"Installing {package.split('==')[0]}"):
            print(f"⚠️  Failed to install {package}, continuing...")
    return True


def install_langchain():
    """Install LangChain packages."""
    langchain_packages = [
        "langchain==0.1.0",
        "langchain-community==0.0.10"
    ]
    
    print("🦜 Installing LangChain packages...")
    for package in langchain_packages:
        if not run_command(f"pip install {package}", f"Installing {package.split('==')[0]}"):
            print(f"⚠️  Failed to install {package}, continuing...")
    return True


def test_installation():
    """Test if critical packages can be imported."""
    print("🧪 Testing installation...")
    
    test_imports = [
        ("whisper", "OpenAI Whisper"),
        ("sounddevice", "SoundDevice"),
        ("gtts", "Google Text-to-Speech"),
        ("pygame", "Pygame Audio"),
        ("google.generativeai", "Google Gemini AI"),
        ("requests", "HTTP Requests"),
        ("nltk", "Natural Language Toolkit"),
        ("numpy", "NumPy"),
        ("scipy", "SciPy")
    ]
    
    failed_imports = []
    
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} - OK")
        except ImportError as e:
            print(f"❌ {name} - FAILED: {e}")
            failed_imports.append(name)
    
    if failed_imports:
        print(f"\\n⚠️  Some packages failed to install: {', '.join(failed_imports)}")
        print("The assistant might have limited functionality.")
        print("\\n💡 Common fixes:")
        print("   - Try running: pip install torch torchaudio")
        print("   - Ensure you have a stable internet connection")
        print("   - Try running the installer as administrator")
        return False
    else:
        print("\\n🎉 All critical packages installed successfully!")
        return True


def test_audio_system():
    """Test the audio system quickly."""
    print("\\n🎵 Testing audio system...")
    try:
        import sounddevice as sd
        import numpy as np
        
        # Test audio device query
        devices = sd.query_devices()
        print(f"✅ Found {len(devices)} audio devices")
        
        # Test basic numpy operations
        test_audio = np.random.randn(1000).astype(np.float32)
        print("✅ NumPy audio processing - OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Audio system test failed: {e}")
        return False


def download_whisper_model():
    """Pre-download Whisper model."""
    print("\\n🤖 Pre-downloading Whisper base model...")
    try:
        import whisper
        model = whisper.load_model("base")
        print("✅ Whisper base model downloaded successfully")
        return True
    except Exception as e:
        print(f"⚠️  Whisper model download failed: {e}")
        print("   The model will be downloaded automatically on first use.")
        return False


def main():
    """Main installation process."""
    print("=" * 70)
    print("🚀 JARVIS AI ASSISTANT - ADVANCED AUDIO INSTALLER")
    print("=" * 70)
    print("🎤 This installer sets up: sounddevice + Whisper + gTTS")
    print("🚫 No PyAudio compilation required!")
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Upgrade pip
    run_command("python -m pip install --upgrade pip", "Upgrading pip")
    
    # Install packages in order
    print("\\n📦 Starting installation process...")
    success = True
    
    # Install PyTorch first (required for Whisper)
    success &= install_torch()
    
    # Install audio packages
    success &= install_audio_packages()
    
    # Install AI packages
    success &= install_ai_packages()
    
    # Install Google packages
    success &= install_google_packages()
    
    # Install LangChain
    success &= install_langchain()
    
    # Test installation
    test_success = test_installation()
    
    # Test audio system
    audio_success = test_audio_system()
    
    # Download Whisper model
    whisper_success = download_whisper_model()
    
    print("\\n" + "=" * 70)
    if success and test_success:
        print("🎉 INSTALLATION COMPLETED SUCCESSFULLY!")
        print()
        print("🎤 NEW AUDIO PIPELINE READY:")
        print("   • Whisper for speech recognition")
        print("   • gTTS for text-to-speech")
        print("   • SoundDevice for audio recording")
        print("   • Advanced voice activity detection")
        print()
        print("🚀 You can now run: python main.py")
        
        if audio_success:
            print("✅ Audio system test passed")
        if whisper_success:
            print("✅ Whisper model ready")
        
    else:
        print("⚠️  INSTALLATION COMPLETED WITH WARNINGS")
        print("Some features may not work. Check the output above for details.")
        print()
        print("🔧 Troubleshooting:")
        print("   1. Try running as administrator")
        print("   2. Check your internet connection")
        print("   3. Update Python: pip install --upgrade pip setuptools wheel")
    
    print("=" * 70)
    
    input("\\nPress Enter to exit...")


if __name__ == "__main__":
    main()