import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, \
    QTextEdit, QFrame
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPalette, QMovie, QPainter, QPen, QBrush, QRadialGradient, QLinearGradient
import math

# Your existing imports
import pyttsx3
import speech_recognition as sr
import keyboard
import os
import subprocess as sp
import imdb
import wolframalpha
import pyautogui
import webbrowser

from datetime import datetime
from decouple import config
from random import choice
# Assuming 'conv.py' and 'online.py' are in the same directory
from conv import random_text
from online import find_my_ip, search_on_google, search_on_wikipedia, youtube, send_email, get_news, weather_forecast
from openai import OpenAI

# Your existing global variables
engine = pyttsx3.init('sapi5')
engine.setProperty('volume', 1.0)
engine.setProperty('rate', 210)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

USER = config('USER')
HOSTNAME = config('BOT')


class ArcReactorWidget(QWidget):
    """Custom widget to draw the Arc Reactor animation"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 300)
        self.rotation_angle = 0
        self.pulse_intensity = 0.5
        self.pulse_direction = 1

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(50)  # 20 FPS

    def update_animation(self):
        self.rotation_angle += 2
        if self.rotation_angle >= 360:
            self.rotation_angle = 0

        # Pulse effect
        self.pulse_intensity += 0.02 * self.pulse_direction
        if self.pulse_intensity >= 1.0:
            self.pulse_direction = -1
        elif self.pulse_intensity <= 0.3:
            self.pulse_direction = 1

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center_x, center_y = self.width() // 2, self.height() // 2

        # Outer glow effect
        for i in range(10, 0, -1):
            alpha = int(30 * self.pulse_intensity * (i / 10))
            glow_color = QColor(0, 200, 255, alpha)
            painter.setPen(QPen(glow_color, i * 2))
            painter.drawEllipse(center_x - 80 - i * 2, center_y - 80 - i * 2, 160 + i * 4, 160 + i * 4)

        # Main arc reactor ring
        gradient = QRadialGradient(center_x, center_y, 80)
        gradient.setColorAt(0, QColor(100, 200, 255, 200))
        gradient.setColorAt(0.7, QColor(0, 150, 255, 150))
        gradient.setColorAt(1, QColor(0, 100, 200, 100))

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(0, 255, 255), 2))
        painter.drawEllipse(center_x - 80, center_y - 80, 160, 160)

        # Inner core
        core_gradient = QRadialGradient(center_x, center_y, 30)
        core_gradient.setColorAt(0, QColor(255, 255, 255, int(255 * self.pulse_intensity)))
        core_gradient.setColorAt(0.5, QColor(100, 200, 255, int(200 * self.pulse_intensity)))
        core_gradient.setColorAt(1, QColor(0, 150, 255, int(100 * self.pulse_intensity)))

        painter.setBrush(QBrush(core_gradient))
        painter.setPen(QPen(QColor(0, 255, 255), 1))
        painter.drawEllipse(center_x - 30, center_y - 30, 60, 60)

        # Rotating energy lines
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.rotation_angle)

        for angle in range(0, 360, 30):
            painter.save()
            painter.rotate(angle)

            # Energy beam effect
            beam_gradient = QLinearGradient(0, -60, 0, 60)
            beam_gradient.setColorAt(0, QColor(0, 255, 255, 0))
            beam_gradient.setColorAt(0.5, QColor(100, 255, 255, int(150 * self.pulse_intensity)))
            beam_gradient.setColorAt(1, QColor(0, 255, 255, 0))

            painter.setPen(QPen(QBrush(beam_gradient), 2))
            painter.drawLine(0, -70, 0, -40)
            painter.drawLine(0, 40, 0, 70)

            painter.restore()

        painter.restore()

        # Add hexagonal pattern
        painter.setPen(QPen(QColor(0, 255, 255, 100), 1))
        for radius in [40, 55, 70]:
            for i in range(6):
                angle1 = i * 60 * math.pi / 180
                angle2 = (i + 1) * 60 * math.pi / 180
                x1 = center_x + radius * math.cos(angle1)
                y1 = center_y + radius * math.sin(angle1)
                x2 = center_x + radius * math.cos(angle2)
                y2 = center_y + radius * math.sin(angle2)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))


class StatusIndicator(QWidget):
    """Custom animated status indicator"""

    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)
        self.color = color
        self.active = False
        self.pulse = 0.5
        self.pulse_dir = 1

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(100)

    def set_active(self, active):
        self.active = active

    def animate(self):
        if self.active:
            self.pulse += 0.1 * self.pulse_dir
            if self.pulse >= 1.0:
                self.pulse_dir = -1
            elif self.pulse <= 0.3:
                self.pulse_dir = 1
        else:
            self.pulse = 0.2
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.active:
            # Glow effect
            for i in range(5, 0, -1):
                alpha = int(100 * self.pulse * (i / 5))
                glow_color = QColor(*self.color, alpha)
                painter.setPen(QPen(glow_color, i))
                painter.drawEllipse(2, 2, 16, 16)

        # Main indicator
        alpha = int(255 * self.pulse) if self.active else 80
        main_color = QColor(*self.color, alpha)
        painter.setBrush(QBrush(main_color))
        painter.setPen(QPen(QColor(*self.color), 1))
        painter.drawEllipse(4, 4, 12, 12)


class JarvisEnhancedGUI(QMainWindow):
    # Signals
    update_text_signal = pyqtSignal(str)
    listening_status_signal = pyqtSignal(bool)
    speaking_status_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.listening = False
        self.initUI()
        self.setup_jarvis_engine()
        self.greet_me()

        # Connect signals
        self.update_text_signal.connect(self.update_output_text)
        self.listening_status_signal.connect(self.set_listening_status)
        self.speaking_status_signal.connect(self.set_speaking_status)

        # Start voice recognition thread
        self.voice_thread = VoiceCommandThread()
        self.voice_thread.command_received.connect(self.process_command)
        self.voice_thread.listening_status.connect(self.listening_status_signal)
        self.voice_thread.start()

        # Register hotkeys
        keyboard.add_hotkey('ctrl+alt+k', self.start_listening_hotkey)
        keyboard.add_hotkey('ctrl+alt+p', self.pause_listening_hotkey)

    def setup_jarvis_engine(self):
        pass

    def initUI(self):
        self.setWindowTitle(f"◢ {HOSTNAME} ◤ REACTER INTERFACE")
        self.setGeometry(50, 50, 1400, 900)

        # Dark theme with enhanced gradients
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000508, stop:0.2 #001122, stop:0.5 #001a2e, stop:0.8 #000a1a, stop:1 #000000);
                border: 3px solid #00ccff;
                border-radius: 20px;
            }
            QWidget {
                background: transparent;
                color: #00ffff;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Enhanced Header
        self.create_header(main_layout)

        # Content area with Arc Reactor
        content_layout = QHBoxLayout()

        # Left panel with Arc Reactor
        self.create_arc_reactor_panel(content_layout)

        # Right panel with terminal
        self.create_terminal_panel(content_layout)

        main_layout.addLayout(content_layout)

        # Enhanced Control Panel
        self.create_control_panel(main_layout)

    def create_header(self, main_layout):
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0,200,255,0.1), stop:0.3 rgba(0,255,255,0.2), 
                    stop:0.7 rgba(0,255,255,0.2), stop:1 rgba(0,200,255,0.1));
                border: 2px solid #00ccff;
                border-radius: 15px;
                margin: 5px;
                min-height: 80px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)

        # Enhanced Logo
        logo_label = QLabel("◢ J.A.R.V.I.S ◤")
        logo_label.setFont(QFont("Consolas", 24, QFont.Bold))
        logo_label.setStyleSheet("""
            color: #00ffff;
            text-shadow: 0 0 20px #00ffff, 0 0 40px #00ccff;
            background: transparent;
            padding: 10px;
        """)
        header_layout.addWidget(logo_label)

        header_layout.addStretch()

        # Status Panel with custom indicators
        status_panel = self.create_status_panel()
        header_layout.addWidget(status_panel)

        # Enhanced Digital Clock
        self.time_label = QLabel(datetime.now().strftime("%H:%M:%S"))
        self.time_label.setFont(QFont("Consolas", 20, QFont.Bold))
        self.time_label.setStyleSheet("""
            color: #ffaa00;
            text-shadow: 0 0 15px #ffaa00, 0 0 30px #ff8800;
            background: rgba(0,0,0,0.8);
            border: 2px solid #ffaa00;
            border-radius: 10px;
            padding: 10px 20px;
        """)
        header_layout.addWidget(self.time_label)

        # Timer for clock
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        main_layout.addWidget(header_frame)

    def create_status_panel(self):
        status_panel = QFrame()
        status_panel.setStyleSheet("""
            QFrame {
                background: rgba(0,0,0,0.7);
                border: 1px solid #00ccff;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        status_layout = QHBoxLayout(status_panel)

        self.status_label = QLabel("[ SYSTEM: STANDBY ]")
        self.status_label.setFont(QFont("Consolas", 14, QFont.Bold))
        self.status_label.setStyleSheet("""
            color: #00ffff;
            text-shadow: 0 0 10px #00ffff;
        """)
        status_layout.addWidget(self.status_label)

        # Custom status indicators
        status_layout.addWidget(QLabel(" | MIC:"))
        self.listening_indicator = StatusIndicator((0, 255, 0))
        status_layout.addWidget(self.listening_indicator)

        status_layout.addWidget(QLabel(" | SPK:"))
        self.speaking_indicator = StatusIndicator((255, 165, 0))
        status_layout.addWidget(self.speaking_indicator)

        return status_panel

    def create_arc_reactor_panel(self, content_layout):
        left_panel = QFrame()
        left_panel.setFixedWidth(350)
        left_panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0,50,100,0.3), stop:0.5 rgba(0,100,150,0.2), stop:1 rgba(0,30,60,0.3));
                border: 2px solid #0099cc;
                border-radius: 15px;
                margin: 5px;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignCenter)


        reactor_label = QLabel("JARVIS")
        reactor_label.setFont(QFont("Consolas", 16, QFont.Bold))
        reactor_label.setStyleSheet("""
            color: #00ffff;
            text-shadow: 0 0 15px #00ffff;
            margin: 10px;
        """)
        reactor_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(reactor_label)

        self.arc_reactor = ArcReactorWidget()
        left_layout.addWidget(self.arc_reactor)

        # Power level indicator
        power_label = QLabel("________")
        power_label.setFont(QFont("Consolas", 12, QFont.Bold))
        power_label.setStyleSheet("""
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
            margin: 10px;
        """)
        power_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(power_label)

        content_layout.addWidget(left_panel)

    def create_terminal_panel(self, content_layout):
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0,20,40,0.95), stop:0.5 rgba(0,10,20,0.98), stop:1 rgba(0,0,0,0.99));
                border: 2px solid #00ccff;
                border-radius: 15px;
                margin: 5px;
            }
        """)
        right_layout = QVBoxLayout(right_panel)

        # Terminal header
        terminal_header = QLabel("◢ NEURAL INTERFACE TERMINAL ◤")
        terminal_header.setFont(QFont("Consolas", 14, QFont.Bold))
        terminal_header.setStyleSheet("""
            color: #00ffff;
            text-shadow: 0 0 15px #00ffff;
            background: rgba(0,100,150,0.2);
            border: 1px solid #00ccff;
            border-radius: 8px;
            padding: 8px;
            margin: 5px;
        """)
        terminal_header.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(terminal_header)

        # Enhanced terminal output
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 11))
        self.output_text.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0,20,40,0.9), stop:1 rgba(0,0,0,0.95));
                border: 1px solid #006699;
                border-radius: 10px;
                color: #00ff88;
                padding: 15px;
                selection-background-color: rgba(0,255,255,0.3);
                font-family: 'Consolas', 'Courier New', monospace;
                line-height: 1.4;
            }
            QScrollBar:vertical {
                background: rgba(0,0,0,0.5);
                width: 14px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ccff, stop:1 #0099cc);
                border-radius: 7px;
                min-height: 25px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ffff, stop:1 #00ccff);
            }
        """)

        # Enhanced welcome message
        welcome_msg = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                              J.A.R.V.I.S                                  ║
║                    Just A Rather Very Intelligent System                  ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

◢ INITIALIZATION SEQUENCE ◤
► System Status.................. [ONLINE]
► Reactor Core............... [STABLE] 
► Neural Network................ [ACTIVE]
► Voice Recognition............. [STANDBY]
► All Primary Systems........... [OPERATIONAL]

---- READY FOR COMMAND INPUT---- 
        """
        self.output_text.setHtml(f'<pre style="color: #00ffff; text-shadow: 0 0 5px #00ccff;">{welcome_msg}</pre>')
        right_layout.addWidget(self.output_text)

        content_layout.addWidget(right_panel)

    def create_control_panel(self, main_layout):
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0,150,255,0.1), stop:0.3 rgba(0,255,200,0.15), 
                    stop:0.7 rgba(0,255,200,0.15), stop:1 rgba(0,150,255,0.1));
                border: 2px solid #00ffcc;
                border-radius: 15px;
                margin: 5px;
                min-height: 80px;
            }
        """)
        button_layout = QHBoxLayout(control_frame)
        button_layout.setContentsMargins(20, 15, 20, 15)

        # Enhanced buttons
        self.start_btn = QPushButton(" -ACTIVATE NEURAL LINK -")
        self.start_btn.clicked.connect(self.start_listening)
        self.start_btn.setStyleSheet(self.get_enhanced_button_style("#00ff44", "#004411"))
        button_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton(" -SUSPEND OPERATIONS -")
        self.pause_btn.clicked.connect(self.pause_listening)
        self.pause_btn.setStyleSheet(self.get_enhanced_button_style("#ffcc00", "#443300"))
        button_layout.addWidget(self.pause_btn)

        self.exit_btn = QPushButton(" -EMERGENCY SHUTDOWN-")
        self.exit_btn.clicked.connect(self.close)
        self.exit_btn.setStyleSheet(self.get_enhanced_button_style("#ff3366", "#441122"))
        button_layout.addWidget(self.exit_btn)

        main_layout.addWidget(control_frame)

    def get_enhanced_button_style(self, accent_color, shadow_color):
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0,0,0,0.8), stop:0.3 {accent_color}30, 
                    stop:0.7 {accent_color}40, stop:1 rgba(0,0,0,0.9));
                border: 2px solid {accent_color};
                border-radius: 12px;
                color: {accent_color};
                padding: 15px 25px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', 'Courier New', monospace;
                text-shadow: 0 0 15px {accent_color};
                min-height: 25px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {accent_color}40, stop:0.5 {accent_color}60, stop:1 {shadow_color}80);
                border: 2px solid {accent_color};
                text-shadow: 0 0 25px {accent_color}, 0 0 40px {accent_color};
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background: {accent_color}60;
                border: 3px solid {accent_color};
                text-shadow: 0 0 30px {accent_color};
                transform: translateY(1px);
            }}
        """

    def update_time(self):
        self.time_label.setText(datetime.now().strftime("%H:%M:%S"))

    def update_output_text(self, text):
        if text.startswith("You:"):
            formatted_text = f'<span style="color: #00ccff; text-shadow: 0 0 8px #00ccff;">► USER INPUT: {text[4:]}</span>'
        elif text.startswith(f"{HOSTNAME}:"):
            formatted_text = f'<span style="color: #00ff88; text-shadow: 0 0 8px #00ff88;">◆ {HOSTNAME}: {text[len(HOSTNAME) + 1:]}</span>'
        elif text.startswith("JARVIS:"):
            formatted_text = f'<span style="color: #ffaa00; text-shadow: 0 0 8px #ffaa00;">◇ SYSTEM: {text[7:]}</span>'
        else:
            formatted_text = f'<span style="color: #ffffff;">⚡ {text}</span>'

        self.output_text.append(formatted_text)

    def set_listening_status(self, is_listening):
        self.listening_indicator.set_active(is_listening)
        if is_listening:
            self.status_label.setText("[ NEURAL LINK: ACTIVE ]")
            self.status_label.setStyleSheet("""
                color: #00ff44;
                text-shadow: 0 0 15px #00ff44;
            """)
        else:
            self.status_label.setText("[ SYSTEM: STANDBY ]")
            self.status_label.setStyleSheet("""
                color: #00ffff;
                text-shadow: 0 0 10px #00ffff;
            """)

    def set_speaking_status(self, is_speaking):
        self.speaking_indicator.set_active(is_speaking)

    def speak(self, text):
        self.speaking_status_signal.emit(True)
        self.update_text_signal.emit(f"{HOSTNAME}: {text}")
        engine.say(text)
        engine.runAndWait()
        self.speaking_status_signal.emit(False)

    def greet_me(self):
        hour = datetime.now().hour
        greeting = ""
        if (hour >= 6) and (hour < 12):
            greeting = f"Good Morning {USER}"
        elif (hour >= 12) and (hour <= 16):
            greeting = f"Good Afternoon {USER}"
        elif (hour >= 16) and (hour < 24):
            greeting = f"Good evening {USER}"
        self.speak(
            f"{greeting}. I am {HOSTNAME}, your advanced AI assistant. How may I assist you, {USER}?")

    def start_listening(self):
        self.listening = True
        self.listening_status_signal.emit(True)
        self.update_text_signal.emit("JARVIS: Neural link established. Listening for commands...")
        self.voice_thread.start_listening()  # Tell the thread to start listening

    def pause_listening(self):
        self.listening = False
        self.listening_status_signal.emit(False)
        self.update_text_signal.emit("JARVIS: Operations suspended. Standing by.")
        self.voice_thread.stop_listening()  # Tell the thread to stop listening

    def start_listening_hotkey(self):
        self.start_listening()

    def pause_listening_hotkey(self):
        self.pause_listening()

    def process_command(self, query):
        self.update_text_signal.emit(f"You: {query}")
        if not self.listening or query.lower() in ["none", ""]:
            return  # Don't process if paused via GUI/hotkey or empty query

        # --- Your existing command processing logic, now using self.speak ---
        if "how are you jarvis" in query:
            self.speak("I wasn't, but now I am absolutely amazing, just missing you")

        elif "open command prompt" in query:
            self.speak("Opening command prompt")
            os.system('start cmd')

        elif "open camera" in query:
            self.speak("Opening camera boss")
            sp.run('start microsoft.windows.camera:', shell=True)

        elif "open notepad" in query:
            self.speak("Opening notepad for you boss")
            try:
                notepad_paths = [
                    r"C:\Users\shaiv\AppData\Local\Microsoft\WindowsApps\notepad.exe",
                    r"C:\Windows\System32\notepad.exe",
                    "notepad.exe"
                ]
                opened = False
                for path in notepad_paths:
                    try:
                        if path == "notepad.exe":
                            os.system("start notepad")
                        else:
                            os.startfile(path)
                        opened = True
                        break
                    except:
                        continue
                if not opened:
                    self.speak("Sorry, I couldn't open notepad")
            except Exception as e:
                self.speak("Sorry, I couldn't open notepad")

        elif "open spotify" in query:
            self.speak("Opening Spotify for you boss")
            try:
                spotify_paths = [
                    r"C:\Users\shaiv\AppData\Local\Microsoft\WindowsApps\Spotify.exe",
                    r"C:\Users\shaiv\AppData\Roaming\Spotify\Spotify.exe",
                    "spotify"
                ]
                opened = False
                for path in spotify_paths:
                    try:
                        if path == "spotify":
                            os.system("start spotify:")
                        else:
                            os.startfile(path)
                        opened = True
                        break
                    except:
                        continue
                if not opened:
                    self.speak("Sorry, I couldn't open Spotify")
            except Exception as e:
                self.speak("Sorry, I couldn't open Spotify")

        elif "ip address" in query:
            ip_address = find_my_ip()
            self.speak(f"your ip address is {ip_address}")
            self.update_text_signal.emit(f"Your IP address: {ip_address}")

        elif "youtube" in query:
            self.speak("What do you want to play on youtube Shaivi?")
            video = self.get_gui_input("What video on YouTube?")
            if video and video != "none":
                youtube(video)
                self.speak(f"Playing {video} on YouTube.")
            else:
                self.speak("No video specified.")

        elif "open google" in query:
            self.speak(f"What do you want to search on google {USER}")
            search_query = self.get_gui_input(f"What to search on Google, {USER}?")
            if search_query and search_query != "none":
                search_on_google(search_query)
                self.speak(f"Searching Google for {search_query}.")
            else:
                self.speak("No search query specified.")

        elif "open wikipedia" in query:
            self.speak("what do you want to search on wikipedia?")
            search = self.get_gui_input("What to search on Wikipedia?")
            if search and search != "none":
                results = search_on_wikipedia(search)
                self.speak(f"According to wikipedia, {results[:200]}...")
                self.update_text_signal.emit(f"Wikipedia Results for '{search}':\n{results}")
            else:
                self.speak("No Wikipedia search query specified.")

        elif "send an email" in query:
            self.speak("On what email address do you want to send sir?. Please enter in the terminal")
            receiver_add = self.get_gui_input("Enter receiver email address:")
            if not receiver_add:
                self.speak("Email address not provided.")
                return


            self.speak("What should be the subject sir?")
            subject = self.get_gui_input("Enter subject:")
            if not subject:
                self.speak("Subject not provided.")
                return

            self.speak("What is the message?")
            message = self.get_gui_input("Enter message:")
            if not message:
                self.speak("Message not provided.")
                return

            if send_email(receiver_add, subject, message):
                self.speak("I have sent the email shaivi")
                self.update_text_signal.emit("Email sent successfully.")
            else:
                self.speak("Something went wrong. Please check the error log.")
                self.update_text_signal.emit("Error sending email.")

        elif "give me news" in query:
            self.speak("I am reading out the latest headlines of today")
            news_headlines = get_news()
            if news_headlines:
                for headline in news_headlines[:3]:
                    self.speak(headline)
                self.update_text_signal.emit("Latest News Headlines:\n" + "\n".join(news_headlines))
            else:
                self.speak("Sorry, I couldn't fetch the news headlines.")

        elif "weather" in query:
            self.speak("tell me the name of your city")
            city = self.get_gui_input("Enter the name of your city:")
            if city:
                self.speak(f"Getting weather report of your city {city}")
                weather_desc, temp, feels_like = weather_forecast(city)
                if weather_desc:
                    self.speak(f"The current temperature is {temp}, but it feels like {feels_like}")
                    self.speak(f"Also the weather report talks about {weather_desc}")
                    self.update_text_signal.emit(
                        f"Weather in {city}:\nDescription: {weather_desc}\nTemperature: {temp}\nFeels like: {feels_like}")
                else:
                    self.speak(f"Sorry, I couldn't get the weather for {city}.")
            else:
                self.speak("No city specified for weather.")

        elif "movie" in query:
            movies_db = imdb.IMDB()
            self.speak("Please tell me the movie name:")
            text = self.get_gui_input("Enter movie name:")
            if text:
                self.speak("Searching for " + text)
                try:
                    movie_results = movies_db.search_movie(text)
                    if movie_results:
                        self.speak("I found these:")
                        for movie in movie_results[:1]:  # Just take the first result for brevity
                            title = movie.get("title")
                            year = movie.get("year")
                            self.speak(f"{title}. {year}")
                            info = movie.getID()
                            movie_info = movies_db.get_movie(info)
                            rating = movie_info.get("rating")
                            cast = [actor['name'] for actor in movie_info.get("cast", [])[:5]]
                            plot = movie_info.get('plot outline',
                                                  movie_info.get('plot summary', ['plot summary not available']))[0]

                            full_info = (f"{title} was released in {year} has IMDb ratings of {rating}. "
                                         f"It has a cast of {', '.join(cast)}. The plot summary of the movie is: {plot}")
                            self.speak(full_info)
                            self.update_text_signal.emit(full_info)
                            break
                    else:
                        self.speak("Sorry, I couldn't find any movies with that name.")
                except Exception as e:
                    self.speak(f"An error occurred while searching for movies: {e}")
                    self.update_text_signal.emit(f"Error searching movie: {e}")
            else:
                self.speak("No movie name specified.")

        elif "calculate" in query:
            app_id = "6Q4R5J-H8L9K4PHJH"  # Your WolframAlpha App ID
            client = wolframalpha.Client(app_id)
            try:
                ind = query.lower().split().index("calculate")
                text = query.split()[ind + 1:]
                result = client.query(" ".join(text))
                ans = next(result.results).text
                self.speak("The answer is " + ans)
                self.update_text_signal.emit(f"Calculation Result: {ans}")
            except (ValueError, StopIteration):
                self.speak("I couldn't find that. Please try again or rephrase the calculation.")
            except Exception as e:
                self.speak(f"An error occurred during calculation: {e}")
                self.update_text_signal.emit(f"Error in calculation: {e}")

        elif "what is" in query or "who is" in query or "which is" in query:
            app_id = "7A8YWWRT8K"  # Your WolframAlpha App ID
            client = wolframalpha.Client(app_id)
            try:
                ind = query.lower().index('what is') if 'what is' in query.lower() else \
                    query.lower().index('who is') if 'who is' in query.lower() else \
                        query.lower().index('which is') if 'which is' in query.lower() else None

                if ind is not None:
                    text = query.split()[ind + 2:]
                    result = client.query(" ".join(text))
                    ans = next(result.results).text
                    self.speak("The answer is " + ans)
                    self.update_text_signal.emit(f"Information: {ans}")
                else:
                    self.speak("I couldn't find that. Please try again.")
            except (ValueError, StopIteration):
                self.speak("I couldn't find that. Please try again.")
            except Exception as e:
                self.speak(f"An error occurred while fetching information: {e}")
                self.update_text_signal.emit(f"Error fetching info: {e}")

        elif 'stop' in query or 'exit' in query:
            hour = datetime.now().hour
            if hour >= 21 or hour <= 4:
                self.speak("It's been midnight Shaivi, I hope you had your coffee today? bye !! Good night")
            else:
                self.speak("Have a good day shaivi!")
            QApplication.instance().quit()

        elif query != "none" and query.strip():
            self.speak("Thinking...")
            self.update_text_signal.emit("JARVIS: Thinking...")

            # Start LLM processing in a new thread
            self.llm_thread = LLMThread(query)
            self.llm_thread.llm_response_signal.connect(self.handle_llm_response)
            self.llm_thread.error_signal.connect(self.handle_llm_error)
            self.llm_thread.start()

    def handle_llm_response(self, response_text):
        self.speak(response_text)
        self.update_text_signal.emit(f"LLM: {response_text}")

    def handle_llm_error(self, error_message):
        self.speak("I encountered an issue with my advanced language model.")
        self.update_text_signal.emit(error_message)

    def get_gui_input(self, prompt):
        from PyQt5.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "JARVIS Input", prompt)
        if ok:
            return text
        return None


# Voice Recognition Thread
class VoiceCommandThread(QThread):
    command_received = pyqtSignal(str)
    listening_status = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._is_listening = False
        self._recognizer = sr.Recognizer()
        self._microphone = sr.Microphone()

    def run(self):
        while True:
            if self._is_listening:
                self.listening_status.emit(True)
                with self._microphone as source:
                    self._recognizer.pause_threshold = 1
                    try:
                        audio = self._recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        query = self._recognizer.recognize_google(audio, language="en-in")
                        self.command_received.emit(query.lower())
                    except sr.WaitTimeoutError:
                        pass  # Continue listening
                    except sr.UnknownValueError:
                        pass  # Continue listening without emitting "None"
                    except sr.RequestError as e:
                        print(f"Could not request results from Google Speech Recognition service; {e}")
                        pass
                    except Exception as e:
                        print(f"An unexpected error occurred in voice thread: {e}")
                        pass
            else:
                self.listening_status.emit(False)
                self.msleep(100)

    def start_listening(self):
        self._is_listening = True

    def stop_listening(self):
        self._is_listening = False



try:
    import openai


    class LLMThread(QThread):
        llm_response_signal = pyqtSignal(str)
        error_signal = pyqtSignal(str)

        def __init__(self, prompt):
            super().__init__()
            self.prompt = prompt
            self.api_key = config('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', default='')

        def run(self):
            try:
                if not self.api_key:
                    self.error_signal.emit("LLM Error: OpenAI API key not configured in .env file.")
                    return

                openai.api_key = self.api_key
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system",
                         "content": f"You are a helpful AI assistant named {HOSTNAME}. Your user is {USER}."},
                        {"role": "user", "content": self.prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                llm_text = response.choices[0].message.content
                self.llm_response_signal.emit(llm_text)
            except openai.AuthenticationError:
                self.error_signal.emit("LLM Error: Invalid OpenAI API key. Please check your .env file.")
            except Exception as e:
                self.error_signal.emit(f"LLM Error: {e}")
except ImportError:
    print("OpenAI not installed. LLM features disabled.")


    class LLMThread(QThread):
        llm_response_signal = pyqtSignal(str)
        error_signal = pyqtSignal(str)

        def __init__(self, prompt):
            super().__init__()

        def run(self):
            self.error_signal.emit("OpenAI library not installed. Install with: pip install openai")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    jarvis_gui = JarvisEnhancedGUI()
    jarvis_gui.show()
    sys.exit(app.exec_())
