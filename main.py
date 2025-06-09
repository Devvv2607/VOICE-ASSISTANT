import speech_recognition as sr
import pyttsx3
import requests
import re
import time
import threading
import json
from datetime import datetime
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import sys
import os
from dotenv import load_dotenv

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

class VoiceAssistant:
    def __init__(self, mistral_api_key=None):
        """Initialize the voice assistant with all necessary components."""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.active_timers = {}
        self.timer_counter = 0
        self.mistral_api_key = mistral_api_key
        
        # Check if Mistral API key is provided
        if not self.mistral_api_key:
            print("⚠️  WARNING: No Mistral API key found in .env file or environment variables.")
            print("   General questions will use web search fallback.")
            print("   Create a .env file with: MISTRAL_API_KEY=your_key_here")
        else:
            print("✅ Mistral AI ready for intelligent responses!")
        
        # Configure TTS settings
        self.setup_tts()
        
        # Adjust microphone for ambient noise
        self.setup_microphone()
        
        print("Voice Assistant initialized successfully!")
        print("Supported commands:")
        print("- Weather: 'What's the weather in [city]?'")
        print("- Timer: 'Set a timer for [X] minutes/seconds'")
        print("- General questions: 'What is [question]?' (powered by Mistral AI)")
        print("- Exit: 'exit', 'quit', or 'stop'")
    
    def setup_tts(self):
        """Configure text-to-speech settings."""
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Try to set a female voice if available
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 180)  # Slower speech
        self.tts_engine.setProperty('volume', 0.9)
    
    def setup_microphone(self):
        """Adjust microphone for ambient noise."""
        print("Adjusting for ambient noise... Please wait.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Microphone calibrated!")
    
    def speak(self, text):
        """Convert text to speech."""
        print(f"Assistant: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self):
        """Listen for voice input and convert to text."""
        try:
            with self.microphone as source:
                print("Listening... (speak now)")
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Processing speech...")
            # Use Google's free speech recognition
            text = self.recognizer.recognize_google(audio).lower()
            print(f"You said: {text}")
            return text
        
        except sr.WaitTimeoutError:
            return "timeout"
        except sr.UnknownValueError:
            self.speak("Sorry, I couldn't understand what you said.")
            return None
        except sr.RequestError as e:
            self.speak("Sorry, there was an error with the speech recognition service.")
            print(f"Speech recognition error: {e}")
            return None
    
    def identify_intent(self, text):
        """Identify the user's intent from the transcribed text."""
        text = text.lower().strip()
        
        # Exit commands
        if any(word in text for word in ['exit', 'quit', 'stop', 'goodbye', 'bye']):
            return 'exit', {}
        
        # Weather intent
        weather_keywords = ['weather', 'temperature', 'forecast', 'hot', 'cold', 'rain', 'sunny']
        if any(keyword in text for keyword in weather_keywords):
            # Extract location
            location = self.extract_location(text)
            return 'weather', {'location': location}
        
        # Timer intent
        timer_keywords = ['timer', 'alarm', 'remind', 'countdown']
        if any(keyword in text for keyword in timer_keywords):
            duration = self.extract_duration(text)
            return 'timer', {'duration': duration}
        
        # Question intent (general knowledge)
        question_keywords = ['what', 'who', 'where', 'when', 'why', 'how', 'tell me']
        if any(keyword in text for keyword in question_keywords) or '?' in text:
            return 'question', {'query': text}
        
        # Default to question if unclear
        return 'question', {'query': text}
    
    def extract_location(self, text):
        """Extract location from weather-related text."""
        # Common patterns for location extraction
        patterns = [
            r'weather in ([a-zA-Z\s]+)',
            r'weather for ([a-zA-Z\s]+)',
            r'weather at ([a-zA-Z\s]+)',
            r'in ([a-zA-Z\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                location = match.group(1).strip()
                # Clean up common words
                location = re.sub(r'\b(the|city|of)\b', '', location).strip()
                if location:
                    return location
        
        return "current location"  # Default fallback
    
    def extract_duration(self, text):
        """Extract duration from timer-related text."""
        # Look for patterns like "5 minutes", "10 seconds", "2 hours"
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
                
                # Convert to seconds
                if 'minute' in unit or 'min' in unit:
                    return number * 60
                elif 'hour' in unit or 'hr' in unit:
                    return number * 3600
                else:  # seconds
                    return number
        
        return 60  # Default to 1 minute
    
    def get_weather(self, location):
        """Get weather information for a location using a free API."""
        try:
            # Using wttr.in - a free weather service
            url = f"http://wttr.in/{location}?format=j1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                
                temp_c = current['temp_C']
                temp_f = current['temp_F']
                desc = current['weatherDesc'][0]['value']
                humidity = current['humidity']
                
                weather_info = f"The weather in {location} is {desc} with a temperature of {temp_c} degrees Celsius or {temp_f} degrees Fahrenheit. Humidity is {humidity} percent."
                return weather_info
            else:
                return f"Sorry, I couldn't get weather information for {location}."
                
        except Exception as e:
            print(f"Weather API error: {e}")
            return "Sorry, I'm having trouble accessing weather information right now."
    
    def set_timer(self, duration):
        """Set a timer for the specified duration in seconds."""
        self.timer_counter += 1
        timer_id = self.timer_counter
        
        # Convert seconds to readable format
        if duration >= 3600:
            time_str = f"{duration // 3600} hour{'s' if duration // 3600 != 1 else ''}"
            if duration % 3600 >= 60:
                time_str += f" and {(duration % 3600) // 60} minute{'s' if (duration % 3600) // 60 != 1 else ''}"
        elif duration >= 60:
            time_str = f"{duration // 60} minute{'s' if duration // 60 != 1 else ''}"
            if duration % 60 > 0:
                time_str += f" and {duration % 60} second{'s' if duration % 60 != 1 else ''}"
        else:
            time_str = f"{duration} second{'s' if duration != 1 else ''}"
        
        self.speak(f"Timer set for {time_str}.")
        
        # Start timer in a separate thread
        def timer_thread():
            time.sleep(duration)
            if timer_id in self.active_timers:
                self.speak(f"Timer for {time_str} is complete!")
                del self.active_timers[timer_id]
        
        self.active_timers[timer_id] = threading.Thread(target=timer_thread)
        self.active_timers[timer_id].daemon = True
        self.active_timers[timer_id].start()
        
        return f"Timer set for {time_str}."
    
    def ask_mistral(self, query):
        """Ask Mistral AI a question using their API."""
        if not self.mistral_api_key:
            print("No Mistral API key available, falling back to web search...")
            return self.search_web(query)
        
        try:
            # Mistral API endpoint
            url = "https://api.mistral.ai/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.mistral_api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare the message for Mistral
            payload = {
                "model": "mistral-small-latest",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a concise voice assistant. Provide brief, direct answers unless specifically asked for details. Keep responses under 30 words when possible."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }
            
            print("Querying Mistral AI...")
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('choices') and len(data['choices']) > 0:
                    answer = data['choices'][0]['message']['content'].strip()
                    print(f"Mistral response: {answer}")
                    return answer
                else:
                    print("No response from Mistral AI")
                    return self.search_web(query)
            
            elif response.status_code == 401:
                print("Invalid Mistral API key")
                return "Sorry, there's an issue with my AI service. Let me try a different approach."
            
            elif response.status_code == 429:
                print("Mistral API rate limit exceeded")
                return "I'm getting too many requests right now. Let me try a web search instead."
            
            else:
                print(f"Mistral API error: {response.status_code}")
                return self.search_web(query)
                
        except requests.exceptions.Timeout:
            print("Mistral API timeout")
            return "The AI service is taking too long to respond. Let me try a web search."
        
        except Exception as e:
            print(f"Mistral API error: {e}")
            return self.search_web(query)
        """Search the web for general questions using DuckDuckGo."""
        try:
            # Use DuckDuckGo Instant Answer API (free)
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
                
                # Try to get a direct answer
                if data.get('Abstract'):
                    return data['Abstract']
                
                if data.get('Definition'):
                    return data['Definition']
                
                # Try related topics
                if data.get('RelatedTopics') and len(data['RelatedTopics']) > 0:
                    first_topic = data['RelatedTopics'][0]
                    if isinstance(first_topic, dict) and 'Text' in first_topic:
                        return first_topic['Text']
                
                # If no direct answer, try web scraping as fallback
                return self.fallback_search(query)
            
            else:
                return self.fallback_search(query)
                
        except Exception as e:
            print(f"Search error: {e}")
            return "Sorry, I'm having trouble searching for that information right now."
    
    def fallback_search(self, query):
        """Fallback search using web scraping (used responsibly)."""
        try:
            # Search DuckDuckGo web results
            search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for result snippets
                results = soup.find_all('a', class_='result__snippet')
                if results:
                    # Get the first meaningful result
                    snippet = results[0].get_text().strip()
                    if len(snippet) > 20:  # Ensure it's substantial
                        return snippet[:300] + "..." if len(snippet) > 300 else snippet
                
                # Alternative: look for other result containers
                results = soup.find_all('div', class_='result__snippet')
                if results:
                    snippet = results[0].get_text().strip()
                    if len(snippet) > 20:
                        return snippet[:300] + "..." if len(snippet) > 300 else snippet
            
            return "I couldn't find a good answer to that question. You might want to try asking in a different way."
            
        except Exception as e:
            print(f"Fallback search error: {e}")
            return "Sorry, I'm having trouble finding information about that right now."
    
    def answer_question(self, query):
        """Answer general questions using Mistral API."""
        print(f"Asking Mistral: {query}")
        answer = self.ask_mistral(query)
        return answer
    
    def execute_action(self, intent, params):
        """Execute actions based on identified intent."""
        if intent == 'weather':
            location = params.get('location', 'current location')
            return self.get_weather(location)
        
        elif intent == 'timer':
            duration = params.get('duration', 60)
            return self.set_timer(duration)
        
        elif intent == 'question':
            query = params.get('query', '')
            return self.answer_question(query)
        
        elif intent == 'exit':
            return "Goodbye! Have a great day!"
        
        else:
            return "I'm not sure how to help with that. Can you try asking in a different way?"
    
    def run(self):
        """Main loop for the voice assistant."""
        self.speak("Hello! I'm your voice assistant. How can I help you today?")
        
        while True:
            try:
                # Listen for user input
                user_input = self.listen()
                
                if user_input == "timeout":
                    print("No speech detected. Continuing to listen...")
                    continue
                
                if user_input is None:
                    continue
                
                # Identify intent
                intent, params = self.identify_intent(user_input)
                print(f"Intent: {intent}, Params: {params}")
                
                # Execute action
                response = self.execute_action(intent, params)
                
                # Provide voice response
                self.speak(response)
                
                # Exit if requested
                if intent == 'exit':
                    break
                    
            except KeyboardInterrupt:
                self.speak("Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                self.speak("Sorry, I encountered an error. Let me try again.")

def main():
    """Main function to run the voice assistant."""
    print("=== Free Voice Assistant with Mistral AI ===")
    print("Initializing...")
    
    # Load Mistral API key from .env file or environment variable
    mistral_api_key = os.getenv('MISTRAL_API_KEY')
    
    if not mistral_api_key:
        print("\n❌ Mistral API Key not found!")
        print("\nTo set up your API key:")
        print("1. Create a .env file in the same directory as this script")
        print("2. Add this line to the .env file:")
        print("   MISTRAL_API_KEY=your_api_key_here")
        print("3. Get your free API key from: https://console.mistral.ai/")
        print("\nAlternatively, you can set it as an environment variable:")
        print("   export MISTRAL_API_KEY='your_key_here'")
        
        # Offer to enter key temporarily
        user_key = input("\nEnter Mistral API key now (temporary, not saved): ").strip()
        if user_key:
            mistral_api_key = user_key
        else:
            print("⚠️  Running without Mistral AI - will use web search for questions.")
    else:
        print("✅ Mistral API key loaded successfully!")
    
    try:
        assistant = VoiceAssistant(mistral_api_key=mistral_api_key)
        assistant.run()
    except Exception as e:
        print(f"Failed to initialize voice assistant: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you have a microphone connected")
        print("2. Check that all required packages are installed:")
        print("   pip install speechrecognition pyaudio pyttsx3 requests beautifulsoup4 nltk python-dotenv")
        print("3. On Linux, you may need: sudo apt-get install portaudio19-dev python3-pyaudio espeak")
        print("4. Create .env file with: MISTRAL_API_KEY=your_key_here")
        print("5. Get API key from: https://console.mistral.ai/")

if __name__ == "__main__":
    main()
