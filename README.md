# 🌐 Real-Time Translator App

A web application for real-time **speech and text translation** between multiple languages, powered by Azure Speech Services, OpenAI GPT, and ElevenLabs TTS.

## ✨ Features

- 🎤 **Speech Translator** — real-time voice recognition and translation with audio playback
- ✍️ **Text Translator** — live text translation as you type
- 🔊 **Voice Synthesis** — translated speech played back using ElevenLabs
- 🌍 Supports 8 languages: Polish, English, French, German, Italian, Spanish, Japanese, Chinese
- 📱 Responsive design — works on desktop and mobile

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Speech Recognition | Azure Speech SDK (browser-based) |
| Translation | OpenAI GPT-3.5 |
| Text-to-Speech | ElevenLabs |
| Deployment | Docker, Azure App Service, GitHub Actions |

## 📁 Project Structure

```
Realtime-Speech-To-Speech-Translator/
├── app.py                          # Flask backend
├── requirements.txt
├── Dockerfile
├── .env.example
├── templates/
│   └── index.html                  # Frontend (HTML + JS)
├── static/
│   ├── css/
│   │   └── style.css
│   └── images/
│       └── background.jpg
└── .github/
    └── workflows/
        └── deploy.yml              # GitHub Actions CI/CD
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Azure Speech Services account
- OpenAI API key
- ElevenLabs API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AnnaZar89/Realtime-Speech-To-Speech-Translator.git
cd Realtime-Speech-To-Speech-Translator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:
```
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_REGION=your_azure_region
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_voice_id
```

4. Run the app:
```bash
python app.py
```

5. Open your browser at `http://localhost:5000`

## ☁️ Deployment

The app is deployed to **Azure App Service** via Docker and GitHub Actions.

On every push to `main`, GitHub Actions:
1. Builds a Docker image
2. Pushes it to Docker Hub
3. Deploys it to Azure App Service

Link to the demo page [here](https://translator-app-d4b6eddje2bxefd2.switzerlandnorth-01.azurewebsites.net/).

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub access token |
| `AZURE_APP_NAME` | Azure Web App name |
| `AZURE_PUBLISH_PROFILE` | Azure publish profile XML |

### Required Azure Environment Variables

| Variable | Description |
|---|---|
| `AZURE_SPEECH_KEY` | Azure Speech Services key |
| `AZURE_REGION` | Azure region (e.g. westeurope) |
| `OPENAI_API_KEY` | OpenAI API key |
| `ELEVENLABS_API_KEY` | ElevenLabs API key |
| `ELEVENLABS_VOICE_ID` | ElevenLabs voice ID |

## 🔒 Security

- API keys stored in `.env` (not committed to Git)
- Azure Speech token exchange — browser never sees the raw API key
- Rate limiting on `/api/speech-token` endpoint (10 requests/minute)