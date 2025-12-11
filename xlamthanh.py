import os
from pydub import AudioSegment
import librosa
import soundfile as sf

def convert_to_wav(input_path, output_path):
    """Chuyển đổi sang định dạng WAV"""
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="wav")
    print(f"Converted: {input_path} -> {output_path}")

def normalize_audio(input_path, output_path):
    """Chuẩn hóa âm lượng"""
    audio, sr = librosa.load(input_path, sr=None)
    audio_norm = librosa.util.normalize(audio)
    sf.write(output_path, audio_norm, sr)
    print(f"Normalized: {input_path}")

# Xử lý tất cả file trong thư mục
for file in os.listdir("audio/raw"):
    if file.endswith((".mp3", ".m4a")):
        input_file = f"audio/raw/{file}"
        output_file = f"audio/processed/{os.path.splitext(file)[0]}.wav"
        convert_to_wav(input_file, output_file)