# MyVoiceTTS

A local Text-to-Speech application that clones my own voice using [F5-TTS](https://github.com/SWivid/F5-TTS), with a Streamlit web interface. Built for generating narration audio from text or documents — ideal for PPT presentations, voiceovers, and more.

Created by VSCode+ClaudeCode

## Features

- **Voice cloning** — uses a short reference audio clip of your voice (10–30 seconds)
- **Text input** — type or paste text directly
- **File upload** — supports `.txt` and `.docx` documents with auto-parsed preview
- **Editable preview** — edit parsed document text before generating
- **Speed control** — adjust speech rate from 0.6× to 1.5×
- **In-browser playback** — listen and download generated audio instantly
- **Session history** — review and re-download all audio generated in the current session
- **Apple Silicon support** — runs on MPS (M1/M2/M3) or CPU

## Requirements

- Python 3.9+
- macOS (Apple Silicon recommended for speed)

## Installation

```bash
git clone https://github.com/your-username/myvoicetts.git
cd myvoicetts
pip install -r requirements.txt
```

> The F5-TTS model (~1.5 GB) will be downloaded automatically on first run.

## Usage

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

### Steps

1. **Upload reference audio** — record 10–30 seconds of your own voice in a quiet environment, save as WAV, and upload via the sidebar
2. **Enter reference text** — type out what you said in the reference audio (improves quality)
3. **Input text** — type directly or upload a `.txt` / `.docx` file
4. **Adjust speed** — use the sidebar slider if needed
5. **Generate** — click the button and wait for synthesis to complete
6. **Play or download** — the audio player appears automatically after generation

## Project Structure

```
myvoicetts/
├── app.py            # Streamlit frontend
├── tts_engine.py     # F5-TTS wrapper
├── requirements.txt  # Python dependencies
├── reference/        # Place your reference audio here
└── outputs/          # Generated audio files (auto-created)
```

## Tips for Best Results

- Record reference audio in a quiet room with a decent microphone
- Speak naturally at your normal pace in the reference clip
- Provide the reference text transcript for better voice matching
- For long documents, consider splitting into sections for more consistent output

## License

MIT
