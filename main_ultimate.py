"""
Driver Drowsiness Detection System - ULTIMATE VERSION
Features: Drowsiness + Yawn + Head Pose + Blink Rate + Voice Alerts + Recording
"""

import cv2
import numpy as np
import time
from datetime import datetime
import winsound
import os
import threading
from collections import deque

# Try to import optional features
try:
    import pyttsx3  # For voice alerts
    VOICE_AVAILABLE = True
except:
    VOICE_AVAILABLE = False
    print("⚠️  pyttsx3 not installed. Voice alerts disabled.")
    print("   Install with: pip install pyttsx3")

class AdvancedDrowsinessDetector:
    def __init__(self):
        # Load detectors
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        self.eye_cascade_tree = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml'
        )
        
        # ========== ADJUSTABLE SETTINGS ==========
        self.EYE_CLOSED_THRESHOLD = 5      # Frames for drowsiness
        self.YAWN_THRESHOLD = 8            # Mouth aspect ratio threshold
        self.BLINK_RATE_WINDOW = 60        # Frames for blink rate (2 seconds at 30fps)
        self.HEAD_POSE_THRESHOLD = 15      # Degrees for looking away
        # ========================================
        
        # State variables
        self.eye_closed_counter = 0
        self.drowsy_events = 0
        self.yawn_counter = 0
        self.yawn_events = 0
        self.looking_away_counter = 0
        self.looking_away_events = 0
        
        # Blink rate tracking
        self.blinks = deque(maxlen=self.BLINK_RATE_WINDOW)
        self.last_ear = 0.3
        self.blink_count = 0
        
        # Alert cooldown
        self.last_alert_time = 0
        self.last_voice_alert_time = 0
        self.alert_cooldown = 3
        
        # Initialize voice engine
        if VOICE_AVAILABLE:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
        
        # Create directories
        for dir_name in ['logs', 'screenshots', 'recordings']:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
        
        # Initialize log file
        self.log_file = f"logs/advanced_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.init_log_file()
        
        # Recording variables
        self.is_recording = False
        self.video_writer = None
        self.recording_start_time = None
        
        # Statistics
        self.start_time = datetime.now()
        
    def init_log_file(self):
        """Create detailed log file"""
        with open(self.log_file, 'w') as f:
            f.write("timestamp,eyes_detected,drowsiness_score,yawn_detected,looking_away,blink_rate,drowsy_events,yawn_events,looking_away_events\n")
    
    def log_data(self, eyes_detected, drowsiness_score, yawn_detected, looking_away, blink_rate):
        """Log all detection data"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        with open(self.log_file, 'a') as f:
            f.write(f"{timestamp},{eyes_detected},{drowsiness_score:.2f},{yawn_detected},{looking_away},{blink_rate},{self.drowsy_events},{self.yawn_events},{self.looking_away_events}\n")
    
    def play_alert_sound(self, alert_type="drowsy"):
        """Play different sounds for different alerts"""
        try:
            current_time = time.time()
            if current_time - self.last_alert_time >= self.alert_cooldown:
                if alert_type == "drowsy":
                    for _ in range(3):
                        winsound.Beep(1000, 500)
                        time.sleep(0.2)
                elif alert_type == "yawn":
                    winsound.Beep(1500, 300)
                    winsound.Beep(1200, 300)
                elif alert_type == "looking_away":
                    winsound.Beep(800, 200)
                    winsound.Beep(800, 200)
                
                self.last_alert_time = current_time
                print(f"\n🔔 {alert_type.upper()} ALERT! {datetime.now().strftime('%H:%M:%S')}\n")
        except:
            pass
    
    def voice_alert(self, message):
        """Speak alert message"""
        if VOICE_AVAILABLE and hasattr(self, 'engine'):
            try:
                current_time = time.time()
                if current_time - self.last_voice_alert_time >= 5:
                    threading.Thread(target=self._speak, args=(message,)).start()
                    self.last_voice_alert_time = current_time
            except:
                pass
    
    def _speak(self, message):
        """Internal method for voice"""
        try:
            self.engine.say(message)
            self.engine.runAndWait()
        except:
            pass
    
    def detect_eyes(self, face_roi):
        """Enhanced eye detection"""
        eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 5)
        if len(eyes) == 0:
            eyes = self.eye_cascade_tree.detectMultiScale(face_roi, 1.1, 5)
        return eyes
    
    def detect_yawn(self, face_roi_gray, face_roi_color):
        """Detect yawn based on mouth opening"""
        # Simplified yawn detection using mouth region
        h, w = face_roi_gray.shape
        mouth_region = face_roi_gray[int(h*0.6):int(h*0.8), int(w*0.3):int(w*0.7)]
        
        if mouth_region.size > 0:
            # Calculate mouth aspect ratio (simplified)
            mouth_opening = np.mean(mouth_region)
            is_yawn = mouth_opening < 50  # Darker region = open mouth
            
            if is_yawn:
                cv2.rectangle(face_roi_color, 
                            (int(w*0.3), int(h*0.6)), 
                            (int(w*0.7), int(h*0.8)), 
                            (0, 0, 255), 2)
            
            return is_yawn
        return False
    
    def estimate_head_pose(self, face_roi_gray):
        """Estimate if driver is looking away"""
        # Simplified head pose estimation
        h, w = face_roi_gray.shape
        center_x = w // 2
        center_y = h // 2
        
        # Detect face symmetry (simplified)
        left_half = face_roi_gray[:, :center_x]
        right_half = face_roi_gray[:, center_x:]
        
        if left_half.size > 0 and right_half.size > 0:
            left_brightness = np.mean(left_half)
            right_brightness = np.mean(right_half)
            asymmetry = abs(left_brightness - right_brightness)
            
            is_looking_away = asymmetry > 30
            return is_looking_away
        return False
    
    def calculate_blink_rate(self, eyes_detected):
        """Calculate blinks per minute"""
        self.blinks.append(1 if eyes_detected < 2 else 0)
        
        # Count blinks (eyes closed then opened)
        if eyes_detected < 2 and self.last_ear > 0.25:
            self.blink_count += 1
        
        self.last_ear = 0.3 if eyes_detected >= 2 else 0.1
        
        # Calculate blinks per minute
        blink_rate = self.blink_count * (60 / (self.BLINK_RATE_WINDOW / 30))
        return min(blink_rate, 30)  # Cap at 30 blinks/minute
    
    def start_recording(self, frame):
        """Start recording video when drowsy detected"""
        if not self.is_recording:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recordings/drowsy_event_{timestamp}.avi"
            h, w = frame.shape[:2]
            self.video_writer = cv2.VideoWriter(
                filename, 
                cv2.VideoWriter_fourcc(*'XVID'), 
                20.0, 
                (w, h)
            )
            self.is_recording = True
            self.recording_start_time = time.time()
            print(f"🎥 Recording started: {filename}")
    
    def stop_recording(self):
        """Stop recording video"""
        if self.is_recording and self.video_writer:
            self.video_writer.release()
            self.is_recording = False
            print(f"🎥 Recording stopped (Duration: {time.time() - self.recording_start_time:.1f}s)")
    
    def run(self):
        """Main detection loop"""
        print("="*70)
        print("🚗 ADVANCED DRIVER MONITORING SYSTEM")
        print("="*70)
        print("✅ System Started!")
        print(f"⚙️  Drowsiness Sensitivity: {self.EYE_CLOSED_THRESHOLD} frames")
        print(f"⚙️  Yawn Detection: ENABLED")
        print(f"⚙️  Head Pose Detection: ENABLED")
        print(f"⚙️  Blink Rate Analysis: ENABLED")
        print(f"⚙️  Voice Alerts: {'ENABLED' if VOICE_AVAILABLE else 'DISABLED'}")
        print(f"⚙️  Event Recording: ENABLED")
        print("="*70)
        print("📌 Press 'q' - Quit")
        print("📌 Press 's' - Screenshot")
        print("📌 Press 'r' - Reset Statistics")
        print("📌 Press 'v' - Toggle Voice Alerts")
        print("="*70 + "\n")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Camera not found!")
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        frame_count = 0
        start_time = time.time()
        voice_enabled = True
        
        # For statistics display
        blink_rate = 0
        yawn_detected = False
        looking_away = False
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
            
            # Calculate FPS
            frame_count += 1
            if time.time() - start_time > 1:
                fps = frame_count
                frame_count = 0
                start_time = time.time()
            else:
                fps = frame_count
            
            eyes_detected = 0
            yawn_detected = False
            looking_away = False
            
            for (x, y, w, h) in faces:
                # Draw face rectangle
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Face ROI
                face_roi_gray = gray[y:y+h, x:x+w]
                face_roi_color = frame[y:y+h, x:x+w]
                
                # Detect eyes
                eyes = self.detect_eyes(face_roi_gray)
                eyes_detected = len(eyes)
                
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (255, 0, 0), 2)
                
                # Detect yawn
                yawn_detected = self.detect_yawn(face_roi_gray, face_roi_color)
                
                # Detect head pose (looking away)
                looking_away = self.estimate_head_pose(face_roi_gray)
            
            # Calculate blink rate
            blink_rate = self.calculate_blink_rate(eyes_detected)
            
            # Drowsiness detection
            if eyes_detected < 2:
                self.eye_closed_counter += 1
                eye_status = "CLOSED"
            else:
                self.eye_closed_counter = max(0, self.eye_closed_counter - 1)
                eye_status = "OPEN"
            
            drowsiness_score = min(1.0, self.eye_closed_counter / self.EYE_CLOSED_THRESHOLD)
            is_drowsy = self.eye_closed_counter >= self.EYE_CLOSED_THRESHOLD
            
            # Track events
            previous_drowsy = is_drowsy
            previous_yawn = yawn_detected
            previous_looking = looking_away
            
            # ========== ALERTS ==========
            if is_drowsy:
                self.play_alert_sound("drowsy")
                if voice_enabled:
                    self.voice_alert("Warning! You seem drowsy. Please take a break.")
                self.start_recording(frame)
                
                if not previous_drowsy:
                    self.drowsy_events += 1
                    print(f"😴 DROWSY EVENT #{self.drowsy_events}")
            
            if yawn_detected and not previous_yawn:
                self.yawn_events += 1
                self.play_alert_sound("yawn")
                if voice_enabled:
                    self.voice_alert("Yawn detected. You may be tired.")
                print(f"😮 YAWN #{self.yawn_events}")
            
            if looking_away and not previous_looking:
                self.looking_away_events += 1
                self.play_alert_sound("looking_away")
                if voice_enabled:
                    self.voice_alert("Please focus on the road.")
                print(f"👀 LOOKING AWAY #{self.looking_away_events}")
            
            # Stop recording if no longer drowsy
            if not is_drowsy and self.is_recording:
                self.stop_recording()
            
            # ========== LOGGING ==========
            self.log_data(eyes_detected, drowsiness_score, yawn_detected, looking_away, blink_rate)
            
            # ========== RECORDING ==========
            if self.is_recording and self.video_writer:
                self.video_writer.write(frame)
                cv2.putText(frame, "RECORDING...", (10, frame.shape[0] - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # ========== DISPLAY INFO ==========
            self.display_info(frame, eyes_detected, eye_status, drowsiness_score, 
                            fps, self.drowsy_events, yawn_detected, looking_away, 
                            blink_rate, is_drowsy, voice_enabled)
            
            cv2.imshow("Advanced Driver Monitoring System", frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                cv2.imwrite(f"screenshots/driver_{timestamp}.jpg", frame)
                print(f"📸 Screenshot saved")
            elif key == ord('r'):
                self.drowsy_events = 0
                self.yawn_events = 0
                self.looking_away_events = 0
                print("🔄 Statistics reset")
            elif key == ord('v'):
                voice_enabled = not voice_enabled
                print(f"🔊 Voice alerts: {'ON' if voice_enabled else 'OFF'}")
        
        # Cleanup
        if self.is_recording:
            self.stop_recording()
        cap.release()
        cv2.destroyAllWindows()
        
        # Print session summary
        session_duration = (datetime.now() - self.start_time).total_seconds() / 60
        print("\n" + "="*70)
        print("📊 SESSION SUMMARY")
        print("="*70)
        print(f"📅 Date & Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Duration: {session_duration:.1f} minutes")
        print(f"😴 Drowsy Events: {self.drowsy_events}")
        print(f"😮 Yawn Events: {self.yawn_events}")
        print(f"👀 Looking Away Events: {self.looking_away_events}")
        print(f"📝 Log file: {self.log_file}")
        print("="*70)
    
    def display_info(self, frame, eyes_detected, eye_status, drowsiness_score, 
                    fps, drowsy_events, yawn_detected, looking_away, 
                    blink_rate, is_drowsy, voice_enabled):
        """Display all information on frame"""
        h, w = frame.shape[:2]
        
        # Background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 180), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
        
        y_pos = 25
        
        # Title
        cv2.putText(frame, "ADVANCED DRIVER MONITORING", (w//2 - 150, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # Drowsiness section
        cv2.putText(frame, f"Eyes: {eyes_detected} | Status: {eye_status}", (10, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        y_pos += 20
        
        # Drowsiness bar
        bar_width = int(drowsiness_score * 300)
        cv2.rectangle(frame, (10, y_pos), (310, y_pos+15), (100, 100, 100), -1)
        if drowsiness_score < 0.3:
            bar_color = (0, 255, 0)
        elif drowsiness_score < 0.7:
            bar_color = (0, 255, 255)
        else:
            bar_color = (0, 0, 255)
        cv2.rectangle(frame, (10, y_pos), (10 + bar_width, y_pos+15), bar_color, -1)
        cv2.putText(frame, f"Drowsiness: {drowsiness_score:.0%}", (10, y_pos-3), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        y_pos += 25
        
        # Additional metrics
        cv2.putText(frame, f"Blink Rate: {blink_rate:.0f} blinks/min", (10, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        y_pos += 20
        
        # Status indicators
        if yawn_detected:
            cv2.putText(frame, "😮 YAWN DETECTED!", (10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        y_pos += 20
        
        if looking_away:
            cv2.putText(frame, "👀 LOOKING AWAY!", (10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        y_pos += 20
        
        # Right side info
        cv2.putText(frame, f"FPS: {fps}", (w-80, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"Events: {drowsy_events}", (w-100, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Voice status
        voice_status = "🔊 ON" if voice_enabled else "🔇 OFF"
        cv2.putText(frame, f"Voice: {voice_status}", (w-80, 75), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0) if voice_enabled else (0, 0, 255), 1)
        
        # Alert border
        if is_drowsy:
            cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 255), 5)
            cv2.putText(frame, "!!! DROWSY ALERT !!!", (w//2 - 120, h//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Instructions
        cv2.putText(frame, "Q:Quit | S:Shot | R:Reset | V:Voice", (10, h-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

if __name__ == "__main__":
    detector = AdvancedDrowsinessDetector()
    detector.run()