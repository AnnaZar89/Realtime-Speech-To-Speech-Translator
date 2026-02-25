import io
import os
import json
import azure.cognitiveservices.speech as speechsdk
from flask import Flask, render_template, request, jsonify, send_file, Response
from openai import OpenAI
from pydub import AudioSegment
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from pydub.playback import play


load_dotenv()
app = Flask(__name__)
AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
AZURE_REGION = os.getenv('AZURE_REGION')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)


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

def index():
    return render_template('index.html', history_json="[]")

@app.route('/recognize', methods=['POST'])

def recognize():

    audio_file = request.files['audio']
    audio_data = audio_file.read()
    conversation_history = request.form.get('history', '[]')
    source_lang = request.form.get('source_lang')
    target_lang = request.form.get('target_lang')
    if not source_lang or not target_lang:
        return jsonify({"success": False, "error": "Brak języka źródłowego lub docelowego"}), 400

    audio = AudioSegment.from_file(io.BytesIO(audio_data))
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    wav_buffer = io.BytesIO()
    audio.export(wav_buffer, format='wav')

    speech_config = speechsdk.SpeechConfig(AZURE_SPEECH_KEY, AZURE_REGION)
    speech_config.speech_recognition_language = source_lang

    stream = speechsdk.audio.PushAudioInputStream()
    audio_config = speechsdk.audio.AudioConfig(stream=stream)
    recognizer = speechsdk.SpeechRecognizer(speech_config, audio_config)

    stream.write(wav_buffer.getvalue())
    stream.close()

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        original_text = result.text
        translation = translate(original_text, source_lang, target_lang)

        try:
            history_list = json.loads(conversation_history)

        except:
            history_list = []

        history_list.append({"user": original_text, "bot": translation})
        new_history_json = json.dumps(history_list)

        return jsonify({
            'success': True,
            'original_text': original_text,
            'translation': translation,
            'history_json': new_history_json
        })

    else:
        return jsonify({'success': False, 'error': 'Nie rozpoznano mowy'})

@app.route('/synthesize', methods=['POST'])
def synthesize():
    text = request.form.get('text')
    if text:
        audio_content = speak_translation(text)
        return Response(
            audio_content,
            mimetype="audio/mpeg",
            headers={"Content-Disposition": "inline"}
        )
    else:
        return jsonify({"success": False, "error": "No text provided"}), 400

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)




