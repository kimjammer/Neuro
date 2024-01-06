import requests
from RealtimeTTS import TextToAudioStream, CoquiEngine
from RealtimeSTT import AudioToTextRecorder

def process_text(text):
    print(text)
    user_message = text
    history.append({"role": "user", "content": user_message})
    data = {
        "mode": "chat-instruct",
        "character": "AI",
        "messages": history
    }
    
    response = requests.post(url, headers=headers, json=data, verify=False)
    assistant_message = response.json()['choices'][0]['message']['content']
    history.append({"role": "assistant", "content": assistant_message})
    print(assistant_message)
    stream.feed(assistant_message)
    stream.play()

if __name__ == '__main__':
    engine = CoquiEngine(
        use_deepspeed=True,
        voice="./voices/David_Attenborough CC3.wav"
    )
    stream = TextToAudioStream(engine)
    
    url = "http://127.0.0.1:5000/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    history = []
    
    recorder_config = {
        'spinner': False,
        'model': 'tiny.en',
        'language': 'en',
        'silero_sensitivity': 0.4,
        'silero_use_onnx': True,
        'webrtc_sensitivity': 2,
        'post_speech_silence_duration': 0.4,
        'min_length_of_recording': 0,
        'min_gap_between_recordings': 0,
        'enable_realtime_transcription': True,
        'realtime_processing_pause': 0.2,
        'realtime_model_type': 'tiny.en'
    }
    
    
    with AudioToTextRecorder(**recorder_config) as recorder:
        while True:
            recorder.text(process_text)