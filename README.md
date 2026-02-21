# 🎙️ Real-Time Speech-to-Speech Voice Translator
Aplikacja umożliwiająca tłumaczenie mowy w czasie rzeczywistym z zachowaniem barwy głosu lub syntetycznym lektorem. Projekt wykorzystuje zaawansowane API do przetwarzania dźwięku i naturalnego języka.

## Struktura projektu:

1502-realtime-speech-to-speech-translation/
├── app.py                    # Główna aplikacja Flask
├── config.py                 # Konfiguracja
├── core/
│   ├── __init__.py
│   ├── stt_realtime.py       # Speech-to-Text
│   ├── tts_client.py         # Text-to-Speech
│   └── translator.py         # Tłumaczenie
├── templates/
│   └── index.html            # Realtime UI
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── tests/
│   ├── __init__.py
│   ├── test_stt.py
│   └── test_app.py
├── .env.example
├── requirements.txt
├── README.md
├── LICENSE
├── pyproject.toml
└── .github/workflows/ci.yml



## 🚀 Faza 1: Przygotowanie i Konfiguracja Środowiska
Ta faza obejmuje założenie niezbędnych kont oraz wygenerowanie kluczy API, które umożliwią komunikację z silnikami AI.

🔑 Wymagane Klucze API
Do pełnego działania aplikacji potrzebny jest dostęp do następujących usług:

- OpenAI API - Rozpoznawanie mowy (Whisper) i tłumaczenie (GPT)	- platform.openai.com
- ElevenLabs - Synteza mowy (TTS) i klonowanie głosu
- Azure

## 💻 Faza 2: Setup środowiska

Nazwa folderu z projektem:
1502-realtime-speech-to-speech-translation

Zainstaluj biblioteki:

```bash
pip install --break-system-packages azure-cognitiveservices-speech
pip install --break-system-packages openai
pip install --break-system-packages langchain-openai
pip install --break-system-packages elevenlabs
pip install --break-system-packages pyaudio  # dla mikrofonu
```
