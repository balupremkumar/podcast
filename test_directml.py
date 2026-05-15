"""
DirectML GPU acceleration test for Chatterbox.
Run this after installing torch-directml to check if the AMD GPU works.

REVERT COMMAND (if this fails and you want to go back to CPU):
  .\\venv\\Scripts\\pip.exe install torch==2.5.1+cpu torchaudio==2.5.1+cpu torchvision==0.20.1+cpu --index-url https://download.pytorch.org/whl/cpu
"""

import time
import torch

def test_basic_ops():
    print("=== DirectML basic tensor test ===")
    try:
        import torch_directml
        dml = torch_directml.device()
        print(f"  DirectML device: {dml}")

        a = torch.randn(1024, 1024).to(dml)
        b = torch.randn(1024, 1024).to(dml)

        t0 = time.time()
        for _ in range(10):
            c = torch.matmul(a, b)
        _ = c.cpu()  # force sync
        elapsed = time.time() - t0

        print(f"  10x matmul(1024,1024) on DirectML: {elapsed:.2f}s")

        # CPU baseline
        a_cpu = a.cpu(); b_cpu = b.cpu()
        t0 = time.time()
        for _ in range(10):
            c_cpu = torch.matmul(a_cpu, b_cpu)
        elapsed_cpu = time.time() - t0
        print(f"  10x matmul(1024,1024) on CPU:      {elapsed_cpu:.2f}s")
        print(f"  Speedup: {elapsed_cpu / elapsed:.1f}x")
        return dml
    except Exception as e:
        print(f"  FAILED: {e}")
        return None


def test_chatterbox_load(dml):
    print("\n=== Chatterbox model load on DirectML ===")
    try:
        from chatterbox.tts_turbo import ChatterboxTurboTTS
        print("  Loading model to DirectML (this may take 30s)...")
        t0 = time.time()
        model = ChatterboxTurboTTS.from_pretrained(device=str(dml))
        print(f"  Model loaded in {time.time()-t0:.1f}s on {model.device}")
        return model
    except Exception as e:
        print(f"  FAILED: {e}")
        print("  Chatterbox may not support DirectML device string.")
        return None


def test_synthesis(model, dml):
    print("\n=== Synthesis speed test ===")
    try:
        import requests, io, soundfile as sf
        SERVER = "http://localhost:8004"
        # Just time a single sentence via the server (which is still on CPU)
        # This tells us server latency baseline
        t0 = time.time()
        resp = requests.post(f"{SERVER}/v1/audio/speech",
            json={"model":"chatterbox","input":"This is a speed test sentence for the DirectML benchmark.","voice":"persona_a_clean.wav","response_format":"wav"},
            timeout=120)
        elapsed = time.time() - t0
        if resp.ok:
            audio, sr = sf.read(io.BytesIO(resp.content))
            duration = len(audio) / sr
            print(f"  Server synthesised {duration:.1f}s of audio in {elapsed:.1f}s (RTF: {elapsed/duration:.2f}x realtime)")
        else:
            print(f"  Server error: {resp.status_code}")
    except Exception as e:
        print(f"  Server test skipped: {e}")


if __name__ == "__main__":
    dml = test_basic_ops()
    if dml:
        test_chatterbox_load(dml)
    test_synthesis(None, None)
    print("\nDone. Check results above before patching the server.")
