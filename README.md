# Jarvis AI Assistant Setup Guide

A modular, LangChain-powered voice assistant with advanced capabilities.

## 🏗️ Project Structure

```
VOICE-ASSISTANT/
├── src/                    # Source code
│   ├── __init__.py        # Package initialization
│   ├── config.py          # Configuration management
│   ├── assistant.py       # Main assistant class
│   ├── llm/               # Language model wrappers
│   │   ├── __init__.py
│   │   └── gemini_llm.py # Gemini API wrapper
│   └── tools/             # LangChain tools
│       ├── __init__.py
│       ├── calendar_tool.py    # Google Calendar integration
│       ├── email_tool.py       # Email management
│       ├── weather_tool.py     # Weather information
│       ├── music_tool.py       # Music playback
│       ├── timer_tool.py       # Timer and alarms
│       └── news_tool.py        # News fetching
├── main.py                # Entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 🚀 Features

- **🎤 Voice Recognition**: Wake word detection and natural speech processing
- **🧠 LangChain Integration**: Advanced AI reasoning and tool chaining
- **📅 Calendar Management**: Schedule and manage Google Calendar events
- **📧 Email Operations**: Check inbox and send emails
- **🌤️ Weather Updates**: Real-time weather information
- **🎵 Music Control**: Play music on Spotify, YouTube, Apple Music
- **⏰ Smart Timers**: Set and manage timers with notifications
- **📰 News Fetching**: Latest headlines from multiple sources
- **💭 Context Memory**: Remembers conversation history
- **🔧 Modular Design**: Easy to extend and maintain

## 📋 Prerequisites

- Python 3.8 or higher
- Microphone and speakers
- Internet connection
- API keys (optional but recommended for full functionality)

## 🛠️ Installation

### Windows Users (Recommended) - Advanced Audio Pipeline

1. **Use the Advanced installer** (sounddevice + Whisper + gTTS):
   ```bash
   python install_advanced.py
   ```
   
   This installer sets up:
   - 🎤 **Whisper** for accurate speech recognition
   - 🔊 **gTTS** for natural text-to-speech
   - 📡 **SoundDevice** for reliable audio recording
   - 🎯 **Voice Activity Detection** for better wake word detection

### Alternative: Basic Installation

1. **Use the basic Windows installer** (handles PyAudio issues):
   ```bash
   python install_windows.py
   ```

### Manual Installation

1. **Clone or download the project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   *Note: If you encounter PyAudio compilation errors on Windows, use one of the installers above instead.*

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file with your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASSWORD=your_email_app_password
   NEWS_API_KEY=your_newsapi_key_here
   ```

4. **Google Calendar Setup (Optional)**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Calendar API
   - Create credentials (OAuth 2.0 Client ID)
   - Download `credentials.json` to project root

## 🎯 Usage

1. **Start the assistant**:
   ```bash
   python main.py
   ```

2. **Activate with wake word**:
   Say \"Hey Jarvis\" or \"Jarvis\"

3. **Example commands**:
   - \"Schedule a meeting tomorrow at 3 PM\"
   - \"What's the weather in New York?\"
   - \"Play some jazz music on Spotify\"
   - \"Set a timer for 10 minutes\"
   - \"Check my emails\"
   - \"Get me the latest tech news\"
   - \"Sleep\" (to put assistant in standby)
   - \"Exit\" (to quit)

## 🔧 Configuration

### API Keys Setup

- **Google Gemini**: Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **News API**: Get API key from [NewsAPI](https://newsapi.org/)
- **Email**: Use Gmail App Password for secure access

### Voice Settings

The assistant automatically calibrates microphone settings and selects appropriate TTS voice.

## 🏃‍♂️ Running in Basic Mode

If you don't have API keys, the assistant can still run with limited functionality:
- Basic voice recognition
- Weather information (free tier)
- Music playback (opens web browser)
- Timer functionality
- Simple news headlines

## 🛠️ Troubleshooting

### WebRTC VAD Compilation Issues

If you encounter compilation errors with `webrtcvad`, run the fix script:

```bash
python fix_webrtcvad.py
```

This replaces webrtcvad with a Python-only voice activity detection system that doesn't require Visual C++ build tools.

### Common Issues

1. **Microphone not working**:
   - Check microphone permissions
   - Ensure microphone is not muted
   - Try running as administrator

2. **Speech recognition errors**:
   - Ensure stable internet connection
   - Speak clearly and avoid background noise
   - Check microphone quality

3. **Import errors**:
   - Install all requirements: `pip install -r requirements.txt`
   - Use Python 3.8+ with pip 21.0+

4. **Google Calendar issues**:
   - Verify `credentials.json` is in project root
   - Complete OAuth consent screen setup
   - Enable Google Calendar API

## 🎨 Customization

### Adding New Tools

1. Create a new tool in `src/tools/`
2. Inherit from `BaseTool`
3. Implement `_run` method
4. Add to `src/tools/__init__.py`
5. Import in `src/assistant.py`

### Modifying Voice Settings

Edit `src/config.py` to adjust:
- TTS rate and volume
- Wake words
- Timeout settings

## 📜 License

This project is for educational and personal use.

## 🤝 Contributing

Contributions are welcome! Please ensure code follows the modular structure.

---

**Enjoy your AI assistant! 🎉**