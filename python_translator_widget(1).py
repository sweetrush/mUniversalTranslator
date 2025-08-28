import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import pyperclip
import win32gui
import win32con
import win32api
import win32clipboard
import keyboard
import requests
import json
from googletrans import Translator
import langdetect
from langdetect import detect
import sqlite3
import os
from datetime import datetime
import sys
import pygame
from gtts import gTTS
import tempfile
import io

class UniversalTranslator:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Initialize translator with error handling
        try:
            from googletrans import Translator
            self.translator = Translator()
        except ImportError:
            messagebox.showerror("Missing Package", 
                               "Please install googletrans: pip install googletrans==4.0.0rc1")
            sys.exit()
        except Exception as e:
            print(f"Translator initialization warning: {e}")
            self.translator = None
        
        # Initialize pygame mixer for audio playback
        try:
            pygame.mixer.init()
            self.audio_enabled = True
        except:
            self.audio_enabled = False
            print("Audio playback not available")
        
        self.current_audio_file = None
        self.settings = {
            'auto_insert': True,
            'clipboard_monitor': True,
            'always_on_top': True,
            'target_language': 'es',
            'auto_play_audio': False  # New setting for auto-play audio
        }
        
        # Language mappings
        self.languages = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
            'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese',
            'ko': 'Korean', 'zh': 'Chinese (Simplified)', 'ar': 'Arabic', 'hi': 'Hindi',
            'nl': 'Dutch', 'sv': 'Swedish', 'no': 'Norwegian', 'da': 'Danish',
            'fi': 'Finnish', 'pl': 'Polish', 'cs': 'Czech', 'sk': 'Slovak',
            'hu': 'Hungarian', 'ro': 'Romanian', 'bg': 'Bulgarian', 'hr': 'Croatian'
        }
        
        self.create_widgets()
        self.setup_hotkeys()
        self.init_database()
        
        # Initialize these variables BEFORE starting clipboard monitor
        self.current_mode = "translate"
        self.last_clipboard = ""
        self.monitoring = False
        
        # Start clipboard monitor AFTER all variables are initialized
        self.start_clipboard_monitor()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("🌐 Universal Translator")
        self.root.geometry("450x750")  # Increased height for larger text areas
        self.root.configure(bg='#f0f2f5')
        
        # Make window stay on top initially
        self.root.wm_attributes("-topmost", True)
        
        # Remove default window decorations for custom look
        self.root.overrideredirect(False)
        
        # Center window on screen
        self.center_window()
        
        # Make window resizable
        self.root.resizable(True, True)
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container with padding
        main_frame = tk.Frame(self.root, bg='#f0f2f5', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Header with title and minimize button
        header_frame = tk.Frame(main_frame, bg='#4facfe', height=50)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🌐 Universal Translator", 
                              bg='#4facfe', fg='white', font=('Segoe UI', 12, 'bold'))
        title_label.pack(side='left', padx=15, pady=15)
        
        minimize_btn = tk.Button(header_frame, text="−", bg='#ffffff', 
                               fg='#4facfe', bd=0, font=('Segoe UI', 14, 'bold'),
                               command=self.minimize_window)
        minimize_btn.pack(side='right', padx=15, pady=15)
        
        # Mode selector
        mode_frame = tk.Frame(main_frame, bg='#f0f2f5')
        mode_frame.pack(fill='x', pady=(0, 15))
        
        self.translate_btn = tk.Button(mode_frame, text="Translate", 
                                     command=lambda: self.set_mode('translate'),
                                     bg='#4facfe', fg='white', bd=0, padx=20, pady=8,
                                     font=('Segoe UI', 10, 'bold'))
        self.translate_btn.pack(side='left', padx=(0, 5))
        
        self.listen_btn = tk.Button(mode_frame, text="Auto-Detect", 
                                  command=lambda: self.set_mode('listen'),
                                  bg='#e2e8f0', fg='#64748b', bd=0, padx=20, pady=8,
                                  font=('Segoe UI', 10))
        self.listen_btn.pack(side='left', padx=5)
        
        # Translation section
        self.translation_frame = tk.Frame(main_frame, bg='#f0f2f5')
        self.translation_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Language selector
        lang_frame = tk.Frame(self.translation_frame, bg='#f0f2f5')
        lang_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(lang_frame, text="From:", bg='#f0f2f5', font=('Segoe UI', 10)).pack(side='left')
        
        self.from_lang = ttk.Combobox(lang_frame, values=list(self.languages.values()), 
                                     width=12, state='readonly')
        self.from_lang.set('English')
        self.from_lang.pack(side='left', padx=(5, 10))
        
        swap_btn = tk.Button(lang_frame, text="⇄", bg='#e2e8f0', bd=1, 
                           font=('Segoe UI', 12), command=self.swap_languages)
        swap_btn.pack(side='left', padx=5)
        
        tk.Label(lang_frame, text="To:", bg='#f0f2f5', font=('Segoe UI', 10)).pack(side='left', padx=(10, 0))
        
        self.to_lang = ttk.Combobox(lang_frame, values=list(self.languages.values()), 
                                   width=12, state='readonly')
        self.to_lang.set('Spanish')
        self.to_lang.pack(side='left', padx=(5, 0))
        
        # Input text area (larger)
        tk.Label(self.translation_frame, text="Input Text:", bg='#f0f2f5', 
                font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.input_text = scrolledtext.ScrolledText(self.translation_frame, height=6, 
                                                   font=('Segoe UI', 10), wrap='word')
        self.input_text.pack(fill='x', pady=(0, 15))
        self.input_text.bind('<KeyRelease>', self.on_text_change)
        
        # Output text area (larger)
        output_header = tk.Frame(self.translation_frame, bg='#f0f2f5')
        output_header.pack(fill='x', pady=(0, 5))
        
        tk.Label(output_header, text="Translation:", bg='#f0f2f5', 
                font=('Segoe UI', 10, 'bold')).pack(side='left')
        
        # Play audio button
        self.play_btn = tk.Button(output_header, text="🔊", 
                                command=self.play_translation_audio,
                                bg='#e2e8f0', fg='#64748b', bd=0, padx=8, pady=2,
                                font=('Segoe UI', 12), state='disabled')
        self.play_btn.pack(side='right')
        
        self.output_text = scrolledtext.ScrolledText(self.translation_frame, height=6, 
                                                    font=('Segoe UI', 10), wrap='word',
                                                    bg='#f8fffe')
        self.output_text.pack(fill='x', pady=(0, 15))
        self.output_text.insert(1.0, "Translation will appear here...")
        self.output_text.config(state='disabled')
        
        # Action buttons
        btn_frame = tk.Frame(self.translation_frame, bg='#f0f2f5')
        btn_frame.pack(fill='x', pady=(0, 15))
        
        self.insert_btn = tk.Button(btn_frame, text="📋 Insert to App", 
                                  command=self.insert_translation,
                                  bg='#4facfe', fg='white', bd=0, padx=15, pady=8,
                                  font=('Segoe UI', 9, 'bold'))
        self.insert_btn.pack(side='left', padx=(0, 5))
        
        self.copy_btn = tk.Button(btn_frame, text="📄 Copy", 
                                command=self.copy_translation,
                                bg='#e2e8f0', fg='#64748b', bd=0, padx=15, pady=8,
                                font=('Segoe UI', 9))
        self.copy_btn.pack(side='left', padx=5)
        
        self.clear_btn = tk.Button(btn_frame, text="🗑️ Clear", 
                                 command=self.clear_all,
                                 bg='#e2e8f0', fg='#64748b', bd=0, padx=15, pady=8,
                                 font=('Segoe UI', 9))
        self.clear_btn.pack(side='left', padx=5)
        
        # Auto-detect section (initially hidden)
        self.autodetect_frame = tk.Frame(main_frame, bg='#f0f2f5')
        
        # Status indicator
        status_frame = tk.Frame(main_frame, bg='#f0f2f5')
        status_frame.pack(fill='x', pady=(0, 15))
        
        self.status_indicator = tk.Label(status_frame, text="●", fg='#10b981', 
                                       bg='#f0f2f5', font=('Segoe UI', 12))
        self.status_indicator.pack(side='left')
        
        self.status_text = tk.Label(status_frame, text="Ready - Translation mode", 
                                   bg='#f0f2f5', fg='#64748b', font=('Segoe UI', 9))
        self.status_text.pack(side='left', padx=(5, 0))
        
        # Hotkeys info
        hotkey_frame = tk.Frame(main_frame, bg='#f8fafc', relief='solid', bd=1)
        hotkey_frame.pack(fill='x', pady=(0, 15))
        
        hotkey_text = ("Hotkeys: Ctrl+Shift+T (Translate & Insert) • "
                      "Ctrl+Shift+L (Toggle Mode) • Ctrl+Shift+C (Copy) • "
                      "Auto-play: Enable in Settings below")
        tk.Label(hotkey_frame, text=hotkey_text, bg='#f8fafc', fg='#64748b', 
                font=('Segoe UI', 8), wraplength=400).pack(padx=10, pady=5)
        
        # Settings section
        self.create_settings_section(main_frame)
        
    def create_settings_section(self, parent):
        """Create settings panel"""
        settings_frame = tk.LabelFrame(parent, text="Settings", bg='#f8fafc', 
                                     fg='#4a5568', font=('Segoe UI', 9, 'bold'))
        settings_frame.pack(fill='x', pady=(0, 10))
        
        # Auto-insert setting
        auto_frame = tk.Frame(settings_frame, bg='#f8fafc')
        auto_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(auto_frame, text="Auto-insert translations", bg='#f8fafc', 
                font=('Segoe UI', 9)).pack(side='left')
        
        self.auto_insert_var = tk.BooleanVar(value=self.settings['auto_insert'])
        auto_check = tk.Checkbutton(auto_frame, variable=self.auto_insert_var, 
                                  bg='#f8fafc', command=self.update_settings)
        auto_check.pack(side='right')
        
        # Clipboard monitor setting
        clip_frame = tk.Frame(settings_frame, bg='#f8fafc')
        clip_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(clip_frame, text="Monitor clipboard", bg='#f8fafc', 
                font=('Segoe UI', 9)).pack(side='left')
        
        self.clip_monitor_var = tk.BooleanVar(value=self.settings['clipboard_monitor'])
        clip_check = tk.Checkbutton(clip_frame, variable=self.clip_monitor_var, 
                                  bg='#f8fafc', command=self.update_settings)
        clip_check.pack(side='right')
        
        # Always on top setting
        top_frame = tk.Frame(settings_frame, bg='#f8fafc')
        top_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(top_frame, text="Always on top", bg='#f8fafc', 
                font=('Segoe UI', 9)).pack(side='left')
        
        self.always_top_var = tk.BooleanVar(value=self.settings['always_on_top'])
        top_check = tk.Checkbutton(top_frame, variable=self.always_top_var, 
                                 bg='#f8fafc', command=self.toggle_always_on_top)
        top_check.pack(side='right')
        
        # Auto-play audio setting
        audio_frame = tk.Frame(settings_frame, bg='#f8fafc')
        audio_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(audio_frame, text="Auto-play translation audio", bg='#f8fafc', 
                font=('Segoe UI', 9)).pack(side='left')
        
        self.auto_play_var = tk.BooleanVar(value=self.settings['auto_play_audio'])
        audio_check = tk.Checkbutton(audio_frame, variable=self.auto_play_var, 
                                   bg='#f8fafc', command=self.update_settings)
        audio_check.pack(side='right')
        
    def setup_hotkeys(self):
        """Setup global hotkeys"""
        try:
            import keyboard
            keyboard.add_hotkey('ctrl+shift+t', self.hotkey_translate_insert)
            keyboard.add_hotkey('ctrl+shift+l', self.hotkey_toggle_mode)
            keyboard.add_hotkey('ctrl+shift+c', self.hotkey_copy)
        except ImportError:
            print("keyboard package not found - hotkeys disabled")
        except Exception as e:
            print(f"Could not register hotkeys: {e}")
            
    def init_database(self):
        """Initialize SQLite database for translation history"""
        if not os.path.exists('translator_data'):
            os.makedirs('translator_data')
            
        self.db_path = os.path.join('translator_data', 'history.db')
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_text TEXT,
                translated_text TEXT,
                source_lang TEXT,
                target_lang TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def save_translation(self, source, translated, source_lang, target_lang):
        """Save translation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO translations (source_text, translated_text, source_lang, target_lang)
            VALUES (?, ?, ?, ?)
        ''', (source, translated, source_lang, target_lang))
        
        conn.commit()
        conn.close()
        
    def get_language_code(self, language_name):
        """Get language code from language name"""
        for code, name in self.languages.items():
            if name == language_name:
                return code
        return 'en'
        
    def translate_text(self, text, source_lang, target_lang):
        """Translate text using Google Translate"""
        try:
            if not text.strip():
                return ""
            
            if self.translator is None:
                return "Translation service not available"
            
            # Handle auto-detect for source language
            if source_lang == 'auto':
                source_lang = None
                
            # Use googletrans for translation
            result = self.translator.translate(text, src=source_lang, dest=target_lang)
            return result.text
            
        except Exception as e:
            print(f"Translation error: {e}")
            # Try with auto-detect if source language failed
            if source_lang and source_lang != 'auto':
                try:
                    result = self.translator.translate(text, src=None, dest=target_lang)
                    return result.text
                except:
                    pass
            return f"Translation error: {str(e)}"
            
    def detect_language(self, text):
        """Detect language of text"""
        try:
            from langdetect import detect
            detected_lang = detect(text)
            return detected_lang
        except ImportError:
            print("langdetect package not found")
            return 'en'
        except:
            return 'en'
            
    def on_text_change(self, event=None):
        """Handle text input changes"""
        if self.current_mode == 'translate':
            # Debounce translation to avoid too many API calls
            if hasattr(self, 'translate_timer'):
                self.root.after_cancel(self.translate_timer)
            self.translate_timer = self.root.after(500, self.perform_translation)
            
    def perform_translation(self):
        """Perform the actual translation"""
        input_text = self.input_text.get(1.0, tk.END).strip()
        
        input_text = self.input_text.get(1.0, tk.END).strip()
        
        if not input_text:
            self.output_text.config(state='normal')
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(1.0, "Translation will appear here...")
            self.output_text.config(state='disabled')
            return
            
        source_lang = self.get_language_code(self.from_lang.get())
        target_lang = self.get_language_code(self.to_lang.get())
        
        # Show translation in progress
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, "Translating...")
        self.output_text.config(state='disabled')
        self.update_status("Translating...")
        
        # Perform translation in background thread
        def translate_in_background():
            translated = self.translate_text(input_text, source_lang, target_lang)
            
            # Update GUI in main thread
            self.root.after(0, lambda: self.update_translation_output(translated, input_text, source_lang, target_lang))
            
        threading.Thread(target=translate_in_background, daemon=True).start()
        
    def update_translation_output(self, translated, source_text, source_lang, target_lang):
        """Update translation output in GUI"""
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, translated)
        self.output_text.config(state='disabled')
        
        # Enable play button if translation is available and audio is enabled
        if translated and not translated.startswith("Translation error") and self.audio_enabled:
            self.play_btn.config(state='normal', bg='#4facfe', fg='white')
            
            # Auto-play if setting is enabled
            if self.settings.get('auto_play_audio', False):
                self.update_status("Auto-playing translation...")
                # Delay auto-play slightly to let UI update
                self.root.after(500, self.auto_play_translation)
        else:
            self.play_btn.config(state='disabled', bg='#e2e8f0', fg='#64748b')
        
        # Save to database
        if translated and not translated.startswith("Translation error"):
            self.save_translation(source_text, translated, source_lang, target_lang)
            
        if not self.settings.get('auto_play_audio', False):
            self.update_status(f"Translated to {self.languages.get(target_lang, target_lang)}")
        
    def set_mode(self, mode):
        """Switch between translate and listen modes"""
        self.current_mode = mode
        
        if mode == 'translate':
            self.translate_btn.config(bg='#4facfe', fg='white', font=('Segoe UI', 10, 'bold'))
            self.listen_btn.config(bg='#e2e8f0', fg='#64748b', font=('Segoe UI', 10))
            
            self.translation_frame.pack(fill='both', expand=True, pady=(0, 15))
            self.autodetect_frame.pack_forget()
            
            self.update_status("Ready - Translation mode")
            
        else:  # listen mode
            self.listen_btn.config(bg='#4facfe', fg='white', font=('Segoe UI', 10, 'bold'))
            self.translate_btn.config(bg='#e2e8f0', fg='#64748b', font=('Segoe UI', 10))
            
            self.translation_frame.pack_forget()
            self.create_autodetect_interface()
            self.autodetect_frame.pack(fill='both', expand=True, pady=(0, 15))
            
            self.update_status("Listening for incoming text...")
            
    def create_autodetect_interface(self):
        """Create auto-detection interface"""
        # Clear existing widgets
        for widget in self.autodetect_frame.winfo_children():
            widget.destroy()
            
        # Listening indicator
        listen_frame = tk.Frame(self.autodetect_frame, bg='#fef3cd', relief='solid', bd=1)
        listen_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(listen_frame, text="🎯 Auto-Detection Mode Active", 
                bg='#fef3cd', fg='#92400e', font=('Segoe UI', 10, 'bold')).pack(pady=10)
        
        tk.Label(listen_frame, text="Monitoring clipboard for incoming text...", 
                bg='#fef3cd', fg='#92400e', font=('Segoe UI', 9)).pack(pady=(0, 10))
        
        # Detected text area
        self.detected_frame = tk.Frame(self.autodetect_frame, bg='#f0f9ff', relief='solid', bd=1)
        
        tk.Label(self.detected_frame, text="Detected Text:", bg='#f0f9ff', 
                font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        
        # Detected text area (larger)
        tk.Label(self.detected_frame, text="Detected Text:", bg='#f0f9ff', 
                font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.detected_text = scrolledtext.ScrolledText(self.detected_frame, height=4, 
                                                      font=('Segoe UI', 9), wrap='word')
        self.detected_text.pack(fill='x', padx=10, pady=(0, 10))
        self.detected_text.config(state='disabled')
        
        # Auto-translation header with play button
        auto_header = tk.Frame(self.detected_frame, bg='#f0f9ff')
        auto_header.pack(fill='x', padx=10, pady=(0, 5))
        
        tk.Label(auto_header, text="Translation:", bg='#f0f9ff', 
                font=('Segoe UI', 10, 'bold')).pack(side='left')
        
        self.auto_play_btn = tk.Button(auto_header, text="🔊", 
                                     command=self.play_auto_translation_audio,
                                     bg='#e2e8f0', fg='#64748b', bd=0, padx=8, pady=2,
                                     font=('Segoe UI', 12), state='disabled')
        self.auto_play_btn.pack(side='right')
        
        self.auto_translation = scrolledtext.ScrolledText(self.detected_frame, height=4, 
                                                         font=('Segoe UI', 9), wrap='word', 
                                                         bg='#f8fffe')
        self.auto_translation.pack(fill='x', padx=10, pady=(0, 10))
        self.auto_translation.config(state='disabled')
        
        # Auto-detect action buttons
        auto_btn_frame = tk.Frame(self.detected_frame, bg='#f0f9ff')
        auto_btn_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.auto_insert_btn = tk.Button(auto_btn_frame, text="Insert Translation", 
                                       command=self.insert_auto_translation,
                                       bg='#4facfe', fg='white', bd=0, padx=12, pady=6,
                                       font=('Segoe UI', 9, 'bold'))
        self.auto_insert_btn.pack(side='left', padx=(0, 5))
        
        self.auto_copy_btn = tk.Button(auto_btn_frame, text="Copy", 
                                     command=self.copy_auto_translation,
                                     bg='#e2e8f0', fg='#64748b', bd=0, padx=12, pady=6,
                                     font=('Segoe UI', 9))
        self.auto_copy_btn.pack(side='left', padx=5)
        
    def start_clipboard_monitor(self):
        """Start monitoring clipboard for changes"""
        def monitor_clipboard():
            # Wait for complete initialization
            while not hasattr(self, 'current_mode') or not hasattr(self, 'last_clipboard') or not hasattr(self, 'settings'):
                time.sleep(0.1)
                
            while True:
                try:
                    if (hasattr(self, 'current_mode') and 
                        hasattr(self, 'settings') and 
                        hasattr(self, 'last_clipboard') and
                        self.current_mode == 'listen' and 
                        self.settings['clipboard_monitor']):
                        
                        try:
                            import pyperclip
                            current_clipboard = pyperclip.paste()
                            
                            if (current_clipboard != self.last_clipboard and 
                                current_clipboard.strip() and 
                                len(current_clipboard) > 5):
                                
                                self.last_clipboard = current_clipboard
                                
                                # Detect if text is not in English
                                detected_lang = self.detect_language(current_clipboard)
                                
                                if detected_lang != 'en':
                                    self.root.after(0, lambda text=current_clipboard, lang=detected_lang: 
                                                   self.process_detected_text(text, lang))
                                    
                        except Exception as e:
                            print(f"Inner clipboard error: {e}")
                            
                except Exception as e:
                    # Only print error if not an initialization issue
                    if hasattr(self, 'current_mode'):
                        print(f"Clipboard monitoring error: {e}")
                        
                time.sleep(1)  # Check every second
                
        threading.Thread(target=monitor_clipboard, daemon=True).start()
        
    def process_detected_text(self, text, detected_lang):
        """Process detected foreign language text"""
        if not hasattr(self, 'detected_frame'):
            return
            
        # Show detected text
        self.detected_frame.pack(fill='x', pady=(0, 15))
        
        self.detected_text.config(state='normal')
        self.detected_text.delete(1.0, tk.END)
        self.detected_text.insert(1.0, text)
        self.detected_text.config(state='disabled')
        
        # Show translation in progress
        self.auto_translation.config(state='normal')
        self.auto_translation.delete(1.0, tk.END)
        self.auto_translation.insert(1.0, "Translating...")
        self.auto_translation.config(state='disabled')
        
        lang_name = self.languages.get(detected_lang, detected_lang)
        self.update_status(f"Detected {lang_name} text")
        
        # Translate in background
        def translate_detected():
            translated = self.translate_text(text, detected_lang, 'en')
            self.root.after(0, lambda: self.update_auto_translation(translated, text, detected_lang))
            
        threading.Thread(target=translate_detected, daemon=True).start()
        
    def update_auto_translation(self, translated, source_text, source_lang):
        """Update auto-translation result"""
        self.auto_translation.config(state='normal')
        self.auto_translation.delete(1.0, tk.END)
        self.auto_translation.insert(1.0, translated)
        self.auto_translation.config(state='disabled')
        
        # Enable play button for auto-translation
        if translated and not translated.startswith("Translation error") and self.audio_enabled:
            self.auto_play_btn.config(state='normal', bg='#4facfe', fg='white')
            
            # Auto-play if setting is enabled
            if self.settings.get('auto_play_audio', False):
                self.update_status("Auto-playing auto-translation...")
                # Delay auto-play slightly to let UI update
                self.root.after(500, self.auto_play_auto_translation)
        else:
            self.auto_play_btn.config(state='disabled', bg='#e2e8f0', fg='#64748b')
        
        # Save to database
        if translated and not translated.startswith("Translation error"):
            self.save_translation(source_text, translated, source_lang, 'en')
            
        # Auto-insert if enabled
        if self.settings['auto_insert']:
            self.root.after(1000, self.insert_auto_translation)
            
        if not self.settings.get('auto_play_audio', False):
            self.update_status("Auto-translation ready")
        
    def swap_languages(self):
        """Swap source and target languages"""
        from_lang = self.from_lang.get()
        to_lang = self.to_lang.get()
        
        self.from_lang.set(to_lang)
        self.to_lang.set(from_lang)
        
        # Re-translate if there's text
        if self.input_text.get(1.0, tk.END).strip():
            self.perform_translation()
            
    def insert_translation(self):
        """Insert translation to active application"""
        translation = self.output_text.get(1.0, tk.END).strip()
        if translation and translation != "Translation will appear here...":
            self.insert_text_to_active_window(translation)
            self.update_status("Translation inserted into active application")
            
    def insert_auto_translation(self):
        """Insert auto-translation to active application"""
        if hasattr(self, 'auto_translation'):
            translation = self.auto_translation.get(1.0, tk.END).strip()
            if translation and translation != "Translating...":
                self.insert_text_to_active_window(translation)
                self.update_status("Auto-translation inserted into active application")
                
    def insert_text_to_active_window(self, text):
        """Insert text into the currently active window"""
        try:
            # Copy text to clipboard first
            import pyperclip
            pyperclip.copy(text)
            
            # Try to use keyboard for pasting
            try:
                import keyboard
                time.sleep(0.1)  # Small delay
                keyboard.send('ctrl+v')
            except ImportError:
                # Fallback: just copy to clipboard
                messagebox.showinfo("Translation Ready", 
                                  f"Translation copied to clipboard:\n\n{text[:100]}{'...' if len(text) > 100 else ''}\n\nPaste with Ctrl+V")
            
        except Exception as e:
            # Ultimate fallback: show message with text
            messagebox.showinfo("Translation Ready", 
                              f"Translation ready:\n\n{text[:200]}{'...' if len(text) > 200 else ''}\n\nPlease copy manually if needed.")
            
    def copy_translation(self):
        """Copy current translation to clipboard"""
        translation = self.output_text.get(1.0, tk.END).strip()
        if translation and translation != "Translation will appear here...":
            try:
                import pyperclip
                pyperclip.copy(translation)
                self.update_status("Translation copied to clipboard")
            except ImportError:
                # Fallback: show text to copy manually
                messagebox.showinfo("Translation", f"Copy this text:\n\n{translation}")
                self.update_status("Translation ready to copy")
            
    def copy_auto_translation(self):
        """Copy auto-translation to clipboard"""
        if hasattr(self, 'auto_translation'):
            translation = self.auto_translation.get(1.0, tk.END).strip()
            if translation and translation != "Translating...":
                try:
                    import pyperclip
                    pyperclip.copy(translation)
                    self.update_status("Auto-translation copied to clipboard")
                except ImportError:
                    messagebox.showinfo("Auto-Translation", f"Copy this text:\n\n{translation}")
                    self.update_status("Auto-translation ready to copy")
                
    def clear_all(self):
        """Clear all text areas"""
        self.input_text.delete(1.0, tk.END)
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, "Translation will appear here...")
        self.output_text.config(state='disabled')
        # Disable play button
        self.play_btn.config(state='disabled', bg='#e2e8f0', fg='#64748b')
        self.update_status("Cleared")
        
    def minimize_window(self):
        """Minimize window to taskbar"""
        self.root.iconify()
        
    def update_settings(self):
        """Update settings based on checkboxes"""
        self.settings['auto_insert'] = self.auto_insert_var.get()
        self.settings['clipboard_monitor'] = self.clip_monitor_var.get()
        self.settings['auto_play_audio'] = self.auto_play_var.get()
        
        # Update status message
        if self.auto_play_var.get():
            self.update_status("Auto-play audio enabled")
        else:
            self.update_status("Auto-play audio disabled")
        
    def toggle_always_on_top(self):
        """Toggle always on top setting"""
        self.settings['always_on_top'] = self.always_top_var.get()
        self.root.wm_attributes("-topmost", self.settings['always_on_top'])
        
    def update_status(self, message):
        """Update status message"""
        self.status_text.config(text=message)
        
        # Auto-reset status after 3 seconds
        self.root.after(3000, self.reset_status)
        
    def reset_status(self):
        """Reset status to default"""
        if self.current_mode == 'translate':
            self.status_text.config(text="Ready - Translation mode")
        else:
            self.status_text.config(text="Listening for incoming text...")
            
    def text_to_speech(self, text, language='en'):
        """Convert text to speech and return audio file path"""
        try:
            if not text.strip():
                return None
            
            # Import gTTS with error handling
            try:
                from gtts import gTTS
            except ImportError:
                print("gTTS package not available")
                return None
                
            # Create TTS object
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.close()
            
            # Save audio to temporary file
            tts.save(temp_file.name)
            
            return temp_file.name
            
        except Exception as e:
            print(f"TTS error: {e}")
            return None
    
    def play_audio_file(self, file_path):
        """Play audio file using pygame"""
        try:
            if not file_path or not os.path.exists(file_path):
                return False
                
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            return True
            
        except Exception as e:
            print(f"Audio playback error: {e}")
            return False
    
    def play_translation_audio(self):
        """Play audio for current translation"""
        translation = self.output_text.get(1.0, tk.END).strip()
        if not translation or translation == "Translation will appear here...":
            return
            
        # Get target language
        target_lang = self.get_language_code(self.to_lang.get())
        
        # Update button to show loading
        self.play_btn.config(text="🔄", state='disabled')
        self.update_status("Generating audio...")
        
        def generate_and_play():
            # Generate audio file
            audio_file = self.text_to_speech(translation, target_lang)
            
            if audio_file:
                # Update UI and play audio
                self.root.after(0, lambda: self.play_audio_and_update_ui(audio_file, self.play_btn, "Translation audio"))
            else:
                # Reset button if failed
                self.root.after(0, lambda: self.reset_play_button(self.play_btn))
                
        threading.Thread(target=generate_and_play, daemon=True).start()
    
    def play_auto_translation_audio(self):
        """Play audio for auto-translation"""
        if not hasattr(self, 'auto_translation'):
            return
            
        translation = self.auto_translation.get(1.0, tk.END).strip()
        if not translation or translation == "Translating...":
            return
        
        # Auto-translations are always in English
        self.auto_play_btn.config(text="🔄", state='disabled')
        self.update_status("Generating audio...")
        
        def generate_and_play():
            audio_file = self.text_to_speech(translation, 'en')
            
            if audio_file:
                self.root.after(0, lambda: self.play_audio_and_update_ui(audio_file, self.auto_play_btn, "Auto-translation audio"))
            else:
                self.root.after(0, lambda: self.reset_play_button(self.auto_play_btn))
                
        threading.Thread(target=generate_and_play, daemon=True).start()
    
    def play_audio_and_update_ui(self, audio_file, button, description):
        """Play audio and update UI"""
        # Clean up previous audio file
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            try:
                os.unlink(self.current_audio_file)
            except:
                pass
        
        # Play new audio
        if self.play_audio_file(audio_file):
            self.current_audio_file = audio_file
            self.update_status(f"Playing {description}")
            
            # Monitor playback and reset button when done
            def monitor_playback():
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                # Reset button when playback is done
                self.root.after(0, lambda: self.reset_play_button(button))
                
            threading.Thread(target=monitor_playback, daemon=True).start()
        else:
            self.reset_play_button(button)
    
    def auto_play_translation(self):
        """Auto-play the main translation"""
        if self.settings.get('auto_play_audio', False):
            self.play_translation_audio()
    
    def auto_play_auto_translation(self):
        """Auto-play the auto-detected translation"""
        if self.settings.get('auto_play_audio', False):
            self.play_auto_translation_audio()

    def reset_play_button(self, button):
        """Reset play button to normal state"""
        button.config(text="🔊", state='normal', bg='#4facfe', fg='white')
        self.update_status("Audio ready")

    # Hotkey handlers
    def hotkey_translate_insert(self):
        """Hotkey: Translate and insert"""
        if self.current_mode == 'translate':
            self.insert_translation()
        else:
            self.insert_auto_translation()
            
    def hotkey_toggle_mode(self):
        """Hotkey: Toggle between modes"""
        new_mode = 'listen' if self.current_mode == 'translate' else 'translate'
        self.set_mode(new_mode)
        
    def hotkey_copy(self):
        """Hotkey: Copy translation"""
        if self.current_mode == 'translate':
            self.copy_translation()
        else:
            self.copy_auto_translation()
            
    def run(self):
        """Start the application"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
            
    def on_closing(self):
        """Handle application closing"""
        try:
            # Clean up audio file
            if hasattr(self, 'current_audio_file') and self.current_audio_file and os.path.exists(self.current_audio_file):
                try:
                    pygame.mixer.music.stop()
                    os.unlink(self.current_audio_file)
                except:
                    pass
            
            # Quit pygame mixer
            if hasattr(self, 'audio_enabled') and self.audio_enabled:
                pygame.mixer.quit()
            
            # Unhook keyboard listeners
            import keyboard
            keyboard.unhook_all()
        except:
            pass
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    # Install required packages if not available
    required_packages = [
        'googletrans==4.0.0rc1',
        'pyperclip',
        'pywin32',
        'keyboard',
        'langdetect',
        'requests',
        'pygame',
        'gTTS'
    ]
    
    print("Universal Translation Widget")
    print("============================")
    print("Make sure you have installed the required packages:")
    for package in required_packages:
        print(f"  pip install {package}")
    print("\nStarting application...\n")
    
    try:
        app = UniversalTranslator()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        print("\nPlease make sure all required packages are installed:")
        for package in required_packages:
            print(f"  pip install {package}")
        input("Press Enter to exit...")
