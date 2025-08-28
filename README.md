# 🌐 Universal Translation Widget

A powerful, feature-rich desktop translation application that seamlessly integrates with all Windows applications. Translate text in real-time, auto-detect foreign languages, and hear translations with natural-sounding text-to-speech - all with global hotkeys and smart automation.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🔄 **Dual Translation Modes**
- **Manual Translation**: Type in any language, get instant translations
- **Auto-Detection**: Automatically detects and translates foreign text from your clipboard

### 🌍 **25+ Languages Supported**
English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese, Arabic, Hindi, Dutch, Swedish, Norwegian, Danish, Finnish, Polish, Czech, Slovak, Hungarian, Romanian, Bulgarian, Croatian, and more.

### 🎵 **Text-to-Speech Audio**
- High-quality Google Text-to-Speech integration
- Natural pronunciation in target languages
- Auto-play option for hands-free operation
- Manual audio controls with visual feedback

### ⚡ **Windows Integration**
- **Direct text insertion** into any Windows application (Word, WhatsApp, Facebook, etc.)
- **Global hotkeys** that work system-wide
- **Clipboard monitoring** for automatic foreign text detection
- **Always-on-top** option for constant accessibility

### 🎛️ **Smart Automation**
- Auto-insert translations into active applications
- Auto-play audio when translations complete
- Background clipboard monitoring
- Real-time translation as you type

### 💾 **Translation History**
- SQLite database stores all translation history
- Easy retrieval of past translations
- Organized by source/target language pairs

## 🚀 Installation

### Prerequisites
- **Python 3.8 or higher**
- **Windows Operating System**

### Install Dependencies

```bash
pip install googletrans==4.0.0rc1 pyperclip langdetect keyboard pywin32 pygame gTTS
```

### Download and Run

1. **Download** the `universal_translator.py` file
2. **Open Command Prompt** in the download folder
3. **Run the application**:
   ```bash
   python universal_translator.py
   ```

## 🎯 Quick Start Guide

### Basic Translation
1. **Launch** the application
2. **Select languages** in the dropdown menus
3. **Type your text** in the input area
4. **View translation** in the output area
5. **Click "Insert to App"** to paste into any Windows application

### Auto-Detection Mode
1. **Click "Auto-Detect"** mode button
2. **Copy foreign text** from anywhere (websites, emails, messages)
3. **Translation appears automatically** in English
4. **Audio plays** (if auto-play is enabled)

### Audio Features
1. **Click the 🔊 button** next to any translation to hear it spoken
2. **Enable "Auto-play translation audio"** in settings for automatic playback
3. **Hear perfect pronunciation** in the target language

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+T` | Translate and insert into active app |
| `Ctrl+Shift+L` | Toggle between Translation/Auto-Detection modes |
| `Ctrl+Shift+C` | Copy current translation to clipboard |

## ⚙️ Settings

### Available Options
- **Auto-insert translations**: Automatically paste translations into active applications
- **Monitor clipboard**: Enable/disable automatic detection of foreign text
- **Always on top**: Keep the widget visible above other windows
- **Auto-play translation audio**: Automatically play audio when translations complete

### Accessing Settings
Settings are located in the bottom panel of the application window. Changes take effect immediately.

## 🖥️ Interface Overview

### Translation Mode
```
┌─────────────────────────────────────────┐
│ 🌐 Universal Translator            [−] │
├─────────────────────────────────────────┤
│ [Translate] [Auto-Detect]              │
│                                         │
│ From: English  ⇄  To: Spanish         │
│                                         │
│ Input Text:                            │
│ ┌─────────────────────────────────────┐ │
│ │ Type your message here...           │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Translation:                      🔊   │
│ ┌─────────────────────────────────────┐ │
│ │ Translation will appear here...     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [📋 Insert to App] [📄 Copy] [🗑️ Clear] │
└─────────────────────────────────────────┘
```

### Auto-Detection Mode
```
┌─────────────────────────────────────────┐
│ 🎯 Auto-Detection Mode Active          │
│ Monitoring clipboard for incoming text │
│                                         │
│ Detected Text:                         │
│ ┌─────────────────────────────────────┐ │
│ │ Hola, ¿cómo estás?                 │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Translation:                      🔊   │
│ ┌─────────────────────────────────────┐ │
│ │ Hello, how are you?                 │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [Insert Translation] [Copy]            │
└─────────────────────────────────────────┘
```

## 🔧 Technical Details

### Architecture
- **GUI Framework**: tkinter (built-in Python GUI library)
- **Translation Engine**: Google Translate via googletrans library
- **Language Detection**: langdetect library
- **Text-to-Speech**: Google Text-to-Speech (gTTS)
- **Audio Playback**: pygame mixer
- **Windows Integration**: pywin32 for system-level operations
- **Database**: SQLite for translation history

### File Structure
```
universal_translator.py     # Main application file
translator_data/           # Created on first run
├── history.db            # SQLite database for translation history
└── temp_audio_*.mp3      # Temporary audio files (auto-deleted)
```

### Performance
- **Translation Speed**: ~1-2 seconds per translation
- **Audio Generation**: ~2-3 seconds for TTS generation
- **Memory Usage**: ~50-100MB during operation
- **Clipboard Monitoring**: 1-second intervals for optimal performance

## 🛠️ Troubleshooting

### Common Issues

**"Translation service not available"**
- Check internet connection (Google Translate requires internet)
- Verify googletrans package is installed correctly

**"Audio playback not available"**
- Install pygame: `pip install pygame`
- Install gTTS: `pip install gTTS`
- Check system audio settings

**Global hotkeys not working**
- Run as administrator if keyboard package installation failed
- Some antivirus software may block global hotkey registration

**Clipboard monitoring errors**
- Ensure pyperclip is installed: `pip install pyperclip`
- Check Windows clipboard permissions

### Package Installation Issues

If you encounter package installation errors, try:

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install packages individually
pip install googletrans==4.0.0rc1
pip install pyperclip
pip install langdetect
pip install keyboard
pip install pywin32
pip install pygame
pip install gTTS
```

## 📋 Requirements

### Python Packages
- `googletrans==4.0.0rc1` - Google Translate integration
- `pyperclip` - Clipboard operations
- `langdetect` - Language detection
- `keyboard` - Global hotkey support
- `pywin32` - Windows API integration
- `pygame` - Audio playback
- `gTTS` - Google Text-to-Speech

### System Requirements
- **OS**: Windows 10/11 (tested)
- **Python**: 3.8 or higher
- **RAM**: 512MB minimum
- **Storage**: 100MB for installation and cache
- **Internet**: Required for translation and TTS services

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Reporting Issues
- Use the GitHub issue tracker
- Include error messages and steps to reproduce
- Mention your Python version and OS

### Feature Requests
- Check existing issues first
- Describe the feature and use case
- Consider implementation complexity

### Pull Requests
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Universal Translation Widget

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 🙏 Acknowledgments

- **Google Translate** - Translation services
- **Google Text-to-Speech** - Audio generation
- **Python Community** - Amazing libraries and support
- **Contributors** - Thank you for making this project better

## 📞 Support

### Getting Help
- **Documentation**: Read this README thoroughly
- **Issues**: Check [existing issues](https://github.com/yourrepo/issues) first
- **Community**: Join discussions in the issues section

### Contact
- **GitHub Issues**: For bug reports and feature requests
- **Email**: [your-email@example.com] for private inquiries

---

**Made with ❤️ for seamless cross-language communication**

*Bridging language barriers, one translation at a time.*
