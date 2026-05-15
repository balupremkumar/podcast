"""
Script 2: test_narrator.py
Read a pre-written script in the cloned voice and produce a finished MP3.

Input:  voice_samples/persona_a.wav
        scripts/narrator_script.txt
Output: output/narrator_output.mp3
"""

import io
import os
import re
import subprocess
import sys
import time

import numpy as np
import pedalboard
import requests
import soundfile as sf

SERVER = "http://localhost:8004"
VOICE_SAMPLE   = r"C:\AI\projects\Podcast\voice_samples\persona_a_clean.wav"
SCRIPT_PATH    = r"C:\AI\projects\Podcast\scripts\narrator_script.txt"
RAW_WAV_PATH   = r"C:\AI\projects\Podcast\output\narrator_raw.wav"
OUTPUT_MP3     = r"C:\AI\projects\Podcast\output\narrator_output.mp3"
SILENCE_MS     = 400
TARGET_SR      = 24000


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def upload_voice(path: str) -> str:
    with open(path, "rb") as f:
        filename = os.path.basename(path)
        resp = requests.post(
            f"{SERVER}/upload_reference",
            files=[("files", (filename, f, "audio/wav"))],
            timeout=60,
        )
    resp.raise_for_status()
    data = resp.json()
    uploaded = data.get("uploaded_files", [])
    if uploaded:
        return uploaded[0]
    filename_only = os.path.basename(path)
    if filename_only in data.get("all_reference_files", []):
        return filename_only
    raise RuntimeError(f"Upload failed: {data}")


def synthesize_sentence(voice_filename: str, text: str) -> np.ndarray:
    resp = requests.post(
        f"{SERVER}/v1/audio/speech",
        json={"model": "chatterbox", "input": text, "voice": voice_filename, "response_format": "wav"},
        timeout=300,
    )
    resp.raise_for_status()
    audio, sr = sf.read(io.BytesIO(resp.content))
    if sr != TARGET_SR:
        import resampy
        audio = resampy.resample(audio, sr, TARGET_SR)
    return audio.astype(np.float32)


def post_process(audio: np.ndarray, sample_rate: int, output_path: str):
    board = pedalboard.Pedalboard([
        pedalboard.HighpassFilter(cutoff_frequency_hz=80),
        pedalboard.Compressor(threshold_db=-20, ratio=4.0, attack_ms=5.0, release_ms=150.0),
        pedalboard.Gain(gain_db=2),
        pedalboard.LowShelfFilter(cutoff_frequency_hz=3000, gain_db=3),
        pedalboard.Limiter(threshold_db=-1.5),
    ])
    if audio.ndim == 1:
        audio = audio[np.newaxis, :]
    processed = board(audio, sample_rate)
    sf.write(output_path, processed.T, sample_rate)


def main():
    os.makedirs(r"C:\AI\projects\Podcast\output", exist_ok=True)

    print("Checking server...")
    requests.get(f"{SERVER}/api/model-info", timeout=10).raise_for_status()

    with open(SCRIPT_PATH, encoding="utf-8") as f:
        raw_text = f.read()
    sentences = split_sentences(raw_text)
    print(f"Script has {len(sentences)} sentences.")

    print("Uploading voice sample...")
    voice_file = upload_voice(VOICE_SAMPLE)
    print(f"  Voice: {voice_file}")

    silence = np.zeros(int(TARGET_SR * SILENCE_MS / 1000), dtype=np.float32)
    segments = []
    t0 = time.time()

    for i, sentence in enumerate(sentences, 1):
        print(f"  [{i}/{len(sentences)}] {sentence[:60]}...")
        audio = synthesize_sentence(voice_file, sentence)
        segments.append(audio)
        segments.append(silence)

    assembled = np.concatenate(segments[:-1])  # drop trailing silence
    print(f"Synthesis done in {time.time() - t0:.1f}s. Applying post-processing...")

    post_process(assembled, TARGET_SR, RAW_WAV_PATH)

    print("Normalising to EBU R128 (-14 LUFS)...")
    ffmpeg_normalize = os.path.join(os.path.dirname(sys.executable), "ffmpeg-normalize.exe")
    subprocess.run([
        ffmpeg_normalize, RAW_WAV_PATH,
        "-o", OUTPUT_MP3,
        "-c:a", "libmp3lame", "-b:a", "192k",
        "--force",
    ], check=True)

    print(f"\nDone → {OUTPUT_MP3}")
    print("Total time:", f"{time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
