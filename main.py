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

class AgenticJarvis:
    def __init__(self, mistral_api_key=None):
        """Initialize the agentic AI voice assistant with all necessary components."""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.active_timers = {}
        self.timer_counter = 0
        self.mistral_api_key = mistral_api_key
        self.listening_for_wake_word = True
        self.wake_words = ['hey jarvis', 'jarvis', 'hey davis', 'davis']
        
        # Email configuration
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.email_imap_server = os.getenv('EMAIL_IMAP_SERVER', 'imap.gmail.com')
        self.email_smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        
        # News API configuration
        self.news_api_key = os.getenv('NEWS_API_KEY')
        
        # Google Calendar API setup
        self.calendar_service = None
        self.setup_calendar_api()
        
        # Music platforms
        self.music_platforms = {
            'spotify': 'https://open.spotify.com/search/',
            'youtube': 'https://www.youtube.com/results?search_query=',
            'apple': 'https://music.apple.com/search?term='
        }
        
        # Check API keys and configurations
        self.check_configurations()
        
        # Configure TTS settings
        self.setup_tts()
        
        # Adjust microphone for ambient noise
        self.setup_microphone()
        
        self.display_capabilities()
    
    def check_configurations(self):
        """Check which services are properly configured."""
        print("\n🔧 Checking service configurations...")
        
        if self.mistral_api_key:
            print("✅ Mistral AI: Ready")
        else:
            print("⚠️  Mistral AI: Not configured (will use web search)")
        
        if self.email_user and self.email_password:
            print("✅ Email: Ready")
        else:
            print("⚠️  Email: Not configured")
        
        if self.news_api_key:
            print("✅ News API: Ready")
        else:
            print("⚠️  News API: Will use free sources")
        
        if self.calendar_service:
            print("✅ Google Calendar: Ready")
        else:
            print("⚠️  Google Calendar: Not configured")
    
    def setup_calendar_api(self):
        """Setup Google Calendar API."""
        try:
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            creds = None
            
            # Check if token.pickle exists
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            # If there are no valid credentials, request authorization
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
                
                # Save credentials for next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            
            self.calendar_service = build('calendar', 'v3', credentials=creds)
            
        except Exception as e:
            print(f"Calendar API setup error: {e}")
            self.calendar_service = None
    
    def display_capabilities(self):
        """Display assistant capabilities."""
        print("\n" + "="*70)
        print("🤖 JARVIS - ADVANCED AGENTIC AI ASSISTANT")
        print("="*70)
        print("🎤 Say 'Hey Jarvis' to activate!")
        print("\n🚀 CAPABILITIES:")
        print("📅 Calendar Management - 'Schedule meeting tomorrow at 3 PM'")
        print("⏰ Smart Timers - 'Set timer for 10 minutes'")
        print("📰 Real-time News - 'What's the latest news?'")
        print("🎵 Music Control - 'Play [song name] on Spotify'")
        print("📧 Email Management - 'Check my latest emails'")
        print("🌤️  Weather Updates - 'Weather in New York'")
        print("🧠 Intelligent Q&A - 'Explain quantum computing'")
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
    
    def identify_intent_and_extract_params(self, text):
        """Advanced intent recognition with parameter extraction."""
        text = text.lower().strip()
        
        # Calendar intents
        calendar_keywords = ['schedule', 'meeting', 'appointment', 'calendar', 'book', 'plan', 'remind me']
        if any(keyword in text for keyword in calendar_keywords):
            return 'calendar', self.extract_calendar_params(text)
        
        # Email intents
        email_keywords = ['email', 'mail', 'check mail', 'latest mail', 'inbox', 'send email']
        if any(keyword in text for keyword in email_keywords):
            if any(word in text for word in ['send', 'compose', 'write']):
                return 'send_email', self.extract_email_params(text)
            else:
                return 'check_email', {}
        
        # Music intents
        music_keywords = ['play', 'music', 'song', 'spotify', 'youtube', 'tune']
        if any(keyword in text for keyword in music_keywords):
            return 'music', self.extract_music_params(text)
        
        # News intents
        news_keywords = ['news', 'latest news', 'headlines', 'current events', 'breaking news']
        if any(keyword in text for keyword in news_keywords):
            return 'news', self.extract_news_params(text)
        
        # Timer intents
        timer_keywords = ['timer', 'alarm', 'countdown', 'set timer']
        if any(keyword in text for keyword in timer_keywords):
            return 'timer', {'duration': self.extract_duration(text)}
        
        # Weather intents
        weather_keywords = ['weather', 'temperature', 'forecast', 'climate']
        if any(keyword in text for keyword in weather_keywords):
            return 'weather', {'location': self.extract_location(text)}
        
        # Control intents
        if any(word in text for word in ['sleep', 'standby', 'go to sleep']):
            return 'sleep', {}
        
        if any(word in text for word in ['exit', 'quit', 'stop', 'goodbye', 'bye']):
            return 'exit', {}
        
        # Default to question
        return 'question', {'query': text}
    
    def extract_calendar_params(self, text):
        """Extract calendar event parameters."""
        params = {}
        
        # Extract event title
        title_patterns = [
            r'schedule (.+?) (?:for|at|on)',
            r'book (.+?) (?:for|at|on)',
            r'meeting (?:about|for) (.+?) (?:at|on)',
            r'appointment (?:for|about) (.+?) (?:at|on)'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text)
            if match:
                params['title'] = match.group(1).strip()
                break
        else:
            params['title'] = 'Meeting'  # Default title
        
        # Extract time
        time_patterns = [
            r'at (\d{1,2}(?::\d{2})?\s*(?:am|pm))',
            r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))',
            r'at (\d{1,2})\s*(?:o\'?clock)?'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                params['time'] = match.group(1)
                break
        
        # Extract date
        if 'tomorrow' in text:
            params['date'] = 'tomorrow'
        elif 'today' in text:
            params['date'] = 'today'
        elif 'next week' in text:
            params['date'] = 'next week'
        else:
            # Try to extract specific dates
            date_pattern = r'(?:on\s+)?(\w+day|\w+\s+\d{1,2})'
            match = re.search(date_pattern, text)
            if match:
                params['date'] = match.group(1)
        
        return params
    
    def extract_email_params(self, text):
        """Extract email parameters."""
        params = {}
        
        # Extract recipient
        to_patterns = [
            r'to ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'send (?:email )?to (.+?)(?:\s+saying|\s+about|\s+with)',
        ]
        
        for pattern in to_patterns:
            match = re.search(pattern, text)
            if match:
                params['to'] = match.group(1).strip()
                break
        
        # Extract subject
        subject_patterns = [
            r'subject (.+?)(?:\s+saying|\s+message)',
            r'about (.+?)(?:\s+saying|\s+message)',
        ]
        
        for pattern in subject_patterns:
            match = re.search(pattern, text)
            if match:
                params['subject'] = match.group(1).strip()
                break
        
        return params
    
    def extract_music_params(self, text):
        """Extract music parameters."""
        params = {}
        
        # Extract song name
        song_patterns = [
            r'play (.+?)(?:\s+on|\s+from|\s*$)',
            r'song (.+?)(?:\s+on|\s+from|\s*$)',
            r'music (.+?)(?:\s+on|\s+from|\s*$)'
        ]
        
        for pattern in song_patterns:
            match = re.search(pattern, text)
            if match:
                params['song'] = match.group(1).strip()
                break
        
        # Extract platform
        if 'spotify' in text:
            params['platform'] = 'spotify'
        elif 'youtube' in text:
            params['platform'] = 'youtube'
        elif 'apple' in text:
            params['platform'] = 'apple'
        else:
            params['platform'] = 'youtube'  # Default
        
        return params
    
    def extract_news_params(self, text):
        """Extract news parameters."""
        params = {}
        
        # Extract category
        if any(word in text for word in ['tech', 'technology']):
            params['category'] = 'technology'
        elif any(word in text for word in ['business', 'finance']):
            params['category'] = 'business'
        elif any(word in text for word in ['sports']):
            params['category'] = 'sports'
        elif any(word in text for word in ['health']):
            params['category'] = 'health'
        else:
            params['category'] = 'general'
        
        return params
    
    def extract_duration(self, text):
        """Extract duration from timer text."""
        patterns = [
            r'(\d+)\s*(minute|minutes|min)',
            r'(\d+)\s*(second|seconds|sec)',
            r'(\d+)\s*(hour|hours|hr)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                number = int(match.group(1))
                unit = match.group(2)
                
                if 'minute' in unit or 'min' in unit:
                    return number * 60
                elif 'hour' in unit or 'hr' in unit:
                    return number * 3600
                else:
                    return number
        
        return 60  # Default
    
    def extract_location(self, text):
        """Extract location from weather text."""
        patterns = [
            r'weather in ([a-zA-Z\s]+)',
            r'weather for ([a-zA-Z\s]+)',
            r'temperature in ([a-zA-Z\s]+)',
            r'in ([a-zA-Z\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                location = match.group(1).strip()
                location = re.sub(r'\b(the|city|of|today|tomorrow)\b', '', location).strip()
                if location and len(location) > 1:
                    return location
        
        return "current location"
    
    # ============ AGENTIC CAPABILITIES ============
    
    def schedule_calendar_event(self, params):
        """Schedule a calendar event."""
        if not self.calendar_service:
            return "Sorry, Google Calendar is not configured. Please set up credentials.json first."
        
        try:
            
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
                event_date = datetime.now(ist)  # Default fallback
            
            # Parse time
            try:
                if time_str:
                    time_obj = datetime.strptime(time_str.upper(), '%I:%M %p').time()
                else:
                    time_obj = datetime.strptime('10:00 AM', '%I:%M %p').time()
                
                start_datetime = datetime.combine(event_date.date(), time_obj)
                end_datetime = start_datetime + timedelta(hours=1)  # 1 hour duration
                
            except ValueError:
                # Default time if parsing fails
                start_datetime = event_date.replace(hour=10, minute=0, second=0, microsecond=0)
                end_datetime = start_datetime + timedelta(hours=1)
            
            # Create event
            event = {
                'summary': title,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'UTC',
                },
                'description': f'Event created by Jarvis AI Assistant',
            }
            
            # Insert event
            event = self.calendar_service.events().insert(calendarId='primary', body=event).execute()
            
            return f"✅ Successfully scheduled '{title}' for {start_datetime.strftime('%B %d at %I:%M %p')}"
            
        except Exception as e:
            return f"Sorry, I couldn't schedule the event. Error: {str(e)}"
    
    def get_latest_emails(self):
        """Get latest emails from inbox."""
        if not self.email_user or not self.email_password:
            return "Email is not configured. Please add EMAIL_USER and EMAIL_PASSWORD to your .env file."
        
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.email_imap_server)
            mail.login(self.email_user, self.email_password)
            mail.select('inbox')
            
            # Search for recent emails
            result, data = mail.search(None, 'ALL')
            email_ids = data[0].split()
            
            if not email_ids:
                return "You have no emails in your inbox."
            
            # Get latest 3 emails
            latest_emails = []
            for email_id in email_ids[-3:]:
                result, msg_data = mail.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                
                subject = msg['subject'] or 'No Subject'
                sender = msg['from'] or 'Unknown Sender'
                date = msg['date'] or 'Unknown Date'
                
                latest_emails.append(f"From: {sender}\nSubject: {subject}\nDate: {date}")
            
            mail.close()
            mail.logout()
            
            if latest_emails:
                response = "Here are your latest emails:\n\n" + "\n\n---\n\n".join(latest_emails)
                return response
            else:
                return "No recent emails found."
            
        except Exception as e:
            return f"Sorry, I couldn't check your emails. Error: {str(e)}"
    
    def get_real_time_news(self, params):
        """Get real-time news."""
        try:
            category = params.get('category', 'general')
            
            if self.news_api_key:
                # Use NewsAPI if available
                url = f"https://newsapi.org/v2/top-headlines"
                params_dict = {
                    'apiKey': self.news_api_key,
                    'country': 'us',
                    'category': category,
                    'pageSize': 5
                }
                
                response = requests.get(url, params=params_dict, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    
                    if articles:
                        news_items = []
                        for article in articles[:3]:  # Top 3 news
                            title = article.get('title', 'No title')
                            description = article.get('description', 'No description')
                            news_items.append(f"📰 {title}\n   {description}")
                        
                        return "Here are the latest headlines:\n\n" + "\n\n".join(news_items)
                    else:
                        return "No news articles found."
                else:
                    return self.get_free_news()
            else:
                return self.get_free_news()
                
        except Exception as e:
            return f"Sorry, I couldn't fetch the news. Error: {str(e)}"
    
    def get_free_news(self):
        """Get news from free sources."""
        try:
            # Use RSS feeds or web scraping for free news
            url = "https://rss.cnn.com/rss/edition.rss"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                from xml.etree import ElementTree as ET
                root = ET.fromstring(response.content)
                
                news_items = []
                for item in root.findall('.//item')[:3]:
                    title = item.find('title').text if item.find('title') is not None else 'No title'
                    description = item.find('description').text if item.find('description') is not None else 'No description'
                    news_items.append(f"📰 {title}\n   {description[:100]}...")
                
                return "Here are the latest headlines:\n\n" + "\n\n".join(news_items)
            else:
                return "Sorry, I couldn't fetch news at the moment."
                
        except Exception as e:
            return f"Error fetching news: {str(e)}"
    
    def play_music(self, params):
        """Play music on specified platform."""
        song = params.get('song', 'music')
        platform = params.get('platform', 'youtube')
        
        try:
            if platform == 'spotify':
                url = f"{self.music_platforms['spotify']}{song.replace(' ', '%20')}"
            elif platform == 'apple':
                url = f"{self.music_platforms['apple']}{song.replace(' ', '+')}"
            else:  # Default to YouTube
                url = f"{self.music_platforms['youtube']}{song.replace(' ', '+')}"
            
            # Open in web browser
            webbrowser.open(url)
            
            return f"🎵 Opening '{song}' on {platform.title()}. Enjoy your music!"
            
        except Exception as e:
            return f"Sorry, I couldn't play the music. Error: {str(e)}"
    
    def set_smart_timer(self, duration):
        """Set a smart timer with notifications."""
        self.timer_counter += 1
        timer_id = self.timer_counter
        
        # Convert seconds to readable format
        if duration >= 3600:
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            time_str = f"{hours} hour{'s' if hours != 1 else ''}"
            if minutes > 0:
                time_str += f" and {minutes} minute{'s' if minutes != 1 else ''}"
        elif duration >= 60:
            minutes = duration // 60
            seconds = duration % 60
            time_str = f"{minutes} minute{'s' if minutes != 1 else ''}"
            if seconds > 0:
                time_str += f" and {seconds} second{'s' if seconds != 1 else ''}"
        else:
            time_str = f"{duration} second{'s' if duration != 1 else ''}"
        
        def timer_thread():
            time.sleep(duration)
            if timer_id in self.active_timers:
                # Multiple notifications
                self.speak(f"⏰ Timer complete! Your {time_str} timer is done!")
                
                # System notification (if available)
                try:
                    if platform.system() == "Windows":
                        subprocess.run(['msg', '*', f'Jarvis: Timer for {time_str} is complete!'])
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(['osascript', '-e', f'display notification "Timer for {time_str} is complete!" with title "Jarvis"'])
                    elif platform.system() == "Linux":
                        subprocess.run(['notify-send', 'Jarvis', f'Timer for {time_str} is complete!'])
                except:
                    pass  # Ignore if system notifications fail
                
                del self.active_timers[timer_id]
        
        self.active_timers[timer_id] = threading.Thread(target=timer_thread)
        self.active_timers[timer_id].daemon = True
        self.active_timers[timer_id].start()
        
        return f"⏰ Smart timer set for {time_str}. I'll notify you when it's done!"
    
    def get_weather(self, location):
        """Get weather information."""
        try:
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
                
                weather_info = f"🌤️ Weather in {location}:\n"
                weather_info += f"   Condition: {desc}\n"
                weather_info += f"   Temperature: {temp_c}°C ({temp_f}°F)\n"
                weather_info += f"   Feels like: {feels_like_c}°C\n"
                weather_info += f"   Humidity: {humidity}%\n"
                weather_info += f"   Wind: {wind_speed} km/h"
                
                return weather_info
            else:
                return f"Sorry, I couldn't get weather information for {location}."
                
        except Exception as e:
            return "Sorry, I'm having trouble accessing weather information."
    
    def ask_mistral(self, query):
        """Ask Mistral AI with enhanced prompting."""
        if not self.mistral_api_key:
            return self.search_web(query)
        
        try:
            url = "https://api.mistral.ai/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.mistral_api_key}",
                "Content-Type": "application/json"
            }
            
            system_prompt = """You are Jarvis, an advanced AI assistant. Provide accurate, helpful, and conversational responses. 
            Be concise but informative. Think step by step for complex questions. 
            If you don't know something, say so honestly."""
            
            payload = {
                "model": "mistral-small-latest",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                "max_tokens": 200,
                "temperature": 0.3
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('choices'):
                    return data['choices'][0]['message']['content'].strip()
            
            return self.search_web(query)
            
        except Exception as e:
            return self.search_web(query)
    
    def search_web(self, query):
        """Enhanced web search."""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_redirect': '1',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('Abstract') and len(data['Abstract']) > 20:
                    return data['Abstract'][:400]
                
                if data.get('Definition') and len(data['Definition']) > 20:
                    return data['Definition'][:400]
                
                if data.get('RelatedTopics'):
                    first_topic = data['RelatedTopics'][0]
                    if isinstance(first_topic, dict) and 'Text' in first_topic:
                        return first_topic['Text'][:400]
            
            return "I couldn't find a good answer to that question. Please try rephrasing."
           
        except Exception as e:
            return "I'm having trouble searching for that information right now."
   
    def send_email(self, params):
       """Send an email."""
       if not self.email_user or not self.email_password:
           return "Email is not configured. Please add EMAIL_USER and EMAIL_PASSWORD to your .env file."
       
       try:
           to_email = params.get('to')
           subject = params.get('subject', 'Message from Jarvis')
           
           if not to_email:
               return "I need an email address to send the message to."
           
           # Create message
           msg = MIMEMultipart()
           msg['From'] = self.email_user
           msg['To'] = to_email
           msg['Subject'] = subject
           
           body = "This is a message sent by Jarvis AI Assistant."
           msg.attach(MIMEText(body, 'plain'))
           
           # Send email
           server = smtplib.SMTP(self.email_smtp_server, 587)
           server.starttls()
           server.login(self.email_user, self.email_password)
           server.send_message(msg)
           server.quit()
           
           return f"✅ Email sent successfully to {to_email}"
           
       except Exception as e:
           return f"Sorry, I couldn't send the email. Error: {str(e)}"
   
    def process_command(self, text):
       """Process user command and execute appropriate action."""
       if not text or text == "timeout":
           return "continue"
       
       # Identify intent and extract parameters
       intent, params = self.identify_intent_and_extract_params(text)
       
       print(f"🎯 Intent: {intent}")
       if params:
           print(f"📋 Parameters: {params}")
       
       try:
           if intent == 'calendar':
               response = self.schedule_calendar_event(params)
           
           elif intent == 'check_email':
               response = self.get_latest_emails()
           
           elif intent == 'send_email':
               response = self.send_email(params)
           
           elif intent == 'music':
               response = self.play_music(params)
           
           elif intent == 'news':
               response = self.get_real_time_news(params)
           
           elif intent == 'timer':
               duration = params.get('duration', 60)
               response = self.set_smart_timer(duration)
           
           elif intent == 'weather':
               location = params.get('location', 'current location')
               response = self.get_weather(location)
           
           elif intent == 'sleep':
               self.speak("Going to sleep mode. Say 'Hey Jarvis' to wake me up.")
               self.listening_for_wake_word = True
               return "sleep"
           
           elif intent == 'exit':
               self.speak("Goodbye! Have a great day!")
               return "exit"
           
           elif intent == 'question':
               query = params.get('query', text)
               response = self.ask_mistral(query)
           
           else:
               response = "I'm not sure how to help with that. Could you please rephrase?"
           
           self.speak(response)
           return "continue"
           
       except Exception as e:
           error_msg = f"Sorry, I encountered an error: {str(e)}"
           self.speak(error_msg)
           return "continue"
   
    def run(self):
       """Main execution loop."""
       self.speak("Hello! I'm Jarvis, your advanced AI assistant. I'm ready to help!")
       
       while True:
           try:
               if self.listening_for_wake_word:
                   # Wake word detection mode
                   if self.listen_for_wake_word():
                       self.speak("Yes, I'm here! How can I help you?")
                       self.listening_for_wake_word = False
                   continue
               
               # Active listening mode
               user_input = self.listen()
               
               if user_input is None:
                   continue
               
               if user_input == "timeout":
                   self.speak("I didn't hear anything. Going back to wake word mode.")
                   self.listening_for_wake_word = True
                   continue
               
               # Process the command
               result = self.process_command(user_input)
               
               if result == "exit":
                   break
               elif result == "sleep":
                   continue
               
               # Brief pause before listening again
               time.sleep(1)
               
           except KeyboardInterrupt:
               self.speak("Shutting down. Goodbye!")
               break
           except Exception as e:
               print(f"Unexpected error: {e}")
               self.speak("I encountered an unexpected error. Let me restart.")
               time.sleep(2)

def main():
   """Main function to initialize and run Jarvis."""
   print("🚀 Initializing Jarvis AI Assistant...")
   
   # Get Mistral API key from environment or user input
   mistral_api_key = os.getenv('MISTRAL_API_KEY')
   
   if not mistral_api_key:
       print("\n⚠️  MISTRAL_API_KEY not found in environment variables.")
       print("Jarvis will use web search for questions.")
       print("To enable AI responses, add MISTRAL_API_KEY to your .env file.")
   
   try:
       # Initialize Jarvis
       jarvis = AgenticJarvis(mistral_api_key=mistral_api_key)
       
       print("\n✅ Jarvis initialized successfully!")
       print("🎤 Say 'Hey Jarvis' to start...")
       
       # Run the assistant
       jarvis.run()
       
   except Exception as e:
       print(f"\n❌ Failed to initialize Jarvis: {e}")
       print("Please check your configuration and try again.")

if __name__ == "__main__":
   main()
