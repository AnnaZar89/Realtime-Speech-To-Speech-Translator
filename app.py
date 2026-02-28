import os
from flask import Flask, render_template, request, jsonify, Response
from openai import OpenAI
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings


load_dotenv()

AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
AZURE_REGION = os.getenv('AZURE_REGION')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')

client = OpenAI(api_key=OPENAI_API_KEY)
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

app = Flask(__name__)

def translate(text, source, target):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Translate from {source} to {target}. Return ONLY the translation. Preserve all punctuation marks and line breaks from the original text."
            },
            {"role": "user", "content": text}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

def speak_translation(text):
    try:
        response = elevenlabs_client.text_to_speech.convert(
            voice_id=ELEVENLABS_VOICE_ID,
            output_format="mp3_44100_128",
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True
            )
        )
        audio_data = b''.join(chunk for chunk in response if chunk)
        return audio_data
    except Exception as e:
        print(f"❌ Błąd ElevenLabs: {e}")

@app.route('/')

@app.route('/')
def index():
    return render_template('index.html')  # bez azure_key i azure_region

@app.route('/translate_voice', methods=['POST'])
def translate_voice():
    try:
        text = request.form.get('text')
        src_lang = request.form.get('source_lang')
        target_lang = request.form.get('target_lang')
        if not text or not src_lang or not target_lang:
            return jsonify({"success": False, "error": "Brak wymaganych danych"}), 400

        translation = translate(text, src_lang, target_lang)
        return jsonify({
            "success": True,
            "original": text,
            "translation": translation
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/translate_text', methods=['POST'])
def translate_text():
    try:
        text = request.form.get('text')
        src_lang = request.form.get('source_lang')
        target_lang = request.form.get('target_lang')
        translation = translate(text, src_lang, target_lang)
        if not text or not src_lang or not target_lang:
            return jsonify({"success": False, "error": "Brak wymaganych danych"}), 400

        return jsonify({
            "success": True,
            "translation": translation
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/synthesize', methods=['POST'])
def synthesize():
    text = request.form.get('text')
    if not text:
        return jsonify({"success": False, "error": "Brak tekstu"}), 400
    audio_content = speak_translation(text)
    if audio_content:
        return Response(
            audio_content,
            mimetype="audio/mpeg",
            headers={"Content-Disposition": "inline"}
        )
    else:
        return jsonify({"success": False, "error": "Błąd generowania audio"}), 500


@app.route('/api/speech-token', methods=['GET'])
def get_speech_token():
    import requests
    token_url = f"https://{AZURE_REGION}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
    headers = {'Ocp-Apim-Subscription-Key': AZURE_SPEECH_KEY}
    response = requests.post(token_url, headers=headers)
    return jsonify({
        "token": response.text,
        "region": AZURE_REGION
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)




