"""
Jarvis AI Assistant - Main Entry Point
A LangChain-powered voice assistant with advanced capabilities.
"""

import os
from src import config, AgenticJarvis


def print_welcome():
    """Print welcome message and setup instructions."""
    print("\n" + "="*70)
    print("🚀 JARVIS AI ASSISTANT - STRUCTURED VERSION")
    print("="*70)
    print("📁 PROJECT STRUCTURE:")
    print("├── src/")
    print("│   ├── config.py         # Configuration management")
    print("│   ├── assistant.py      # Main assistant class")
    print("│   ├── llm/              # LLM wrapper")
    print("│   └── tools/            # LangChain tools")
    print("├── main.py              # Entry point")
    print("├── requirements.txt     # Dependencies")
    print("└── .env.example         # Environment template")
    print("="*70)


def main():
    """Main function to initialize and run Jarvis."""
    print_welcome()
    print("🔧 Initializing Jarvis AI Assistant...")
    
    # Check if environment file exists
    if not os.path.exists('.env'):
        print("\n⚠️  .env file not found!")
        print("Please copy .env.example to .env and configure your API keys.")
        
        create_env = input("\nWould you like to continue with basic mode? (y/n): ").lower().strip()
        if create_env != 'y':
            print("Please set up your .env file and try again.")
            return
    
    # Get API keys from configuration
    gemini_api_key = config.gemini_api_key
    
    if not gemini_api_key:
        print("\n⚠️  GEMINI_API_KEY not found.")
        print("Advanced AI features will be limited.")
        use_basic = input("Continue with basic mode? (y/n): ").lower().strip()
        if use_basic != 'y':
            print("Please set up your .env file with API keys and try again.")
            return
    
    try:
        # Initialize and run Jarvis
        jarvis = AgenticJarvis(gemini_api_key=gemini_api_key)
        jarvis.run()
        
    except KeyboardInterrupt:
        print("\n👋 Jarvis shutdown initiated")
    except Exception as e:
        print(f"❌ Failed to start Jarvis: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()