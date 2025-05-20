import threading
import logging
import queue
from typing import Dict, Any, Callable, Optional
import time

# Import speech recognition libraries conditionally to handle environments where they may not be installed
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False

class VoiceManager:
    """
    Manages voice input and output capabilities for agents
    Provides text-to-speech and speech-to-text functionality
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("voice_manager")
        self.is_running = False
        self.speech_thread = None
        self.recognition_thread = None
        self.speech_queue = queue.Queue()
        self.callback = None
        self.confidence_threshold = config.get("VOICE_CONFIDENCE_THRESHOLD", 0.7)
        self.language = config.get("VOICE_RECOGNITION_LANGUAGE", "en-US")
        
        # Check if voice libraries are available
        if not VOICE_ENABLED:
            self.logger.warning("Voice libraries not available. Voice capabilities will be disabled.")
            return
            
        # Initialize speech recognition
        try:
            self.recognizer = sr.Recognizer()
            self.logger.info("Speech recognition initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize speech recognition: {e}")
            return
            
        # Initialize text-to-speech engine
        try:
            self.engine = pyttsx3.init()
            # Configure voice properties
            self.engine.setProperty('rate', config.get("VOICE_RATE", 150))
            self.engine.setProperty('volume', config.get("VOICE_VOLUME", 1.0))
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            self.available_voices = {voice.id: voice for voice in voices}
            self.logger.info(f"Text-to-speech initialized with {len(voices)} voices")
            
            # Set default voice
            default_voice_id = config.get("AGENT_VOICE_ID")
            if default_voice_id and default_voice_id in self.available_voices:
                self.engine.setProperty('voice', self.available_voices[default_voice_id].id)
                self.logger.info(f"Set default voice to {default_voice_id}")
        except Exception as e:
            self.logger.error(f"Failed to initialize text-to-speech: {e}")
            self.engine = None
            
    def start(self, callback: Callable[[str, float], None]):
        """
        Start voice recognition and text-to-speech processing
        The callback will be called with (text, confidence) when voice input is recognized
        """
        if not VOICE_ENABLED:
            self.logger.warning("Voice capabilities are disabled")
            return False
            
        if self.is_running:
            self.logger.warning("Voice manager is already running")
            return False
            
        self.callback = callback
        self.is_running = True
        
        # Start speech output thread
        self.speech_thread = threading.Thread(target=self._speech_worker)
        self.speech_thread.daemon = True
        self.speech_thread.start()
        
        # Start speech recognition thread
        self.recognition_thread = threading.Thread(target=self._recognition_worker)
        self.recognition_thread.daemon = True
        self.recognition_thread.start()
        
        self.logger.info("Voice manager started")
        return True
        
    def stop(self):
        """
        Stop voice recognition and text-to-speech processing
        """
        if not self.is_running:
            return
            
        self.is_running = False
        
        # Wait for threads to finish
        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=2.0)
            
        if self.recognition_thread and self.recognition_thread.is_alive():
            self.recognition_thread.join(timeout=2.0)
            
        self.logger.info("Voice manager stopped")
        
    def speak(self, text: str, voice_id: str = None) -> bool:
        """
        Speak text using text-to-speech
        If voice_id is provided, use that voice, otherwise use the default voice
        """
        if not VOICE_ENABLED or not self.is_running or not self.engine:
            self.logger.warning(f"Cannot speak: {text} (voice not enabled or not running)")
            return False
            
        # Add to speech queue
        self.speech_queue.put((text, voice_id))
        return True
        
    def get_available_voices(self) -> Dict[str, str]:
        """
        Get a dictionary of available voices {id: name}
        """
        if not VOICE_ENABLED or not self.engine:
            return {}
            
        return {voice_id: voice.name for voice_id, voice in self.available_voices.items()}
        
    def _speech_worker(self):
        """
        Worker thread for text-to-speech processing
        """
        while self.is_running:
            try:
                # Get text from queue (with timeout to check is_running periodically)
                try:
                    text, voice_id = self.speech_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                    
                # Change voice if necessary
                if voice_id and voice_id in self.available_voices:
                    self.engine.setProperty('voice', self.available_voices[voice_id].id)
                    
                # Speak the text
                self.logger.debug(f"Speaking: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
                self.speech_queue.task_done()
            except Exception as e:
                self.logger.error(f"Error in speech worker: {e}")
                time.sleep(0.5)  # Avoid tight loop on error
                
    def _recognition_worker(self):
        """
        Worker thread for speech recognition
        """
        if not hasattr(self, 'recognizer'):
            self.logger.error("Speech recognition not initialized")
            return
            
        # Use microphone as audio source
        mic = sr.Microphone()
        
        with mic as source:
            # Adjust for ambient noise
            self.logger.info("Calibrating for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source)
            self.logger.info("Speech recognition ready")
            
            while self.is_running:
                try:
                    self.logger.debug("Listening for speech...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    try:
                        # Use Google's speech recognition
                        text = self.recognizer.recognize_google(audio, language=self.language)
                        confidence = 0.9  # Google doesn't provide confidence, use default
                        
                        self.logger.info(f"Recognized: {text} (confidence: {confidence})")
                        
                        # Check confidence threshold
                        if confidence >= self.confidence_threshold and self.callback:
                            self.callback(text, confidence)
                    except sr.UnknownValueError:
                        self.logger.debug("Speech not understood")
                    except sr.RequestError as e:
                        self.logger.error(f"Could not request results from Google Speech API: {e}")
                except Exception as e:
                    self.logger.error(f"Error in recognition worker: {e}")
                    time.sleep(0.5)  # Avoid tight loop on error
