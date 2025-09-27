"""
Main Jarvis AI Assistant class with advanced speech recognition and LangChain integration.
"""

import re
import json
import pickle
import os
import time
from datetime import datetime, timedelta
import pytz
import nltk
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferWindowMemory

from .config import config
from .llm import GeminiLLM
from .utils import audio_manager
from .tools import (
    CalendarTool, EmailTool, WeatherTool, 
    MusicTool, TimerTool, NewsTool
)


class AgenticJarvis:
    """LangChain-powered Jarvis AI Assistant."""
    
    def __init__(self, gemini_api_key=None):
        """Initialize the LangChain-powered Jarvis assistant."""
        self.gemini_api_key = gemini_api_key or config.gemini_api_key
        self.listening_for_wake_word = True
        self.wake_words = config.wake_words

        # Use advanced audio manager
        self.audio_manager = audio_manager

        # Setup Google Calendar
        self.calendar_service = None
        self.llm = None  # Ensure llm attribute always exists
        self.agent = None  # Ensure agent attribute always exists

        self.setup_calendar_api()

        # Configure TTS using gTTS (handled by audio manager)
        # No additional TTS setup needed

        # Test audio system
        self.test_audio_system()

        # Initialize LangChain components
        self.setup_langchain()

        # Download NLTK data if needed
        self.setup_nltk()

        self.display_capabilities()
    
    def setup_nltk(self):
        """Download required NLTK data."""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            print("Downloading required NLTK data...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
    
    def setup_calendar_api(self):
        """Setup Google Calendar API."""
        try:
            creds = None
            
            if os.path.exists(config.calendar_token_file):
                with open(config.calendar_token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if os.path.exists(config.calendar_credentials_file):
                        flow = InstalledAppFlow.from_client_secrets_file(
                            config.calendar_credentials_file, 
                            config.calendar_scopes
                        )
                        creds = flow.run_local_server(port=0)
                    else:
                        print("⚠️  Google Calendar: credentials.json not found")
                        return
                
                with open(config.calendar_token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.calendar_service = build('calendar', 'v3', credentials=creds)
            print("✅ Google Calendar: Ready")
            
        except Exception as e:
            print(f"Calendar API setup error: {e}")
            self.calendar_service = None
    
    def setup_langchain(self):
        """Initialize LangChain components."""
        try:
            # Initialize LLM
            if self.gemini_api_key:
                self.llm = GeminiLLM(api_key=self.gemini_api_key)
                print("✅ Gemini LLM: Ready")
            else:
                print("⚠️  No LLM configured - using basic responses")
                self.llm = None
            
            # Initialize tools
            self.tools = [
                CalendarTool(self.calendar_service),
                EmailTool(config.get_email_config()),
                WeatherTool(),
                MusicTool(),
                TimerTool(),
                NewsTool(config.news_api_key)
            ]
            
            # Initialize memory
            self.memory = ConversationBufferWindowMemory(
                memory_key="chat_history",
                k=10,
                return_messages=True
            )
            
            # Initialize agent if LLM is available
            if self.llm:
                self.agent = initialize_agent(
                    tools=self.tools,
                    llm=self.llm,
                    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                    memory=self.memory,
                    verbose=False,
                    max_iterations=3,
                    early_stopping_method="generate"
                )
                print("✅ LangChain Agent: Ready")
            else:
                self.agent = None
                print("⚠️  LangChain Agent: Not available without LLM")
            
        except Exception as e:
            print(f"LangChain setup error: {e}")
            self.agent = None
    
    def display_capabilities(self):
        """Display assistant capabilities."""
        print("\n" + "="*70)
        print("🤖 JARVIS - LANGCHAIN-POWERED AI ASSISTANT")
        print("="*70)
        print("🎤 Say 'Hey Jarvis' to activate!")
        print("\n🚀 ENHANCED CAPABILITIES:")
        print("📅 Smart Calendar - 'Schedule team meeting tomorrow at 3 PM'")
        print("⏰ Intelligent Timers - 'Set a 10 minute timer for my pasta'")
        print("📰 Real-time News - 'Get me the latest technology news'")
        print("🎵 Music Control - 'Play some jazz on Spotify'")
        print("📧 Email Management - 'Check my emails and send reply'")
        print("🌤️  Weather Updates - 'What's the weather like in Tokyo?'")
        print("🧠 Advanced Q&A - 'Explain blockchain with examples'")
        print("🔗 Tool Chaining - Complex multi-step tasks")
        print("💭 Context Memory - Remembers conversation context")
        print("😴 Sleep Mode - 'Sleep' or 'Standby'")
        print("❌ Exit - 'Exit' or 'Quit'")
        print("="*70)
        
        # Display configuration status
        status = config.validate_config()
        print("\n📊 CONFIGURATION STATUS:")
        print(f"🧠 LLM (Mistral): {'✅' if status['llm'] else '⚠️ '}")
        print(f"📧 Email: {'✅' if status['email'] else '⚠️ '}")
        print(f"📰 News API: {'✅' if status['news_api'] else '⚠️ '}")
        print(f"📅 Calendar: {'✅' if status['calendar_credentials'] else '⚠️ '}")
        print("="*70)
    

    def test_audio_system(self):
        """Test the audio system."""
        if self.audio_manager:
            print("✅ Audio system ready")
        else:
            print("⚠️  Audio system may have issues")
    
    def speak(self, text):
        """Convert text to speech using gTTS and display text."""
        print(f"\n🤖 Jarvis: {text}")
        print("-" * 60)
        
        # Use advanced audio manager for speech synthesis
        self.audio_manager.speak_text(text)
    
    def listen_for_wake_word(self):
        """Listen specifically for the wake word."""
        try:
            return self.audio_manager.listen_for_wake_word(self.wake_words, timeout=3.0)
        
        except Exception as e:
            print(f"⚠️  Wake word detection error: {e}")
            return False
    
    def listen(self):
        """Listen for voice input and convert to text."""
        try:
            text = self.audio_manager.listen_for_command(timeout=8.0)
            
            if text == "timeout" or text is None:
                return "timeout"
            elif text:
                return text
            else:
                self.speak("I couldn't understand that. Could you please repeat?")
                return None
        
        except Exception as e:
            print(f"⚠️  Speech recognition error: {e}")
            self.speak("There's an issue with speech recognition.")
            return None
    
    def process_with_langchain(self, user_input):
        """Process user input using LangChain agent or always fallback to Gemini LLM if no tool matches."""
        try:
            if self.agent:
                # Use LangChain agent for intelligent processing
                response = self.agent.run(input=user_input)
                return response
            else:
                # Fallback to tool matching, but always use Gemini LLM for unmatched input
                tool_response = self.basic_tool_processing(user_input, allow_llm_fallback=False)
                if tool_response is not None:
                    return tool_response
                # Always use Gemini LLM if available
                if self.llm:
                    try:
                        return self.llm._call(user_input)
                    except Exception as e:
                        return f"LLM error: {e}"
                return "I'm not sure how to help with that. Try asking about calendar, email, weather, music, timers, or news."
        except Exception as e:
            print(f"LangChain processing error: {e}")
            if self.llm:
                try:
                    return self.llm._call(user_input)
                except Exception as e2:
                    return f"LLM error: {e2}"
            return "I'm not sure how to help with that. Try asking about calendar, email, weather, music, timers, or news."
    
    def basic_tool_processing(self, user_input, allow_llm_fallback=True):
        """Basic tool processing without LangChain agent. Returns None if no tool matches and allow_llm_fallback is False."""
        user_input = user_input.lower()

        # Calendar
        if any(word in user_input for word in ['schedule', 'meeting', 'appointment', 'calendar']):
            params = self.extract_calendar_params(user_input)
            return self.tools[0]._run(json.dumps(params))

        # Email (improved intent detection)
        elif any(word in user_input for word in ['email', 'mail', 'inbox']):
            if any(word in user_input for word in ['check', 'latest', 'read', 'unread', 'new']):
                return self.tools[1]._run('check')
            else:
                return self.tools[1]._run('{}')

        # Weather
        elif any(word in user_input for word in ['weather', 'temperature', 'forecast']):
            location = self.extract_location(user_input)
            return self.tools[2]._run(location)

        # Music
        elif any(word in user_input for word in ['play', 'music', 'song']):
            params = self.extract_music_params(user_input)
            return self.tools[3]._run(json.dumps(params))

        # Timer
        elif any(word in user_input for word in ['timer', 'alarm', 'countdown']):
            return self.tools[4]._run(user_input)

        # News (improved intent detection)
        elif any(word in user_input for word in ['news', 'headlines', 'headline', 'latest news']):
            category = 'general'
            if 'tech' in user_input:
                category = 'technology'
            elif 'business' in user_input:
                category = 'business'
            return self.tools[5]._run(category)

        # Fallback: Use Gemini LLM for general questions if allowed
        if allow_llm_fallback and self.llm:
            try:
                return self.llm._call(user_input)
            except Exception as e:
                return f"LLM error: {e}"

        # If not allowed to fallback, return None
        if not allow_llm_fallback:
            return None

        return "I'm not sure how to help with that. Try asking about calendar, email, weather, music, timers, or news."
    
    def extract_calendar_params(self, text):
        """Extract calendar parameters from text."""
        params = {'title': 'Meeting', 'date': 'today', 'time': '10:00 AM'}
        
        if 'tomorrow' in text:
            params['date'] = 'tomorrow'
        
        time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))', text)
        if time_match:
            params['time'] = time_match.group(1)
        
        return params
    
    def extract_music_params(self, text):
        """Extract music parameters from text."""
        params = {'song': 'music', 'platform': 'youtube'}
        
        song_match = re.search(r'play (.+?)(?:\s+on|\s*$)', text)
        if song_match:
            params['song'] = song_match.group(1).strip()
        
        if 'spotify' in text:
            params['platform'] = 'spotify'
        elif 'apple' in text:
            params['platform'] = 'apple'
        
        return params
    
    def extract_location(self, text):
        """Extract location from text."""
        location_match = re.search(r'(?:in|for|at)\s+([a-zA-Z\s]+)', text)
        if location_match:
            return location_match.group(1).strip()
        return "current location"
    
    def process_command(self, text):
        """Process user command using LangChain."""
        if not text or text == "timeout":
            return "continue"
        
        # Handle control commands
        if any(word in text for word in ['sleep', 'standby', 'go to sleep']):
            self.speak("Going to sleep mode. Say 'Hey Jarvis' to wake me up.")
            self.listening_for_wake_word = True
            return "sleep"
        
        elif any(word in text for word in ['exit', 'quit', 'goodbye', 'bye']):
            self.speak("Goodbye! It was great assisting you today.")
            return "exit"
        
        elif any(word in text for word in ['help', 'what can you do', 'capabilities']):
            help_text = """I can help you with:
            Calendar scheduling and management
            Email checking and sending
            Weather updates for any location
            Playing music on various platforms
            Setting timers and reminders
            Getting latest news and headlines
            Answering questions and having conversations
            And much more! Just ask me naturally."""
            self.speak(help_text)
            return "continue"
        
        # Process with LangChain
        try:
            response = self.process_with_langchain(text)
            self.speak(response)
            return "continue"
        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}. Please try again."
            self.speak(error_msg)
            return "continue"
    
    def run(self):
        """Main execution loop."""
        try:
            print("\n🚀 Jarvis is now active and ready!")
            self.speak("Hello! I'm Jarvis, your LangChain-powered AI assistant. I'm ready to help you with advanced tasks!")
            
            while True:
                try:
                    if self.listening_for_wake_word:
                        # Wait for wake word
                        if self.listen_for_wake_word():
                            self.speak("Yes, how can I help you?")
                            self.listening_for_wake_word = False
                        continue
                    
                    # Listen for command
                    user_input = self.listen()
                    
                    if user_input:
                        result = self.process_command(user_input)
                        
                        if result == "exit":
                            break
                        elif result == "sleep":
                            continue
                        elif result == "continue":
                            # Ask if user needs more help
                            self.speak("Is there anything else I can help you with?")
                            
                            # Wait for response
                            response = self.listen()
                            if response and any(word in response for word in ['no', 'nothing', 'that\'s all', 'thanks']):
                                self.speak("Alright! I'll go back to listening for 'Hey Jarvis'.")
                                self.listening_for_wake_word = True
                            elif response == "timeout":
                                self.speak("I'll go back to listening for 'Hey Jarvis'.")
                                self.listening_for_wake_word = True
                    
                except KeyboardInterrupt:
                    print("\n\n👋 Keyboard interrupt detected")
                    self.speak("Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error in main loop: {e}")
                    self.speak("I encountered an error. Let me restart.")
                    time.sleep(2)
                    continue
        
        except Exception as e:
            print(f"❌ Critical error: {e}")
            self.speak("I'm experiencing technical difficulties. Please restart me.")