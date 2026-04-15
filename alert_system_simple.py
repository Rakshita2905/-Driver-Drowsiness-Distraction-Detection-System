"""
Simple Alert System - No Pygame Required
"""

import time
from datetime import datetime
import winsound  # For Windows beep

class AlertSystem:
    """
    Simple Alert System using Windows beep
    """
    
    def __init__(self, config):
        self.config = config
        self.last_alert_time = 0
        self.alert_cooldown = config['alerts']['cooldown_time']
        
        self.messages = {
            'drowsy': "⚠️ WARNING: You seem drowsy!",
            'microsleep': "🚨 EMERGENCY: Microsleep detected!",
            'distracted': "⚠️ Please focus on the road!"
        }
    
    def trigger_alert(self, alert_type, level=2):
        """Trigger alert"""
        current_time = time.time()
        
        if current_time - self.last_alert_time < self.alert_cooldown:
            return
        
        self.last_alert_time = current_time
        message = self.messages.get(alert_type, "Alert!")
        
        # Print alert to console
        print(f"\n{'='*50}")
        print(f"🔔 ALERT: {message}")
        print(f"{'='*50}\n")
        
        # Windows beep sound
        try:
            for _ in range(3):
                winsound.Beep(1000, 500)  # 1000Hz for 500ms
                time.sleep(0.2)
        except:
            pass
        
        # Log alert
        self.log_alert(alert_type, level, message)
    
    def log_alert(self, alert_type, level, message):
        """Log alert to file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open("logs/alerts.csv", "a") as f:
                f.write(f"{timestamp}, {alert_type}, Level: {level}, {message}\n")
        except:
            pass