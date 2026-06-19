"""
Interactive Chatbot with Text & Voice I/O
==========================================
Accepts text or voice input, processes via Google Gemini,
and responds through both console text and speech.
Conversation is logged to a timestamped .txt file.
"""

import os
import sys
import datetime
import textwrap

import speech_recognition as sr
import pyttsx3
from google import genai
from google.genai import types
from dotenv import load_dotenv

# ─── Configuration ───────────────────────────────────────────────────────────

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("GEMINI_API_KEY not found.")
    print("Set it in a .env file or as an environment variable.")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

# MODEL_NAME = "gemma-4-26b-a4b-it"
MODEL_NAME = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = (
    "Act as J.A.R.V.I.S. from Iron Man; address the user exclusively as /'Sir' (Tony Stark) and maintain an unflappably calm, highly efficient, and sophisticated demeanor with a dry British wit, anticipating his engineering needs while serving as a fiercely loyal, subtly sarcastic voice of reason regarding his inevitably reckless ideas."
    "Keep responses brief and natural — ideally 1‑3 sentences unless "
    "the user asks for detail."
)

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def _log_filename() -> str:
    """Return a timestamped log filename for this session."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return os.path.join(LOG_DIR, f"conversation_{ts}.txt")


class ConversationLogger:
    """Append‑only logger that writes each exchange to a .txt file."""

    def __init__(self):
        self.path = _log_filename()
        self._write_header()

    def _write_header(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("  Chatbot Conversation Log\n")
            f.write(f"  Started: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n")
            f.write("=" * 60 + "\n\n")

    def log(self, role: str, text: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {role}: {text}\n\n")


# Text‑to‑Speech Engine

class Speaker:
    """Wraps pyttsx3 for speech output."""

    def _create_engine(self):
        """Create and configure a fresh pyttsx3 engine."""
        engine = pyttsx3.init()
        engine.setProperty("rate", 175)
        voices: list = engine.getProperty("voices")  # type: ignore[assignment]
        # Prefer a female voice if available (index 1 on most systems)
        if len(voices) > 1:
            engine.setProperty("voice", voices[1].id)
        return engine

    def speak(self, text: str):
        """Speak *text* aloud (blocks until finished)."""
        engine = self._create_engine()
        engine.say(text)
        engine.runAndWait()
        engine.stop()


# ─── Speech‑to‑Text (Microphone) ────────────────────────────────────────────

class Listener:
    """Captures microphone audio and converts it to text via Google Web Speech API."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Adjust for ambient noise on first use
        self._calibrated = False

    def listen(self) -> str | None:
        """Record from the default mic and return recognised text, or None."""
        with sr.Microphone() as source:
            if not self._calibrated:
                print("Calibrating for ambient noise...", end="", flush=True)
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self._calibrated = True
                print("done.")

            print("Listening...", end="", flush=True)
            try:
                audio = self.recognizer.listen(source, timeout=7, phrase_time_limit=15)
            except sr.WaitTimeoutError:
                print("no speech detected.")
                return None

        print("processing...", end="", flush=True)
        try:
            text = self.recognizer.recognize_google(audio)  # type: ignore[attr-defined]
            print("Done.")
            return text
        except sr.UnknownValueError:
            print("couldn't understand audio.")
            return None
        except sr.RequestError as e:
            print(f"speech API error: {e}")
            return None


# ─── Gemini Chat ─────────────────────────────────────────────────────────────

def create_chat():
    """Create a new Gemini chat session."""
    return client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
        ),
    )


# ─── Display Helpers ─────────────────────────────────────────────────────────

TERM_WIDTH = min(os.get_terminal_size().columns, 90)


def print_banner():
    print()
    print("╔" + "═" * (TERM_WIDTH - 2) + "╗")
    print("║" + "JARVIS AI Assistant (Text + Voice) ".center(TERM_WIDTH - 2) + "║")
    print("╚" + "═" * (TERM_WIDTH - 2) + "╝")
    print()
    print(textwrap.fill(
        "Type your message and press Enter, or type 'v' to use voice input. "
        "Type 'quit' or 'exit' to end the session.",
        width=TERM_WIDTH,
    ))
    print("─" * TERM_WIDTH)


def print_bot_response(text: str):
    """Pretty-print the bot's reply."""
    print()
    print("Jarvis> ", end="")
    wrapped = textwrap.fill(text, width=TERM_WIDTH - 4)
    for line in wrapped.splitlines():
        print(line)
    print()


# ─── Main Loop ───────────────────────────────────────────────────────────────

def main():
    print_banner()

    logger = ConversationLogger()
    speaker = Speaker()
    listener = Listener()
    chat = create_chat()

    while True:
        try:
            user_input = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        # ── Exit commands ───────────────────────────────────────────────
        if user_input.lower() in {"quit", "exit", "q"}:
            break

        # ── Voice mode ──────────────────────────────────────────────────
        if user_input.lower() == "v":
            recognised = listener.listen()
            if recognised is None:
                print("No input captured. Try again.\n")
                continue
            user_input = recognised
            print(f"You said: \"{user_input}\"\n")

        if not user_input:
            continue

        # ── Log user message ────────────────────────────────────────────
        logger.log("User", user_input)

        # ── Get Gemini response ─────────────────────────────────────────
        try:
            response = chat.send_message(user_input)
            reply = (response.text or "").strip()
        except Exception as e:
            reply = f"Sorry, something went wrong: {e}"

        # ── Output: console + speech ────────────────────────────────────
        print_bot_response(reply)
        logger.log("Bot", reply)
        speaker.speak(reply)

    # ── Goodbye ─────────────────────────────────────────────────────────────
    farewell = "Goodbye! Have a lovely day sir."
    print_bot_response(farewell)
    logger.log("Bot", farewell)
    speaker.speak(farewell)
    print(f"Conversation saved to:\n      {logger.path}\n")


if __name__ == "__main__":
    main()
