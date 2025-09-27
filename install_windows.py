"""
Windows-specific installation script for Jarvis AI Assistant.
This script handles PyAudio installation issues on Windows.
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
        print(f"Error output: {e.stderr}")
        return False


def install_basic_packages():
    """Install packages that don't require compilation."""
    basic_packages = [
        "SpeechRecognition==3.10.0",
        "pyttsx3==2.90", 
        "google-generativeai==0.3.2",
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "nltk==3.8.1",
        "pytz==2023.3",
        "python-dotenv==1.0.0",
        "pydantic==2.5.0",
        "typing-extensions==4.8.0"
    ]
    
    print("📦 Installing basic packages...")
    for package in basic_packages:
        if not run_command(f"pip install {package}", f"Installing {package.split('==')[0]}"):
            return False
    return True


def install_google_packages():
    """Install Google API packages."""
    google_packages = [
        "google-auth==2.17.3",
        "google-auth-oauthlib==1.0.0", 
        "google-auth-httplib2==0.2.0",
        "google-api-python-client==2.88.0"
    ]
    
    print("🔧 Installing Google API packages...")
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
        ("speech_recognition", "Speech Recognition"),
        ("pyttsx3", "Text-to-Speech"),
        ("google.generativeai", "Google Gemini AI"),
        ("requests", "HTTP Requests"),
        ("nltk", "Natural Language Toolkit")
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
        print(f"\n⚠️  Some packages failed to install: {', '.join(failed_imports)}")
        print("The assistant might have limited functionality.")
        return False
    else:
        print("\n🎉 All critical packages installed successfully!")
        return True


def main():
    """Main installation process."""
    print("=" * 70)
    print("🚀 JARVIS AI ASSISTANT - WINDOWS INSTALLER")
    print("=" * 70)
    print("This installer will set up Jarvis without PyAudio compilation issues.")
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Upgrade pip
    run_command("python -m pip install --upgrade pip", "Upgrading pip")
    
    # Install packages in order
    success = True
    success &= install_basic_packages()
    success &= install_google_packages() 
    success &= install_langchain()
    
    # Test installation
    test_success = test_installation()
    
    print("\n" + "=" * 70)
    if success and test_success:
        print("🎉 INSTALLATION COMPLETED SUCCESSFULLY!")
        print("You can now run: python main.py")
    else:
        print("⚠️  INSTALLATION COMPLETED WITH WARNINGS")
        print("Some features may not work. Check the output above for details.")
    
    print("=" * 70)
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()"""
Windows-specific installation script for Jarvis AI Assistant.
This script handles PyAudio installation issues on Windows.
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
        print(f"Error output: {e.stderr}")
        return False


def install_basic_packages():
    """Install packages that don't require compilation."""
    basic_packages = [
        "SpeechRecognition==3.10.0",
        "pyttsx3==2.90", 
        "google-generativeai==0.3.2",
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "nltk==3.8.1",
        "pytz==2023.3",
        "python-dotenv==1.0.0",
        "pydantic==2.5.0",
        "typing-extensions==4.8.0"
    ]
    
    print("📦 Installing basic packages...")
    for package in basic_packages:
        if not run_command(f"pip install {package}", f"Installing {package.split('==')[0]}"):
            return False
    return True


def install_google_packages():
    """Install Google API packages."""
    google_packages = [
        "google-auth==2.17.3",
        "google-auth-oauthlib==1.0.0", 
        "google-auth-httplib2==0.2.0",
        "google-api-python-client==2.88.0"
    ]
    
    print("🔧 Installing Google API packages...")
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
        ("speech_recognition", "Speech Recognition"),
        ("pyttsx3", "Text-to-Speech"),
        ("google.generativeai", "Google Gemini AI"),
        ("requests", "HTTP Requests"),
        ("nltk", "Natural Language Toolkit")
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
        print(f"\n⚠️  Some packages failed to install: {', '.join(failed_imports)}")
        print("The assistant might have limited functionality.")
        return False
    else:
        print("\n🎉 All critical packages installed successfully!")
        return True


def main():
    """Main installation process."""
    print("=" * 70)
    print("🚀 JARVIS AI ASSISTANT - WINDOWS INSTALLER")
    print("=" * 70)
    print("This installer will set up Jarvis without PyAudio compilation issues.")
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Upgrade pip
    run_command("python -m pip install --upgrade pip", "Upgrading pip")
    
    # Install packages in order
    success = True
    success &= install_basic_packages()
    success &= install_google_packages() 
    success &= install_langchain()
    
    # Test installation
    test_success = test_installation()
    
    print("\n" + "=" * 70)
    if success and test_success:
        print("🎉 INSTALLATION COMPLETED SUCCESSFULLY!")
        print("You can now run: python main.py")
    else:
        print("⚠️  INSTALLATION COMPLETED WITH WARNINGS")
        print("Some features may not work. Check the output above for details.")
    
    print("=" * 70)
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()