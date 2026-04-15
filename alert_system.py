import pygame
import pyttsx3
import threading
import time
from datetime import datetime

class AlertSystem:
    """
    Multi-modal Alert System
    """
    
    def __init__(self, config):
        self.config = config
        try:
            pygame.mixer.init()
        except:
            print("Audio system not available")
        
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
        except:
            self.tts_engine = None
        
        self.last_alert_time = 0
        self.alert_cooldown = config['alerts']['cooldown_time']
        
        self.messages = {
            'drowsy': "Warning! You seem drowsy. Please take a break.",
            'microsleep': "EMERGENCY! Microsleep detected. Pull over immediately!",
            'distracted': "Please focus on the road!"
        }
    
    def trigger_alert(self, alert_type, level=2):
        """Trigger multi-modal alert"""
        current_time = time.time()
        
        if current_time - self.last_alert_time < self.alert_cooldown:
            return
        
        self.last_alert_time = current_time
        message = self.messages.get(alert_type, "Alert!")
        
        # Audio alert
        try:
            print('\a', end='', flush=True)
        except:
            pass
        
        # Voice alert
        if self.tts_engine and level >= 2:
            threading.Thread(target=self.trigger_voice_alert, args=(message,)).start()
        
        # Log alert
        self.log_alert(alert_type, level, message)
    
    def trigger_voice_alert(self, message):
        """Text-to-speech alert"""
        try:
            if self.tts_engine:
                self.tts_engine.say(message)
                self.tts_engine.runAndWait()
        except:
            pass
    
    def log_alert(self, alert_type, level, message):
        """Log alert to file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open("logs/alerts.csv", "a") as f:
                f.write(f"{timestamp}, {alert_type}, Level: {level}, {message}\n")
        except:
            pass