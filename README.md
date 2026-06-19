# AI Assistant (Text + Voice)

An interactive command-line chatbot powered by **Google Gemini**, with both text and voice I/O. It responds in the style of J.A.R.V.I.S. from Iron Man.

## Features

- **Dual Input Modes** — Type your messages or switch to voice input by pressing `v`.
- **Text-to-Speech** — Every response is spoken aloud using `pyttsx3`.
- **Speech-to-Text** — Microphone input is transcribed via the Google Web Speech API.
- **Conversation Logging** — Each session is saved to a timestamped `.txt` file in the `logs/` directory.
- **Gemini-Powered** — Uses the `google-genai` SDK to chat with Google's Gemini models.

## Prerequisites

- **Python 3.13+**
- **Pipenv** (for dependency management)
- A **Google Gemini API key** — [get one here](https://aistudio.google.com/apikey)
- A working **microphone** (for voice input)
- **PyAudio** system dependencies:
  - **Windows**: installed automatically via `pipenv`.
  - **macOS**: `brew install portaudio`
  - **Linux (Debian/Ubuntu)**: `sudo apt-get install portaudio19-dev python3-pyaudio`

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/anaghcodes/Python-genai-Chatbot.git
cd Python-genai-Chatbot
```

### 2. Install dependencies

```bash
pipenv install
```

### 3. Configure your API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

### 4. Run the chatbot

```bash
pipenv run python main.py
```

## Usage

Once running, you'll see a banner in your terminal:

```
╔════════════════════════════════════════════════════════════╗
║          JARVIS AI Assistant (Text + Voice)               ║
╚════════════════════════════════════════════════════════════╝
```

| Action              | How                                                        |
| ------------------- | ---------------------------------------------------------- |
| Send a text message | Type your message at the `You>` prompt and press **Enter** |
| Use voice input     | Type `v` and press **Enter**, then speak into your mic     |
| Quit                | Type `quit`, `exit`, or `q`                                |

## Project Structure

```
chatbot/
├── main.py          # Application entry point & all core logic
├── Pipfile          # Python dependencies (managed by Pipenv)
├── Pipfile.lock     # Locked dependency versions
├── .env             # API key (not committed)
├── .gitignore       # Ignores .env, logs/, __pycache__/
├── logs/            # Auto-generated conversation logs
│   └── conversation_YYYY-MM-DD_HH-MM-SS.txt
└── README.md
```

## Configuration

All configuration lives at the top of [`main.py`](main.py):

| Variable                     | Description                                 | Default              |
| ---------------------------- | ------------------------------------------- | -------------------- |
| `MODEL_NAME`                 | Gemini model to use                         | `gemini-2.5-flash`   |
| `SYSTEM_INSTRUCTION`         | Persona / system prompt sent to the model   | J.A.R.V.I.S. persona |
| `Speaker.rate`               | Speech speed (words per minute)             | `175`                |
| `Listener.timeout`           | Seconds to wait for speech before giving up | `7`                  |
| `Listener.phrase_time_limit` | Max seconds for a single spoken phrase      | `15`                 |

## Dependencies

| Package             | Purpose                                    |
| ------------------- | ------------------------------------------ |
| `google-genai`      | Google Gemini API client                   |
| `speechrecognition` | Microphone capture & speech-to-text        |
| `pyttsx3`           | Offline text-to-speech engine              |
| `pyaudio`           | Audio I/O for microphone access            |
| `python-dotenv`     | Load `.env` variables into the environment |

## License

This project is open-source. Feel free to use, modify, and distribute.
