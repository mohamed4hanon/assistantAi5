# assistantAi5 🎙️🤖

An offline-triggered Voice Assistant powered by the official **Google GenAI SDK** (`gemini-2.5-flash`) and optimized specifically for deployment on a **Raspberry Pi 3** running **Raspberry Pi OS Lite** (headless environment).

It features hardware integration via GPIO pins for push-to-talk interactions and visual LED feedback.

---

## ✨ Features
* **Optimized for OS Lite:** Pure CLI execution, lightweight, and consumes minimal system resources.
* **Push-to-Talk Mechanism:** Triggered by a physical hardware button via Raspberry Pi GPIO.
* **Visual LED Feedback:** LED turns ON when the assistant is processing or speaking, providing clear state status.
* **Powered by Gemini 2.5:** Uses `gemini-2.5-flash` via the official `google-genai` client with multi-turn chat memory.
* **Efficient Custom `.env` Loader:** Reads environment keys safely without external dependency packages like `python-dotenv`.
* **Clean Text-to-Speech (TTS):** Integrated with `gTTS` and automated text-cleaning filters to avoid spoken markdown characters (`*`, `#`, etc.).

---

## 🛠️ Hardware Requirements
* **Single Board Computer:** Raspberry Pi 3 (Model B or B+).
* **OS:** Raspberry Pi OS Lite (Bullseye/Bookworm).
* **Audio Input:** USB/I2S Microphone (Note: Built-in audio jack on Pi 3 is output-only).
* **Audio Output:** Speaker or Amplifier (connected via Audio Jack or I2S/USB sound card using `mpg123`).
* **Components:** * 1x Push Button Connected to **GPIO 24** (Physical Pin 18) with internal pull-up.
  * 1x LED Connected to **GPIO 25** (Physical Pin 22) with a current-limiting resistor.

---

## 🚀 Installation & Setup

### 1. System & Audio Dependencies (Crucial for OS Lite)
Since Raspberry Pi OS Lite does not include a desktop environment, you must install core audio architectures (`ALSA`) along with `mpg123` manually:

```bash
sudo apt-get update
sudo apt-get install -y mpg123 alsa-utils portaudio19-dev python3-pyaudio
```


Tip: You can check if your microphone is detected on OS Lite by running arecord -l.

### 2. Clone the Repository
```bash
   git clone [https://github.com/mohamed4hanon/assistantAi5.git](https://github.com/mohamed4hanon/assistantAi5.git)
   cd assistantAi5
```

### 3. Install Python Packages
Install the required python libraries using pip:
```bash
pip install google-genai speechrecognition gtts RPi.GPIO
```

(Note: If you encounter a managed-environment error on newer OS Lite versions, use a virtual environment python3 -m venv venv && source venv/bin/activate before installing).

### 4. API Configuration
Create a .env file in the root directory next to your script:
```bash
nano .env
````
Add your official Gemini API key:

```bash
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 5. 💻 Usage
Run the assistant script directly from the terminal:
```bash
python assistant5.py
```

###  6. How to use:
1. On boot, the assistant will announce that it is ready.
2. Press and release the physical button.
3. The system will start listening. Speak your query in Arabic (e.g., "ما هي حالة الطقس اليوم؟").
4. The LED turns ON while the assistant fetches the response from Gemini and speaks it back.
5. Say "خروج", "إنهاء", or "توقف" to safely shut down the script and clear GPIO states.

###  📜 License
This project is open-source and licensed under the MIT License.















