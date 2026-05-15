# Build Spec: AI Voice Studio — Local Test
## Claude Execution Brief

---

## Your Machine (Context for Claude)

| | |
|---|---|
| **GPU** | AMD Radeon RX 9070 XT — 16GB VRAM, RDNA 4 (gfx1201) |
| **RAM** | 32GB |
| **OS** | Windows 10 |
| **Test goals** | Voice clone quality · Single narrator pipeline · Two-speaker conversation |
| **UI** | Command-line / scripts only — no web interface |

---

## Scope for This Build

**In scope**: Voice cloning, audio synthesis, audio post-processing.

**Out of scope**: LLM transcript/script generation. Scripts are prepared manually using an external
AI tool (Claude, ChatGPT, etc.) and fed in as plain text or JSON files. This keeps the test
focused on the core voice and audio pipeline.

LM Studio and Ollama are not needed for this build.

---

## Critical Constraints (Read First)

### AMD GPU on Windows

**F5-TTS**: No viable GPU path on Windows with AMD. CPU-only is far too slow. Not used.

**Chatterbox TTS Server** (github.com/devnen/Chatterbox-TTS-Server): Explicitly supports
AMD ROCm on Windows. Community-confirmed working on AMD RDNA cards. This is the voice engine.
Requires AMD Adrenalin 24.10+ drivers.

### Speed Expectations

| Step | Estimated time |
|---|---|
| Chatterbox voice clone training (30 sec sample) | 30–90 seconds (GPU) |
| Chatterbox TTS per sentence (~15 words) | 2–5 seconds (GPU) |
| Full 5-min podcast (narrator mode) | 3–8 minutes |
| Full 5-min podcast (conversation, 2 voices) | 5–12 minutes |
| Audio post-processing | Under 1 minute |

---

## Build Sequence

### Phase 1 — Prerequisites

**What to install (in order):**

1. **Python 3.11.x** (not 3.12 or 3.13 — compatibility issues with some AI libs)
   - Download from python.org
   - During install: tick "Add Python to PATH"
   - Verify: `python --version` → should show 3.11.x

2. **Git for Windows**
   - Download from git-scm.com
   - Default install options are fine

3. **FFmpeg**
   - Download the "essentials" build from ffmpeg.org (Windows)
   - Extract to `C:\ffmpeg`
   - Add `C:\ffmpeg\bin` to Windows PATH (System Environment Variables)
   - Verify: `ffmpeg -version`

4. **AMD ROCm for Windows** (attempt — needed for Chatterbox GPU support)
   - Go to rocm.docs.amd.com → Windows install guide
   - Install HIP SDK 7.2.1 or later
   - Requires AMD Adrenalin drivers 24.10 or newer
   - If install fails or errors: note it and continue — Chatterbox will fall back to CPU

**Verification checkpoint before Phase 2:**
```
python --version        # Should show 3.11.x
git --version           # Any version
ffmpeg -version         # Should show build info
```

---

### Phase 2 — Python Environment

Create an isolated environment for the project:

```
# Run from C:\AI\projects\Podcast
python -m venv venv
venv\Scripts\activate

# Verify venv is active (prompt should show (venv))
python --version
```

Install dependencies:
```
pip install pedalboard soundfile requests python-dotenv
pip install ffmpeg-normalize
```

---

### Phase 3 — Voice Engine (Chatterbox TTS Server)

This is the critical component. Use the community Server version, not the Itch.io desktop app.

1. **Clone the Server repo**
   ```
   # From C:\AI\projects\Podcast
   git clone https://github.com/devnen/Chatterbox-TTS-Server.git
   cd Chatterbox-TTS-Server
   ```

2. **Install with AMD ROCm support (attempt first)**
   ```
   # Make sure venv is active
   pip install -r requirements-rocm.txt
   ```
   If requirements-rocm.txt does not exist in the repo, check the README for AMD install instructions.
   Fallback: `pip install -r requirements.txt` (CPU mode)

3. **Install PyTorch with ROCm for Windows (if ROCm installed in Phase 1)**
   ```
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.1
   ```
   If this fails or produces errors about missing libs: fall back to standard CPU torch:
   ```
   pip install torch torchvision torchaudio
   ```

4. **Start the Chatterbox server**
   ```
   python server.py
   ```
   It should print a URL like `http://localhost:8004` (or similar). If it says "using CUDA" or
   "using ROCm" — GPU is active. If it says "using CPU" — that's fine, continue.
   Leave this running in a separate terminal window.

5. **Quick API test**
   Open a new terminal (venv active), run:
   ```python
   import requests
   r = requests.get("http://localhost:8004/health")
   print(r.json())
   ```
   Should return a status OK response.

---

### Phase 4 — Pipeline Scripts

Create these three scripts in `C:\AI\projects\Podcast\`:

---

#### Script 1: `test_voice_clone.py`
**Purpose**: Upload a voice sample, generate a preview sentence, hear how close it sounds.

The script should:
- Accept a path to a WAV or MP3 file (the voice sample — 30 sec to 3 min recommended)
- POST it to Chatterbox Server's voice clone endpoint
- Request TTS of a fixed test sentence ("Welcome to our health briefing. Today we will cover three key updates from the clinical team.")
- Save output to `output/voice_clone_test.wav`
- Print how long it took

Key API calls to Chatterbox Server (check the repo's README for exact endpoints):
- Upload reference audio: `POST /upload_audio` or `/set_voice`
- Generate TTS with that voice: `POST /tts` with `{"text": "...", "voice": "uploaded"}`

---

#### Script 2: `test_narrator.py`
**Purpose**: Read a pre-written spoken script in the cloned voice and produce a finished MP3.

**Input**: A plain text file `scripts/narrator_script.txt` — written or AI-generated externally.
The file should already be in spoken prose (no bullet points, no headers). See sample below.

The script should:
1. Read `scripts/narrator_script.txt`
2. Split into sentences (split on `.`, `!`, `?` — keep punctuation)
3. For each sentence: call Chatterbox Server TTS with the cloned voice from Script 1
4. Collect all audio segments
5. Concatenate with 400ms silence between sentences using soundfile / numpy
6. Run the assembled audio through Pedalboard post-processing
7. Save to `output/narrator_output.mp3`
8. Print total time taken

---

#### Script 3: `test_conversation.py`
**Purpose**: Generate a two-speaker conversation from a pre-written dialogue script.

**Input**: A JSON file `scripts/conversation_script.json` — written or AI-generated externally.

Format of the JSON file:
```json
[
  {"speaker": "Host", "text": "Welcome to the briefing. Today we have three key updates."},
  {"speaker": "Guest", "text": "Thanks for having me. Let's start with hand hygiene — great news this week."},
  {"speaker": "Host", "text": "Ninety-four percent compliance. That's a real achievement for the team."}
]
```

The script should:
1. Load and parse `scripts/conversation_script.json`
2. For each line in the dialogue:
   - If speaker == "Host": use Voice Persona A (user's own cloned voice)
   - If speaker == "Guest": use Voice Persona B (a second uploaded voice sample, or a Chatterbox preset)
   - Call Chatterbox Server → get audio segment
4. Concatenate all segments with 300ms silence between turns using Pedalboard
5. Run full post-processing chain
6. Save to `output/conversation_output.mp3`
7. Print total time

---

#### Audio Post-Processing (used in Scripts 2 and 3)

Apply this Pedalboard chain to the assembled audio before saving:

```python
import pedalboard
import numpy as np
import soundfile as sf

def post_process(audio_array, sample_rate, output_path):
    board = pedalboard.Pedalboard([
        pedalboard.HighpassFilter(cutoff_frequency_hz=80),
        pedalboard.Compressor(threshold_db=-20, ratio=4.0,
                              attack_ms=5.0, release_ms=150.0),
        pedalboard.Gain(gain_db=2),
        pedalboard.LowShelfFilter(cutoff_frequency_hz=3000, gain_db=3),
        pedalboard.Limiter(threshold_db=-1.5),
    ])
    processed = board(audio_array, sample_rate)
    sf.write(output_path, processed.T, sample_rate)
```

Then normalise to EBU R128 standard using ffmpeg-normalize:
```
ffmpeg-normalize output/raw.wav -o output/final.mp3 -c:a libmp3lame -b:a 192k
```

---

### Sample Input Files

Create these files in `C:\AI\projects\Podcast\scripts\` before running the tests.
Generate the content yourself using Claude or any AI tool — paste the raw topic/transcript in
and ask it to rewrite as spoken audio. Examples below to get you started.

**`scripts/narrator_script.txt`** — plain spoken prose, no formatting:
```
Welcome to this week's clinical update. We have three important items to cover.

First, some great news. Hand hygiene compliance has reached ninety-four percent
across all wards following the gel dispenser rollout. That is a real achievement,
and a sincere thank you to everyone who has made this a priority.

Second, a timely reminder as we head into flu season. The free staff flu vaccination
clinic is running every Tuesday from eight in the morning until four in the afternoon,
in the staff health room on Level Two. Please take advantage of this.

Third, a process update. Patient room allocation for isolation cases now follows the
revised protocol issued on the fifth of May. The updated flowchart is on the intranet.
If you have any questions, please contact your charge nurse directly.
```

**`scripts/conversation_script.json`** — two-speaker dialogue:
```json
[
  {"speaker": "Host", "text": "Welcome to this week's clinical update. I'm joined today by our infection prevention lead. Thanks for being here."},
  {"speaker": "Guest", "text": "Happy to be here. Lots of good news this week, which makes a nice change."},
  {"speaker": "Host", "text": "Let's start with that. Hand hygiene compliance hit ninety-four percent. How significant is that?"},
  {"speaker": "Guest", "text": "It's a real milestone. Anything above ninety percent is considered excellent practice. The gel dispenser rollout made a genuine difference."},
  {"speaker": "Host", "text": "Great outcome. Now flu season is coming up — what do staff need to know?"},
  {"speaker": "Guest", "text": "The vaccination clinic is running every Tuesday, Level Two staff health room, eight till four. It's free, it's quick, and it protects patients too, not just staff."},
  {"speaker": "Host", "text": "And finally there's a protocol update for isolation room allocation?"},
  {"speaker": "Guest", "text": "Yes, new flowchart is live on the intranet from the fifth of May. Any questions, go straight to your charge nurse — they've all been briefed."},
  {"speaker": "Host", "text": "Perfect. Thanks for the update, and thanks everyone for listening."}
]
```

---

## Folder Structure

```
C:\AI\projects\Podcast\
├── venv\
├── Chatterbox-TTS-Server\
├── voice_samples\
│   ├── persona_a.wav              ← Your own voice recording (30 sec min)
│   └── persona_b.wav              ← Second voice for conversation mode
├── scripts\
│   ├── narrator_script.txt        ← Pre-written spoken prose (plain text)
│   └── conversation_script.json   ← Pre-written dialogue (JSON array)
├── output\
│   ├── voice_clone_test.wav
│   ├── narrator_output.mp3
│   └── conversation_output.mp3
├── test_voice_clone.py
├── test_narrator.py
├── test_conversation.py
└── BUILD_SPEC.md
```

---

## Voice Sample Requirements

To test voice cloning the user needs to record audio before running the scripts.

**Requirements:**
- Duration: 30 seconds minimum, 2–3 minutes ideal
- Content: read anything aloud — a news article, a policy document, any continuous speech
- Conditions: quiet room, no echo, consistent distance from mic (~30cm)
- Format: WAV preferred, MP3 acceptable
- No music, no other speakers, no long silences

**How to record on Windows 10:**
- Open Voice Recorder (search in Start menu)
- Record, then export as MP3
- Convert to WAV using: `ffmpeg -i recording.mp3 persona_a.wav`

Save the file as `C:\AI\projects\Podcast\voice_samples\persona_a.wav`

---

## Troubleshooting Guide (for Claude to follow if things break)

| Symptom | Likely cause | Fix |
|---|---|---|
| narrator_script.txt is empty or missing | File not created yet | Create the scripts\ folder and add both input files before running |
| Chatterbox server won't start | Missing dependencies | Run `pip install -r requirements.txt` inside the Chatterbox dir with venv active |
| Chatterbox says "device: cpu" | ROCm not detected or not installed | Acceptable — continue in CPU mode |
| FFmpeg not found | PATH not set | Add `C:\ffmpeg\bin` to System PATH and restart terminal |
| JSON parse error from LLM | 7B model hallucinated | Add retry logic — call Ollama again with "fix this JSON:" prompt |
| Audio sounds choppy when concatenating | Sample rate mismatch | Resample all segments to 24000 Hz before concatenating |

---

## What Success Looks Like

After running all three scripts:

1. **Voice clone test**: You listen to `voice_clone_test.wav` and recognise it as your voice reading the test sentence. It should not sound robotic.

2. **Narrator output**: `narrator_output.mp3` sounds like a professional audio reading of the clinical update. Clear, broadcast-quality loudness, natural pacing.

3. **Conversation output**: `conversation_output.mp3` has two clearly distinct voices taking turns in a natural-sounding dialogue about the clinical update content.

If all three pass the "would I be embarrassed to play this in a meeting?" test — the concept is validated and we can move to building the product.

---

## Next Session Prompt (copy-paste this to start the build)

```
I want to build a local AI voice podcast studio for testing purposes.
My specs: Windows 10, AMD Radeon RX 9070 XT (16GB VRAM), 32GB RAM.
Transcript/script generation is out of scope — scripts are pre-written and fed in as files.
The build spec is at C:\AI\projects\Podcast\BUILD_SPEC.md — please read it
before doing anything, then execute Phase 1 through Phase 4 in order.
Ask me before starting each phase.
```
```
