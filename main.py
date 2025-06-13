import speech_recognition as sr
import pyttsx3
import requests
import re
import time
import threading
import json
import webbrowser
import subprocess
import platform
from datetime import datetime, timedelta
import pytz
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import sys
import os
from dotenv import load_dotenv
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import calendar
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# LangChain imports
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.llms.base import LLM
from langchain.schema import LLMResult, Generation
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.utilities import SerpAPIWrapper
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading required NLTK data...")
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

class MistralLLM(LLM):
    """Custom Mistral LLM wrapper for LangChain."""
    
    api_key: str
    model_name: str = "mistral-small-latest"
    max_tokens: int = 500
    temperature: float = 0.3
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call the Mistral API."""
        try:
            url = "https://api.mistral.ai/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('choices'):
                    return data['choices'][0]['message']['content'].strip()
            
            return "Error: Unable to get response from Mistral API"
            
        except Exception as e:
            return f"Error calling Mistral API: {str(e)}"
    
    @property
    def _llm_type(self) -> str:
        return "mistral"

class CalendarTool(BaseTool):
    """LangChain tool for calendar operations."""
    
    name = "calendar_scheduler"
    description = "Schedule calendar events. Input should be JSON with title, date, and time."
    calendar_service = None
    
    def __init__(self, calendar_service):
        super().__init__()
        self.calendar_service = calendar_service
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Schedule a calendar event."""
        try:
            # Parse the query as JSON
            params = json.loads(query) if query.startswith('{') else {'title': query}
            
            if not self.calendar_service:
                return "Google Calendar is not configured."
            
            ist = pytz.timezone('Asia/Kolkata')
            title = params.get('title', 'New Event')
            date_str = params.get('date', 'today')
            time_str = params.get('time', '10:00 AM')
            
            # Calculate event datetime
            if date_str == 'today':
                event_date = datetime.now(ist)
            elif date_str == 'tomorrow':
                event_date = datetime.now(ist) + timedelta(days=1)
            else:
                event_date = datetime.now(ist)
            
            # Parse time
            try:
                time_obj = datetime.strptime(time_str.upper(), '%I:%M %p').time()
                start_datetime = datetime.combine(event_date.date(), time_obj)
                end_datetime = start_datetime + timedelta(hours=1)
            except ValueError:
                start_datetime = event_date.replace(hour=10, minute=0, second=0, microsecond=0)
                end_datetime = start_datetime + timedelta(hours=1)
            
            # Create event
            event = {
                'summary': title,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'description': 'Event created by Jarvis AI Assistant',
            }
            
            event = self.calendar_service.events().insert(calendarId='primary', body=event).execute()
            return f"Successfully scheduled '{title}' for {start_datetime.strftime('%B %d at %I:%M %p')}"
            
        except Exception as e:
            return f"Error scheduling event: {str(e)}"

class EmailTool(BaseTool):
    """LangChain tool for email operations."""
    
    name = "email_manager"
    description = "Check latest emails or send emails. Use 'check' to get latest emails or JSON with 'to', 'subject' to send."
    
    def __init__(self, email_config):
        super().__init__()
        self.email_user = email_config.get('user')
        self.email_password = email_config.get('password')
        self.email_imap_server = email_config.get('imap_server', 'imap.gmail.com')
        self.email_smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Handle email operations."""
        if not self.email_user or not self.email_password:
            return "Email is not configured."
        
        try:
            if query.lower() == 'check':
                return self._check_emails()
            else:
                # Try to parse as JSON for sending email
                params = json.loads(query) if query.startswith('{') else {}
                return self._send_email(params)
        except Exception as e:
            return f"Email operation failed: {str(e)}"
    
    def _check_emails(self):
        """Check latest emails."""
        try:
            mail = imaplib.IMAP4_SSL(self.email_imap_server)
            mail.login(self.email_user, self.email_password)
            mail.select('inbox')
            
            result, data = mail.search(None, 'ALL')
            email_ids = data[0].split()
            
            if not email_ids:
                return "No emails in inbox."
            
            latest_emails = []
            for email_id in email_ids[-3:]:
                result, msg_data = mail.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                
                subject = msg['subject'] or 'No Subject'
                sender = msg['from'] or 'Unknown Sender'
                date = msg['date'] or 'Unknown Date'
                
                latest_emails.append(f"From: {sender}\nSubject: {subject}")
            
            mail.close()
            mail.logout()
            
            return "Latest emails:\n" + "\n---\n".join(latest_emails)
            
        except Exception as e:
            return f"Error checking emails: {str(e)}"
    
    def _send_email(self, params):
        """Send an email."""
        try:
            to_email = params.get('to')
            subject = params.get('subject', 'Message from Jarvis')
            body = params.get('body', 'This is a message sent by Jarvis AI Assistant.')
            
            if not to_email:
                return "Need email address to send message."
            
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_smtp_server, 587)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            return f"Email sent successfully to {to_email}"
            
        except Exception as e:
            return f"Error sending email: {str(e)}"

class WeatherTool(BaseTool):
    """LangChain tool for weather information."""
    
    name = "weather_checker"
    description = "Get weather information for a location. Input should be the location name."
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Get weather information."""
        try:
            location = query.strip() or "current location"
            url = f"http://wttr.in/{location}?format=j1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                
                temp_c = current['temp_C']
                temp_f = current['temp_F']
                desc = current['weatherDesc'][0]['value']
                humidity = current['humidity']
                feels_like_c = current['FeelsLikeC']
                wind_speed = current['windspeedKmph']
                
                return f"Weather in {location}: {desc}, {temp_c}°C ({temp_f}°F), feels like {feels_like_c}°C, humidity {humidity}%, wind {wind_speed} km/h"
            else:
                return f"Could not get weather for {location}"
                
        except Exception as e:
            return f"Weather check failed: {str(e)}"

class MusicTool(BaseTool):
    """LangChain tool for music operations."""
    
    name = "music_player"
    description = "Play music on various platforms. Input should be JSON with 'song' and 'platform' (spotify/youtube/apple)."
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Play music."""
        try:
            if query.startswith('{'):
                params = json.loads(query)
                song = params.get('song', 'music')
                platform = params.get('platform', 'youtube')
            else:
                song = query
                platform = 'youtube'
            
            music_platforms = {
                'spotify': f'https://open.spotify.com/search/{song.replace(" ", "%20")}',
                'youtube': f'https://www.youtube.com/results?search_query={song.replace(" ", "+")}',
                'apple': f'https://music.apple.com/search?term={song.replace(" ", "+")}'
            }
            
            url = music_platforms.get(platform, music_platforms['youtube'])
            webbrowser.open(url)
            
            return f"Opening '{song}' on {platform.title()}"
            
        except Exception as e:
            return f"Music playback failed: {str(e)}"

class TimerTool(BaseTool):
    """LangChain tool for timer operations."""
    
    name = "timer_manager"
    description = "Set timers. Input should be duration in seconds or descriptive text like '5 minutes'."
    
    def __init__(self):
        super().__init__()
        self.active_timers = {}
        self.timer_counter = 0
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Set a timer."""
        try:
            duration = self._parse_duration(query)
            self.timer_counter += 1
            timer_id = self.timer_counter
            
            # Format time string
            time_str = self._format_duration(duration)
            
            def timer_thread():
                time.sleep(duration)
                if timer_id in self.active_timers:
                    print(f"\n⏰ TIMER COMPLETE! Your {time_str} timer is done!")
                    # System notification
                    try:
                        if platform.system() == "Windows":
                            subprocess.run(['msg', '*', f'Jarvis: Timer for {time_str} complete!'])
                        elif platform.system() == "Darwin":
                            subprocess.run(['osascript', '-e', f'display notification "Timer complete!" with title "Jarvis - {time_str}"'])
                        elif platform.system() == "Linux":
                            subprocess.run(['notify-send', 'Jarvis Timer', f'{time_str} complete!'])
                    except:
                        pass
                    del self.active_timers[timer_id]
            
            self.active_timers[timer_id] = threading.Thread(target=timer_thread)
            self.active_timers[timer_id].daemon = True
            self.active_timers[timer_id].start()
            
            return f"Timer set for {time_str}. I'll notify you when it's done!"
            
        except Exception as e:
            return f"Timer setup failed: {str(e)}"
    
    def _parse_duration(self, text):
        """Parse duration from text."""
        patterns = [
            (r'(\d+)\s*(?:minutes?|mins?)', lambda x: int(x) * 60),
            (r'(\d+)\s*(?:seconds?|secs?)', lambda x: int(x)),
            (r'(\d+)\s*(?:hours?|hrs?)', lambda x: int(x) * 3600),
        ]
        
        for pattern, converter in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return converter(match.group(1))
        
        # Try to extract just numbers
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0]) * 60  # Default to minutes
        
        return 60  # Default 1 minute
    
    def _format_duration(self, duration):
        """Format duration as readable string."""
        if duration >= 3600:
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            return f"{hours} hour{'s' if hours != 1 else ''}" + (f" {minutes} min" if minutes else "")
        elif duration >= 60:
            minutes = duration // 60
            seconds = duration % 60
            return f"{minutes} minute{'s' if minutes != 1 else ''}" + (f" {seconds} sec" if seconds else "")
        else:
            return f"{duration} second{'s' if duration != 1 else ''}"

class NewsTool(BaseTool):
    """LangChain tool for news information."""
    
    name = "news_fetcher"
    description = "Get latest news. Input can be 'general', 'technology', 'business', 'sports', or 'health'."
    
    def __init__(self, news_api_key=None):
        super().__init__()
        self.news_api_key = news_api_key
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Get news information."""
        try:
            category = query.lower().strip() if query else 'general'
            
            if self.news_api_key:
                return self._get_news_api(category)
            else:
                return self._get_free_news()
                
        except Exception as e:
            return f"News fetch failed: {str(e)}"
    
    def _get_news_api(self, category):
        """Get news from NewsAPI."""
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'apiKey': self.news_api_key,
                'country': 'us',
                'category': category,
                'pageSize': 3
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if articles:
                    news_items = []
                    for article in articles:
                        title = article.get('title', 'No title')
                        description = article.get('description', 'No description')[:100]
                        news_items.append(f"{title}\n{description}...")
                    
                    return "Latest headlines:\n" + "\n---\n".join(news_items)
            
            return self._get_free_news()
            
        except Exception:
            return self._get_free_news()
    
    def _get_free_news(self):
        """Get news from free sources."""
        try:
            url = "https://rss.cnn.com/rss/edition.rss"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                from xml.etree import ElementTree as ET
                root = ET.fromstring(response.content)
                
                news_items = []
                for item in root.findall('.//item')[:3]:
                    title = item.find('title').text if item.find('title') is not None else 'No title'
                    news_items.append(title)
                
                return "Latest headlines:\n" + "\n".join(news_items)
            
            return "Unable to fetch news at the moment."
            
        except Exception as e:
            return f"News unavailable: {str(e)}"

class AgenticJarvis:
    def __init__(self, mistral_api_key=None):
        """Initialize the LangChain-powered Jarvis assistant."""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.mistral_api_key = mistral_api_key
        self.listening_for_wake_word = True
        self.wake_words = ['hey jarvis', 'jarvis', 'hey davis', 'davis']
        
        # Load configurations
        self.email_config = {
            'user': os.getenv('EMAIL_USER'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'imap_server': os.getenv('EMAIL_IMAP_SERVER', 'imap.gmail.com'),
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        }
        self.news_api_key = os.getenv('NEWS_API_KEY')
        
        # Setup Google Calendar
        self.calendar_service = None
        self.setup_calendar_api()
        
        # Configure TTS and microphone
        self.setup_tts()
        self.setup_microphone()
        
        # Initialize LangChain components
        self.setup_langchain()
        
        self.display_capabilities()
    
    def setup_calendar_api(self):
        """Setup Google Calendar API."""
        try:
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            creds = None
            
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if os.path.exists('credentials.json'):
                        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                        creds = flow.run_local_server(port=0)
                    else:
                        print("⚠️  Google Calendar: credentials.json not found")
                        return
                
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            
            self.calendar_service = build('calendar', 'v3', credentials=creds)
            
        except Exception as e:
            print(f"Calendar API setup error: {e}")
            self.calendar_service = None
    
    def setup_langchain(self):
        """Initialize LangChain components."""
        try:
            # Initialize LLM
            if self.mistral_api_key:
                self.llm = MistralLLM(api_key=self.mistral_api_key)
                print("✅ Mistral LLM: Ready")
            else:
                print("⚠️  No LLM configured - using basic responses")
                self.llm = None
            
            # Initialize tools
            self.tools = [
                CalendarTool(self.calendar_service),
                EmailTool(self.email_config),
                WeatherTool(),
                MusicTool(),
                TimerTool(),
                NewsTool(self.news_api_key)
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
    
    def setup_tts(self):
        """Configure text-to-speech settings."""
        voices = self.tts_engine.getProperty('voices')
        if voices:
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            else:
                self.tts_engine.setProperty('voice', voices[0].id)
        
        self.tts_engine.setProperty('rate', 180)
        self.tts_engine.setProperty('volume', 0.9)
    
    def setup_microphone(self):
        """Adjust microphone for ambient noise."""
        print("🎙️  Calibrating microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("✅ Microphone ready!")
    
    def speak(self, text):
        """Convert text to speech and display text."""
        print(f"\n🤖 Jarvis: {text}")
        print("-" * 60)
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen_for_wake_word(self):
        """Listen specifically for the wake word."""
        try:
            with self.microphone as source:
                print("👂 Listening for 'Hey Jarvis'...")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
            
            text = self.recognizer.recognize_google(audio).lower()
            print(f"🎯 Heard: {text}")
            
            for wake_word in self.wake_words:
                if wake_word in text:
                    return True
            return False
        
        except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
            return False
    
    def listen(self):
        """Listen for voice input and convert to text."""
        try:
            with self.microphone as source:
                print("🎤 I'm listening...")
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=12)
            
            print("🔄 Processing speech...")
            text = self.recognizer.recognize_google(audio).lower()
            print(f"📝 You said: {text}")
            return text
        
        except sr.WaitTimeoutError:
            return "timeout"
        except sr.UnknownValueError:
            self.speak("I couldn't understand that. Could you please repeat?")
            return None
        except sr.RequestError as e:
            self.speak("There's an issue with speech recognition.")
            return None
    
    def process_with_langchain(self, user_input):
        """Process user input using LangChain agent."""
        try:
            if self.agent:
                # Use LangChain agent for intelligent processing
                response = self.agent.run(input=user_input)
                return response
            else:
                # Fallback to basic tool matching
                return self.basic_tool_processing(user_input)
                
        except Exception as e:
            print(f"LangChain processing error: {e}")
            return self.basic_tool_processing(user_input)
    
    def basic_tool_processing(self, user_input):
        """Basic tool processing without LangChain agent."""
        user_input = user_input.lower()
        
        # Calendar
        if any(word in user_input for word in ['schedule', 'meeting', 'appointment', 'calendar']):
            params = self.extract_calendar_params(user_input)
            return self.tools[0]._run(json.dumps(params))
        
        # Email
        elif any(word in user_input for word in ['email', 'mail', 'inbox']):
            if 'check' in user_input:
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
        
        # News
        elif any(word in user_input for word in ['news', 'headlines']):
            category = 'general'
            if 'tech' in user_input:
                category = 'technology'
            elif 'business' in user_input:
                category = 'business'
            return self.tools[5]._run(category)
        
        else:
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
            self.speak("Going to sleep mode. Say 'Hey Jarvis  to wake me up.")
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

def main():
    """Main function to initialize and run Jarvis."""
    print("🔧 Initializing Jarvis AI Assistant...")
    
    # Get API keys from environment or prompt user
    mistral_api_key = os.getenv('MISTRAL_API_KEY')
    
    if not mistral_api_key:
        print("\n⚠️  MISTRAL_API_KEY not found in environment variables.")
        print("You can still use basic functionality, but advanced AI features will be limited.")
        use_basic = input("Continue with basic mode? (y/n): ").lower().strip()
        if use_basic != 'y':
            print("Please set up your .env file with API keys and try again.")
            return
    
    try:
        # Initialize Jarvis
        jarvis = AgenticJarvis(mistral_api_key=mistral_api_key)
        
        # Run the assistant
        jarvis.run()
        
    except KeyboardInterrupt:
        print("\n👋 Jarvis shutdown initiated")
    except Exception as e:
        print(f"❌ Failed to start Jarvis: {e}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()
