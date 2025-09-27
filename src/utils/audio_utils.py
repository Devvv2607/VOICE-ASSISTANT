"""
Advanced audio utilities using sounddevice + Whisper + gTTS.
Provides high-quality voice recording, speech recognition, and text-to-speech.
"""

import sounddevice as sd
import numpy as np
import whisper
import io
import tempfile
import os
from gtts import gTTS
import pygame
import threading
import time
from typing import Optional, Tuple
from scipy import signal
import wave


class AdvancedAudioManager:
    """Advanced audio manager using Whisper + gTTS + sounddevice."""
    
    def __init__(self):
        """Initialize the advanced audio manager."""
        self.whisper_model = None
        self.sample_rate = 16000  # Whisper's preferred sample rate
        self.channels = 1  # Mono audio
        self.device_info = None
        self.vad = None
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
        # Setup components
        self.setup_audio_device()
        self.load_whisper_model()
        self.setup_vad()
    
    def setup_audio_device(self):
        """Setup audio input device and print all available devices for user selection."""
        try:
            print("Available audio input devices:")
            devices = sd.query_devices()
            for idx, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    print(f"  [{idx}] {dev['name']} (inputs: {dev['max_input_channels']})")
            # Get default input device
            self.device_info = sd.query_devices(kind='input')
            print(f"✅ Default audio device: {self.device_info['name']}")
            print(f"📊 Sample rate: {self.sample_rate} Hz")
        except Exception as e:
            print(f"⚠️  Audio device setup warning: {e}")
    
    def load_whisper_model(self, model_size="base"):
        """Load Whisper model for speech recognition."""
        try:
            print(f"🧠 Loading Whisper {model_size} model...")
            self.whisper_model = whisper.load_model(model_size)
            print("✅ Whisper model loaded successfully")
            
        except Exception as e:
            print(f"❌ Failed to load Whisper model: {e}")
            print("💡 Try installing torch: pip install torch")
    
    def setup_vad(self):
        """Setup Python-only Voice Activity Detection."""
        try:
            # Lowered VAD threshold for more sensitivity
            self.vad_threshold = 0.00005  # Lower energy threshold
            self.vad_frame_length = 0.025  # 25ms frames
            self.vad_hop_length = 0.010   # 10ms hop
            print(f"✅ Python-only Voice Activity Detection ready (threshold: {self.vad_threshold})")
        except Exception as e:
            print(f"⚠️  VAD setup warning: {e}")
    
    def record_audio(self, duration: float = 5.0, silence_threshold: float = 1.0) -> Optional[np.ndarray]:
        """Record audio with automatic silence detection."""
        try:
            print("🎤 Recording... (speak now)")
            
            # Record audio
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32
            )
            
            # Wait for recording to complete
            sd.wait()
            
            # Convert to proper format
            audio_data = audio_data.flatten()
            
            # Check if audio contains speech
            if self.has_speech(audio_data):
                print("✅ Audio recorded successfully")
                return audio_data
            else:
                print("🔇 No speech detected")
                return None
                
        except Exception as e:
            print(f"❌ Recording failed: {e}")
            return None
    
    def has_speech(self, audio_data: np.ndarray) -> bool:
        """Check if audio contains speech using Python-only methods. Prints energy for debugging."""
        try:
            # Simple energy-based detection
            energy = np.mean(audio_data ** 2)
            print(f"[DEBUG] Audio energy: {energy:.8f} (threshold: {self.vad_threshold})")
            if energy < self.vad_threshold:
                return False
            # Advanced Python-only VAD using spectral features
            zcr = np.mean(np.abs(np.diff(np.sign(audio_data))))
            fft = np.abs(np.fft.fft(audio_data))
            freqs = np.fft.fftfreq(len(fft), 1/self.sample_rate)
            spectral_centroid = np.sum(freqs[:len(freqs)//2] * fft[:len(fft)//2]) / np.sum(fft[:len(fft)//2])
            speech_indicators = 0
            if energy > self.vad_threshold:
                speech_indicators += 1
            if 0.01 < zcr < 0.3:
                speech_indicators += 1
            if 80 < abs(spectral_centroid) < 4000:
                speech_indicators += 1
            return speech_indicators >= 2
        except Exception as e:
            print(f"⚠️  Speech detection error: {e}")
            try:
                energy = np.mean(audio_data ** 2)
                print(f"[DEBUG] (fallback) Audio energy: {energy:.8f} (threshold: {self.vad_threshold})")
                return energy > self.vad_threshold
            except:
                return True  # Fallback - assume speech is present
    
    def transcribe_audio(self, audio_data: np.ndarray) -> Optional[str]:
        """Transcribe audio using Whisper."""
        if not self.whisper_model:
            return None
        
        try:
            print("🔄 Transcribing audio...")
            
            # Whisper expects audio in the range [-1, 1]
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Ensure audio is in correct range
            if np.max(np.abs(audio_data)) > 1.0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(audio_data, language="en")
            text = result["text"].strip().lower()
            
            if text:
                print(f"📝 Transcribed: {text}")
                return text
            else:
                print("🤔 No text detected")
                return None
                
        except Exception as e:
            print(f"❌ Transcription failed: {e}")
            return None
    
    def speak_text(self, text: str, lang: str = "en") -> bool:
        """Convert text to speech using gTTS and play it. Retry temp file deletion if needed."""
        try:
            print(f"🗣️  Speaking: {text}")
            tts = gTTS(text=text, lang=lang, slow=False)
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            try:
                tts.save(tmp_file.name)
                tmp_file.close()  # Ensure file is closed before playback
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            finally:
                # Retry temp file deletion up to 3 times
                for _ in range(3):
                    try:
                        os.unlink(tmp_file.name)
                        break
                    except Exception as e:
                        print(f"[WARN] Could not delete temp file: {e}")
                        time.sleep(0.2)
            print("✅ Speech playback completed")
            return True
        except Exception as e:
            print(f"❌ Speech synthesis failed: {e}")
            return False
    
    def listen_for_wake_word(self, wake_words: list, timeout: float = 3.0) -> bool:
        """Listen for wake word using Whisper."""
        try:
            print("👂 Listening for wake word...")
            
            # Record audio
            audio_data = self.record_audio(duration=timeout)
            
            if audio_data is None:
                return False
            
            # Transcribe
            text = self.transcribe_audio(audio_data)
            
            if text:
                # Check for wake words
                for wake_word in wake_words:
                    if wake_word in text:
                        print(f"🎯 Wake word detected: {wake_word}")
                        return True
            
            return False
            
        except Exception as e:
            print(f"❌ Wake word detection failed: {e}")
            return False
    
    def listen_for_command(self, timeout: float = 8.0) -> Optional[str]:
        """Listen for voice command using Whisper."""
        try:
            print("🎤 Listening for command...")
            
            # Record audio
            audio_data = self.record_audio(duration=timeout)
            
            if audio_data is None:
                return None
            
            # Transcribe
            text = self.transcribe_audio(audio_data)
            if text:
                print(f"📝 You said: {text}")
            else:
                print("🤔 No speech detected or could not transcribe.")
            return text
            
        except Exception as e:
            print(f"❌ Command listening failed: {e}")
            return None
    
    def test_audio_system(self) -> bool:
        """Test the complete audio system."""
        print("\n🧪 Testing audio system...")
        
        # Test recording
        print("1. Testing microphone (say something)...")
        audio = self.record_audio(duration=3.0)
        
        if audio is None:
            print("❌ Microphone test failed")
            return False
        
        # Test transcription
        print("2. Testing speech recognition...")
        text = self.transcribe_audio(audio)
        
        if text is None:
            print("❌ Speech recognition test failed")
            return False
        
        # Test speech synthesis
        print("3. Testing text-to-speech...")
        success = self.speak_text("Audio system test completed successfully.")
        
        if not success:
            print("❌ Text-to-speech test failed")
            return False
        
        print("✅ Audio system test passed!")
        return True


# Global audio manager instance
audio_manager = AdvancedAudioManager()