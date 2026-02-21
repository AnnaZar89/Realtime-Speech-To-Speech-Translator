import io
import os
import json
import azure.cognitiveservices.speech as speechsdk
from flask import Flask, render_template, request, jsonify, send_file
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


def translate(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Translate to french. Return ONLY the translation."
            },
            {"role": "user", "content": text}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content


def speak_translation(text):
    """Odtwarza audio z pamięci (jak w projekcie Flask)"""
    print("🔊 Generuję audio...")

    try:
        # Generuj audio z ElevenLabs
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

        # Zbierz bajty audio (analogicznie do audio_file.read())
        audio_data = b''.join(chunk for chunk in response if chunk)

        # Wczytaj audio z pamięci (jak w projekcie: AudioSegment.from_file(io.BytesIO(audio_data)))
        audio = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")

        print("▶️  Odtwarzam...")

        # Odtwórz bezpośrednio (jak pydub.playback.play)
        play(audio)


    except Exception as e:
        print(f"❌ Błąd ElevenLabs: {e}")



@app.route('/')

def index():
    return render_template('index.html', history_json="[]")

@app.route('/recognize', methods=['POST'])

def recognize():

    # 1. Pobierz audio i historię
    audio_file = request.files['audio']
    audio_data = audio_file.read()
    conversation_history = request.form.get('dataSrcLanguage', '[]')  # Domyślnie pusta lista w stringu; jak są dane to w json
    # 2. Konwersja webm -> WAV 16kHz mono (Twoje dotychczasowe przetwarzanie pydub)
    audio = AudioSegment.from_file(io.BytesIO(audio_data))
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    wav_buffer = io.BytesIO()
    audio.export(wav_buffer, format='wav')

    speech_config = speechsdk.SpeechConfig(AZURE_SPEECH_KEY, AZURE_REGION)
    speech_config.speech_recognition_language = "pl-PL"

    # PushStream dla danych binarnych
    stream = speechsdk.audio.PushAudioInputStream()
    audio_config = speechsdk.audio.AudioConfig(stream=stream)
    recognizer = speechsdk.SpeechRecognizer(speech_config, audio_config)

    stream.write(wav_buffer.getvalue())
    stream.close()

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        original_text = result.text
        translation = translate(original_text)

        try:
            history_list = json.loads(conversation_history) # zamieniamy z jsona na nie json

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
        speak_translation(text)
        return jsonify({"success": True, "message": "Audio played locally"}), 200
    else:
        return jsonify({"success": False, "error": "No text provided"}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)




