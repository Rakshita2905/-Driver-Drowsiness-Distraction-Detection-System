import csv
from datetime import datetime
import os
import json

class DataLogger:
    """
    Logs all detection data
    """
    
    def __init__(self, config):
        self.config = config
        self.log_file = config['logging']['log_file']
        self.enabled = config['logging']['enabled']
        
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'drowsiness_score', 'distraction_score', 
                    'risk_score', 'eye_status', 'distraction_type'
                ])
        
        self.session_start = datetime.now()
        self.stats = {
            'total_drowsy_events': 0,
            'total_distraction_events': 0,
            'total_frames': 0
        }
    
    def log_frame(self, drowsiness_score, distraction_score, risk_score, 
                 eye_status, distraction_type):
        """Log a single frame's data"""
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        self.stats['total_frames'] += 1
        
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, drowsiness_score, distraction_score, 
                risk_score, eye_status, distraction_type
            ])
    
    def log_event(self, event_type, severity, details):
        """Log a specific event"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        event_log = f"logs/events_{datetime.now().strftime('%Y%m%d')}.csv"
        file_exists = os.path.exists(event_log)
        
        with open(event_log, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['timestamp', 'event_type', 'severity', 'details'])
            writer.writerow([timestamp, event_type, severity, details])
        
        if 'drowsy' in event_type.lower():
            self.stats['total_drowsy_events'] += 1
        elif 'distraction' in event_type.lower():
            self.stats['total_distraction_events'] += 1
    
    def close(self):
        """Close logger and save final data"""
        report = {
            'session_start': self.session_start.strftime("%Y-%m-%d %H:%M:%S"),
            'session_end': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'statistics': self.stats
        }
        
        report_file = f"logs/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Session Report Saved: {report_file}")