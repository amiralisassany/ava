
import wave
from vosk import Model, KaldiRecognizer
import language_tool_python
from flask import Flask, request, jsonify
from pydub import AudioSegment
import json

class STT:
    def __init__(self, model_dir, lang='en'):
        self.model_dir = model_dir
        self.lang = lang
        self.audio_dir = None
        self.model = Model(self.model_dir)
        self.recognizer = KaldiRecognizer(self.model, 16000)

    def to_wav(self, input_audio):
        output_audio = input_audio.rsplit('.', 1)[0] + ".wav"
        audio = AudioSegment.from_file(input_audio)

        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(output_audio, format="wav")
    
        return output_audio

    def correct_llm(self, text):
        self.tool = language_tool_python.LanguageTool('en-US')
        matches = self.tool.check(text)
        corrected = language_tool_python.utils.correct(text, matches)
        return corrected

    def to_text(self, audio_path):
        if audio_path.endswith((".mp3", ".ogg")):
            self.audio_dir = self.to_wav(audio_path)
        else:
            self.audio_dir = audio_path

        with wave.open(self.audio_dir, "rb") as wf:
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                self.recognizer.AcceptWaveform(data)

            result = json.loads(self.recognizer.FinalResult())
            self.result = result.get("text", "")
            return self.correct_llm(result.get("text", ""))