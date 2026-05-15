"""
Script 1: test_voice_clone.py
Upload a voice sample, generate a preview sentence, check the clone quality.
"""

import time
import requests

SERVER = "http://localhost:8004"
VOICE_SAMPLE = r"C:\AI\projects\Podcast\voice_samples\persona_a_clean.wav"
OUTPUT_PATH = r"C:\AI\projects\Podcast\output\voice_clone_test.wav"
TEST_SENTENCE = "Welcome to our health briefing. Today we will cover three key updates from the clinical team."


def upload_voice(path: str) -> str:
    """Upload reference audio and return the saved filename."""
    with open(path, "rb") as f:
        filename = path.split("\\")[-1]
        resp = requests.post(
            f"{SERVER}/upload_reference",
            files=[("files", (filename, f, "audio/wav"))],
            timeout=60,
        )
    resp.raise_for_status()
    data = resp.json()
    if data.get("errors"):
        raise RuntimeError(f"Upload errors: {data['errors']}")
    uploaded = data.get("uploaded_files", [])
    if not uploaded:
        # File already existed on server — treat as success
        all_files = data.get("all_reference_files", [])
        filename_only = filename
        if filename_only in all_files:
            return filename_only
        raise RuntimeError(f"Upload returned no files: {data}")
    return uploaded[0]


def synthesize(voice_filename: str, text: str, output_path: str) -> float:
    """Call /v1/audio/speech and save the result. Returns elapsed seconds."""
    t0 = time.time()
    resp = requests.post(
        f"{SERVER}/v1/audio/speech",
        json={"model": "chatterbox", "input": text, "voice": voice_filename, "response_format": "wav"},
        timeout=300,
    )
    resp.raise_for_status()
    elapsed = time.time() - t0
    with open(output_path, "wb") as f:
        f.write(resp.content)
    return elapsed


def main():
    import os
    os.makedirs(r"C:\AI\projects\Podcast\output", exist_ok=True)

    print("Checking server health...")
    try:
        resp = requests.get(f"{SERVER}/api/model-info", timeout=10)
        resp.raise_for_status()
        print(f"  Server OK — {resp.json()}")
    except Exception as e:
        print(f"  Server not ready: {e}")
        print("  Make sure the Chatterbox server is running.")
        return

    print(f"Uploading voice sample: {VOICE_SAMPLE}")
    voice_file = upload_voice(VOICE_SAMPLE)
    print(f"  Uploaded as: {voice_file}")

    print(f"Synthesising test sentence...")
    elapsed = synthesize(voice_file, TEST_SENTENCE, OUTPUT_PATH)
    print(f"  Done in {elapsed:.1f}s → {OUTPUT_PATH}")
    print()
    print("Listen to the output and check it sounds like your voice.")


if __name__ == "__main__":
    main()
