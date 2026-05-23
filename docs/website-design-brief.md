# AI Podcast Studio — Website & Product Design Brief

> **For the designer:** Build within the existing colour system documented at the bottom of this file. Component descriptions map directly to what's already built in `frontend/index.html` — use those as the source of truth for individual component appearance. Reference websites to be provided separately.

---

## Product Overview

Two AI pipelines, one product:

- **Intelligence** — Upload any audio recording → get show notes, chapter markers, a cold open script, and an editorial quality score. Everything runs locally. No audio leaves the server.
- **Voice Studio** — Provide a text script → generate a finished MP3 in a cloned voice. Single narrator or two-speaker conversation.

**Full loop:** Upload a briefing → get a cold open script → synthesise it in your own cloned voice → publish.

**Core differentiator:** Health organisations can't use ElevenLabs, Descript, or any cloud audio tool — data sovereignty and compliance rules it out. This runs entirely on-premise.

---

## Site Architecture

```
/ ─────────────── Landing page (public)
/features ──────── Feature detail (public)
/how-it-works ──── Process walkthrough (public)
/compliance ─────── Privacy & data sovereignty page (public)
/demo ───────────── Book a demo / contact (public)

/app ─────────────── App root (authenticated)
/app/dashboard ───── Job history + quick upload
/app/episode/:id ──── Full episode results (5 tabs)
/app/voice-studio ─── Voice cloning + synthesis
/app/voices ──────── Saved voice library
/app/settings ────── Backend config, model selection
```

---

## Page 1 — Landing Page

### Navigation Bar
- **Left:** Logo — animated EQ bars (5 vertical teal bars) + "Podcast Intelligence" bold wordmark
- **Right:** `How it works` · `Features` · `Compliance` · `Book a demo` (teal outline CTA button)
- Sticky, dark background, subtle bottom border
- Status pill if logged in: `● LOCAL` or `● CLOUD`

### Hero Section

**Headline (large, heavy weight):**
> "Your briefings. Fully analysed.
> Never leaves the building."

**Subheadline:**
> Health organisations record dozens of briefings every month — clinical updates, safety notices, staff comms. Every tool that could help publish them properly sends your audio to an external server. This one doesn't.

**Two CTAs side by side:**
- `See how it works →` (primary, teal fill)
- `Book a demo` (secondary, ghost)

**Hero visual:** Animated pipeline — 7 stage dots lighting up left to right, waveform input on left transforming into output cards (show notes, chapters, cold open) on right. Dark background, teal glow. No stock photos.

**Social proof strip (3 items):**
- "Runs entirely on your servers"
- "No audio processed externally"
- "NZ HIPC compliant deployment"

---

### The Problem Section

**Headline:** "Every other tool is a compliance breach waiting to happen."

Three-column layout:

| Your audio | → sends externally | Health org can't use it |
|---|---|---|
| ElevenLabs, Descript, Riverside | Cloud processing | Data sovereignty breach |

**Callout box:**
> "One audio file containing a clinical briefing. Uploaded to a cloud service. That's a notifiable privacy breach in most health systems."

Below: "We built the alternative."

---

### Features Overview — 4 Cards

Dark panels, teal icon, headline, 2-line description:

**Card 1 — Intelligence Pipeline**
> *Upload a recording. Get back everything a producer needs.*
> Transcription with speaker labels · Show notes · Chapter markers · Cold open script · Quality score

**Card 2 — Voice Studio**
> *Give it a 30-second voice sample. It clones the voice.*
> Single narrator mode or two-speaker conversation. Post-processed to broadcast standard.

**Card 3 — Quality Score**
> *An honest editorial critique of every episode.*
> Scores information density, pacing, clarity, and memorability. Flags specific segments with rewrite suggestions.

**Card 4 — Local-First Architecture**
> *One environment variable. Zero external calls.*
> Switch between cloud LLM and fully local model. Same interface, same output, different backend.

---

### How It Works — 3-Step Visual

**Step 1:** Drop your audio file
- Visual: the drop zone component

**Step 2:** Seven AI stages run in sequence
- Visual: pipeline progress — 7 animated dots: Transcribe → Diarise → Research → Show Notes → Chapters → Cold Open → Quality Score

**Step 3:** Results ready to use
- Visual: 5-tab results panel, Cold Open tab active

---

### Quality Score Showcase

**Headline:** "Not just a summary. An editorial opinion."

Sample output shown:
- Large score number (e.g. 5.75 / 10)
- 4 dimension score bars
- One flag card (amber, medium severity) with issue + suggestion

**Copy:**
> "Most AI tools just summarise what was said. The quality score tells you what was wrong with how it was said — and exactly how to fix it before the next recording."

---

### Compliance Strip

Dark panel, lock icon:

**Headline:** "Built for environments where data can't leave."

Six-column feature list:
- No audio sent to external APIs
- Local LLM mode — one env var
- Works fully air-gapped
- No cloud dependency for production
- NZ HIPC aligned
- On-premise deployment

CTA: `Read the compliance detail →`

---

### CTA Footer

**Headline:** "Ready to see it running on your content?"

- `Book a demo` — opens form (name, org, email, use case)
- `Self-hosted setup guide` — goes to docs

---

## Page 2 — Features Deep-Dive (`/features`)

Seven sections, one per pipeline stage. Each has:
- Stage number (01–07, mono font)
- Stage name + description
- UI component screenshot/mockup
- Small technical note

**Stages:**

| # | Stage | What it does | Technical note |
|---|---|---|---|
| 01 | Transcription | Converts speech to text with word-level timestamps | faster-whisper — word-level timestamps make chapter markers accurate to the second |
| 02 | Speaker Diarisation | Identifies who said what throughout the episode | pyannote 3.1 with VAD fallback for offline/no-token deployments |
| 03 | Guest Research | Pulls background context on named guests | Wikipedia API — zero friction, works offline; swap for Tavily in production |
| 04 | Show Notes | Structured output: title, description, themes, notable moments, quotable moments | Claude Sonnet — schema held across episode lengths, local LLM option available |
| 05 | Chapter Detection | Finds topic shifts and generates timestamp markers | Precise to the word — uses word-level timestamps from Stage 01 |
| 06 | Cold Open | Writes a 30-second spoken hook from the best moment | Designed to be read aloud or synthesised directly via Voice Studio |
| 07 | Quality Score | 4-dimension score, overall rating, flagged segments with rewrite suggestions | Information density · Pacing · Clarity · Memorable moments |

**Voice Studio section (below the 7 stages):**

Separate visual treatment. Headline: "The other half."

> "The intelligence pipeline tells you what's in your audio. The voice studio lets you build audio from scratch — in any voice, running on your own servers."

Features:
- Voice cloning from a 30-second sample
- Single narrator mode
- Two-speaker conversation (JSON dialogue format)
- Pedalboard audio post-processing (compressor, EQ, limiter)
- EBU R128 normalisation for broadcast-standard loudness

---

## Page 3 — Compliance (`/compliance`)

### Why cloud tools are off the table
Plain language — not legal jargon.

> "When you upload audio to ElevenLabs, their servers process it. In a health setting, that audio may contain patient references, staff names, operational details. Most health systems classify this as a potential privacy breach."

### Architecture Diagram — Side by Side

**Cloud tool:**
`Your audio → Internet → External server → Processed → Results`

**This tool:**
`Your audio → Your server → Local processing → Results`
*(nothing leaves)*

### Local Deployment Options — 3 Tiers

**Tier 1 — Default**
Claude API + local Whisper. Transcription is fully local. Generation uses Claude API (text only, no audio sent).

**Tier 2 — Fully Local**
LM Studio + local Whisper. Zero external API calls. Requires GPU with 16GB+ VRAM for reliable JSON output.

**Tier 3 — Air-Gapped**
Fully local + Kiwix offline Wikipedia for guest research. No network required after initial setup.

### Data Storage
- Audio files: temporary, deleted after processing
- Results: in-memory (demo) or your own database (production)
- No telemetry, no logging to external services, no call-home behaviour

### NZ HIPC Note
> Designed for deployment patterns consistent with NZ Health Information Privacy Code requirements. Your legal and privacy team should review for your specific deployment context.

---

## Page 4 — App Interior

### 4a. Dashboard (`/app/dashboard`)

**Left sidebar (fixed):**
- Logo
- Navigation: Dashboard · New Episode · Voice Studio · Voice Library · Settings
- Bottom: LLM backend pill · TTS backend pill

**Main content:**
- Header: "Dashboard" + `New Episode →` (teal)
- Recent Episodes — card grid:
  - Episode title
  - Duration · Speaker count · Language chips
  - Quality score badge (colour-coded by score)
  - Date processed
  - Actions: View · Export · Delete
- Empty state: large drop zone

---

### 4b. New Episode (`/app/new`)

Current upload screen expanded:

- Full-width drag-and-drop zone
- Guest name field (optional — triggers research stage)
- Processing options (expandable):
  - Whisper model: tiny / base / small / medium / large-v3 (tooltip: "Larger = more accurate, slower")
  - LLM backend: Claude / Local
  - Language hint (optional)
- Submit: `Analyse episode →`

Processing screen (keep as-is):
- EQ bar animation
- Stage list with active/done/pending states
- Elapsed time counter
- Progress bar

---

### 4c. Episode Detail (`/app/episode/:id`)

Current results screen expanded:

**Header:**
- Episode title
- Duration · Speakers · Language chips
- Export button (markdown download)
- Re-analyse button
- Share button (placeholder)

**5 Tabs:**

| Tab | Content |
|---|---|
| Cold Open | Script card (large text) · "Hear it in AI voice" button · Audio player (post-synthesis) · "Send to Voice Studio →" |
| Quality Score | Overall score (large) · 4 dimension bars · Flagged segments (severity colour-coded) · "Copy all flags as producer notes" |
| Show Notes | Description · Theme tags · Notable moments (timestamp + description) · Quotable moments (pull quote style) |
| Chapters | Numbered list · Timestamp + title + summary per chapter |
| Transcript | Full diarised transcript · Speaker colour-coded · Timestamp per line |

All tabs have a Copy button and the export button in the header exports all tabs as one markdown file.

---

### 4d. Voice Studio (`/app/voice-studio`)

**Left panel — Voice Setup:**
- Upload voice sample (WAV/MP3, 30 sec minimum)
- Voice name field
- Preview button (generates test sentence)
- Saved voices dropdown

**Right panel — Script:**
- Mode toggle: `Narrator` / `Conversation`

**Narrator mode:**
- Large textarea (plain prose script)
- Character count + estimated duration
- `Produce episode →` button
- Progress: sentence X / total (animated)
- Output: audio player + download MP3

**Conversation mode:**
- Host voice selector · Guest voice selector
- Script editor: alternating Host / Guest line rows
- `Produce conversation →`
- Same progress + output

---

### 4e. Voice Library (`/app/voices`)

Grid of saved voice profiles:
- Card: name · sample playback button · date added
- Actions: Test · Rename · Delete
- `+ Add voice` → Voice Studio setup

---

### 4f. Settings (`/app/settings`)

**LLM Backend**
- Radio: Claude API / Local
- Claude: API key (masked) + model selector
- Local: LM Studio URL + model name
- Test connection button

**Transcription**
- Whisper model selector
- Default language

**TTS Backend**
- Chatterbox URL (default: localhost:8004)
- Test connection
- Status indicator

---

## Design System

### Colour Tokens

| Token | Hex | Usage |
|---|---|---|
| `--navy` | `#0D1F3C` | Page background |
| `--navy-mid` | `#142847` | Card / panel background |
| `--navy-up` | `#1A3358` | Elevated surface, hover state |
| `--teal` | `#0A7EA4` | Primary accent, borders, icons |
| `--teal-sky` | `#38BDF8` | Active state, highlights |
| `--off-white` | `#EEF2F7` | Primary text |
| `--t2` | `#8B9BB4` | Secondary text |
| `--t3` | `#4B5E7A` | Muted text, labels |
| `--green` | `#10B981` | Success, high score |
| `--amber` | `#F59E0B` | Warning, medium severity |
| `--red` | `#EF4444` | Error, high severity |
| `--purple` | `#A78BFA` | Speaker 2 colour in transcript |

### Typography

| Use | Font | Weight | Size |
|---|---|---|---|
| Body | Inter | 400 | 13.5–15.5px |
| Headings | Inter | 800–900 | 18–40px |
| Labels | Inter | 600–700 | 10–11px (uppercase, tracked) |
| Timestamps / code | JetBrains Mono | 400–500 | 11px |

### Existing Components (already built — reuse directly)

| Component | Description |
|---|---|
| EQ bars | 5 vertical teal bars, bounce animation, vary heights |
| Drop zone | Dashed teal border, drag hover state, waveform SVG overlay |
| Tab pills | Pill shape, active = teal fill + border |
| Stage row | Icon (tick/blink/dot) + label + description, active highlight |
| Pull quote | Left teal border, large quotation mark, italic text |
| Flag card | Left border colour by severity (red/amber/green) |
| Score bar | 3px height, animated from 0 to value on mount |
| Status badge | LOCAL / CLOUD / TTS OFF coloured pills |
| Copy button | Ghost, small, inline, "Copied!" confirmation |
| Transcript row | 3-column grid: timestamp · speaker (coloured) · text |
| Progress track | 2px height, teal gradient fill, animated |

### What to Avoid

- Purple gradients, hero illustrations, stock photography
- Rounded card stacks / "bento grids" that look like consumer SaaS
- Anything that reads as a consumer AI product
- Extra animations beyond EQ bars and score bar
- Light mode — dark only

---

## Source Files

| File | What's in it |
|---|---|
| `frontend/index.html` | Full app UI — all components, styles, and JS |
| `pipeline/orchestrator.py` | 7-stage pipeline logic and stage names |
| `api/main.py` | All API endpoints |
| `DECISIONS.md` | Architecture decisions with rationale |
| `architecture.html` | Architecture diagrams (current vs fully local) |

---

## Landing Page — Full Copy (Ready to Drop In)

> All copy below is final draft. Headings, subheadings, body copy, CTAs, and microcopy are all included. Designer drops these into the layout.

---

### NAV

```
Logo    |    How it works    Features    Compliance    |    Book a demo →
```

---

### HERO

**Headline:**
Your briefings. Fully analysed.
Never leaves the building.

**Subheadline:**
Health organisations record dozens of briefings every month — clinical updates, safety notices, staff comms. Every tool that could help publish them sends your audio to an external server. This one doesn't.

**CTA primary:** See how it works →
**CTA secondary:** Book a demo

**Trust strip (3 items, below CTAs):**
- ✓ Runs entirely on your servers
- ✓ No audio processed externally
- ✓ NZ HIPC compliant deployment

---

### PROBLEM SECTION

**Eyebrow label:** THE PROBLEM

**Headline:**
Every other tool is a compliance breach waiting to happen.

**Body:**
ElevenLabs. Descript. Riverside. Adobe Podcast. They're all excellent tools — and they all process your audio on their servers.

In most health environments, that audio contains patient references, staff names, and sensitive operational content. Uploading it to a third-party service isn't just a policy question. It's a notifiable privacy breach.

**Callout block:**
> "One clinical briefing. Uploaded to a cloud transcription service.
> That's a potential breach under the NZ Health Information Privacy Code."

**Transition line:**
We built the alternative.

---

### FEATURES — 4 CARDS

**Section eyebrow:** WHAT IT DOES

**Section headline:** Everything a producer needs. Nothing that leaves your network.

---

**Card 1 — Intelligence Pipeline**

Icon: waveform → document

Headline: Upload a recording. Get back everything.

Body: Drop any audio file and the pipeline runs seven AI stages in sequence — transcription, speaker identification, show notes, chapter markers, a cold open script, and an editorial quality score. Under five minutes for a standard briefing.

---

**Card 2 — Voice Studio**

Icon: microphone

Headline: Clone any voice. Generate broadcast-quality audio.

Body: Record a 30-second voice sample. The studio clones it and reads any script back in that voice — post-processed to broadcast loudness standards. Single narrator or a two-speaker conversation.

---

**Card 3 — Quality Score**

Icon: bar chart with flag

Headline: An honest producer's critique of every episode.

Body: Not a summary — an editorial opinion. The quality score rates each episode on information density, pacing, clarity, and memorability. It flags the exact timestamp where something went wrong, and tells you how to fix it before the next recording.

---

**Card 4 — Local-First Architecture**

Icon: server / lock

Headline: One environment variable. Zero external calls.

Body: Switch between cloud generation and a fully local LLM backend without touching the application code. Same interface, same output. For fully air-gapped deployments, the entire stack — transcription, generation, and voice synthesis — runs on your own hardware.

---

### HOW IT WORKS

**Section eyebrow:** THE PROCESS

**Section headline:** From raw audio to publication-ready content in minutes.

**Step 1**
Label: Drop your audio
Copy: Upload any recording — MP3, WAV, M4A, or OGG. Drag it in or browse. Add a guest name if you want the research stage to run.

**Step 2**
Label: Seven AI stages run in sequence
Copy: Transcription. Speaker identification. Guest research. Show notes. Chapter detection. Cold open. Quality score. Each stage passes its output to the next. You watch them complete in real time.

**Step 3**
Label: Results ready to use
Copy: Five tabs of structured content — ready to copy, export, or send straight to the Voice Studio to synthesise the cold open in your own voice.

---

### QUALITY SCORE SHOWCASE

**Section eyebrow:** QUALITY SCORE

**Headline:**
Not just a summary.
An editorial opinion.

**Left column — copy:**
Most AI tools tell you what was said. The quality score tells you what was wrong with how it was said.

It rates each episode across four dimensions — information density, pacing, clarity, and memorable moments — then flags the specific timestamps where problems occur. Each flag comes with a rewrite suggestion attached.

It doesn't soften the feedback. If the first six seconds are filler, it says so. If a key piece of information was buried and hard to retain, it flags it. If a sentence broke mid-thought, it shows you how to fix it.

That's the tool a producer actually needs.

**Right column — show sample score UI (5.75/10, 3 flags)**

---

### COMPLIANCE STRIP

**Section eyebrow:** DATA SOVEREIGNTY

**Headline:** Built for environments where data can't leave.

**6-item grid:**
- No audio sent to external APIs
- Local LLM mode available
- Fully air-gapped deployment option
- No telemetry or call-home behaviour
- On-premise installation
- NZ HIPC aligned architecture

**CTA:** Read the full compliance detail →

---

### USE CASES

**Section eyebrow:** WHO IT'S FOR

**Headline:** Built for organisations that record and brief regularly.

**3 columns:**

**Health sector**
Clinical teams, infection control leads, and comms managers producing weekly briefings for staff. Compliance rules out every cloud tool. This runs on your own infrastructure.

**Government & public sector**
Regular internal communications that contain sensitive operational content. Same compliance constraints, same solution.

**Any organisation with an internal broadcast**
Legal, finance, education, professional services. If you record briefings that shouldn't leave your network, this runs locally wherever you need it.

---

### FINAL CTA SECTION

**Headline:** Ready to see it running on your content?

**Subheadline:** We'll run a live demo on a real recording from your organisation — or one of ours if you'd rather start there.

**CTA primary:** Book a demo →
**CTA secondary:** Self-hosted setup guide

**Below CTAs — 3 reassurance items:**
- No cloud account required to trial
- Runs on standard server hardware
- Setup takes under an hour

---

### FOOTER

**Left:** Logo + tagline: "AI podcast production for organisations that can't use the cloud."

**Centre columns:**
Product: Features · How it works · Compliance · Pricing
Resources: Setup guide · API docs · Architecture overview

**Right:** Book a demo · Contact

**Bottom bar:** © 2026 Podcast Intelligence · Privacy · Built in New Zealand

---

## Features Page — Full Copy (`/features`)

**Page headline:** Seven AI stages. One pipeline. Everything runs on your hardware.

**Page subheadline:** Each stage is a discrete AI component — not one model doing seven things. They pass structured output to each other so failures are isolated and each component can be swapped independently.

---

**Stage 01 — Transcription**

Eyebrow: STAGE 01
Headline: Speech to text. Every word, with its exact timestamp.

Body: Transcription runs with faster-whisper — a high-accuracy speech recognition model that operates entirely on your server. It produces word-level timestamps for every word in the recording. That precision is what makes everything downstream accurate: chapter markers don't approximate from paragraph breaks, they land on the exact second where a topic shifts.

Technical note: Supports tiny / base / small / medium / large-v3 model sizes. Base handles most clean recordings well. Large-v3 is recommended for accented speech or noisy audio.

---

**Stage 02 — Speaker Diarisation**

Eyebrow: STAGE 02
Headline: Who said what. Labelled throughout.

Body: Diarisation identifies each distinct speaker in the recording and labels every line of the transcript with the correct speaker. In the results view, each speaker gets a distinct colour. In the show notes, notable moments are attributed correctly.

Technical note: Uses pyannote 3.1 when a HuggingFace token is provided. Falls back to silence-gap detection for air-gapped deployments — reliable for clean two-speaker interviews with natural pauses.

---

**Stage 03 — Guest Research**

Eyebrow: STAGE 03 · OPTIONAL
Headline: Context on your guest, injected into the show notes.

Body: If you provide a guest name, this stage pulls background context and injects it into the show notes prompt. The model weaves the context into the episode description rather than appending a bio paragraph. The result reads like a producer who already knew the guest, not a tool that looked them up afterwards.

Technical note: Uses Wikipedia API by default — zero friction, works offline. Swap for Tavily or Exa for real-time web search in production.

---

**Stage 04 — Show Notes**

Eyebrow: STAGE 04
Headline: Structured show notes. Not a wall of text.

Body: Show notes come back as structured JSON — episode title, description, key themes, notable moments with timestamps, and quotable moments with context. The quotable moments aren't just any lines — the model looks for the ones a producer would actually use: surprising statements, counterintuitive claims, lines that would make someone click.

Technical note: Claude Sonnet maintains schema integrity across episode lengths. Local LLM option available via LLM_PROVIDER=local — reliable for short recordings, occasional field drops on longer content.

---

**Stage 05 — Chapter Detection**

Eyebrow: STAGE 05
Headline: Topic shifts marked to the second.

Body: Chapter detection finds where the conversation changes topic and generates a title and summary for each chapter. Because timestamps come from Stage 01's word-level data, each chapter marker is exact — not an approximation. Embed them directly into your podcast player or YouTube description.

---

**Stage 06 — Cold Open**

Eyebrow: STAGE 06
Headline: A 30-second hook. Written to be spoken aloud.

Body: The cold open is the most immediately useful output for most producers. It's a 30-second spoken teaser written from the strongest moment in the episode — designed to be read aloud, not scanned. It hooks on the most surprising or counterintuitive thing in the recording. It ends on a question or an open loop. Use it as your trailer, your email subject line, your social clip narration.

Once generated, you can synthesise it directly in the Voice Studio — hear the cold open in your own cloned voice before the episode is even edited.

---

**Stage 07 — Quality Score**

Eyebrow: STAGE 07
Headline: Four dimensions. Specific flags. Rewrite suggestions attached.

Body: The quality score rates each episode on information density, pacing, clarity, and memorable moments. The overall score gives you a benchmark to track over time. The flagged segments tell you exactly where problems are — what the issue is, how severe it is, and what to say instead.

The model doesn't soften the feedback. A generic opener that wastes six seconds is flagged as medium severity. A sentence that breaks mid-thought and buries critical information is flagged as high. The goal isn't to validate the recording — it's to make the next one better.

---

**Voice Studio section**

Eyebrow: VOICE STUDIO
Headline: The other half.

Body: The intelligence pipeline tells you what's in your audio. The voice studio lets you build audio from scratch — in any voice, on your own hardware.

Give it a 30-second recording of any voice. It clones the voice and uses it to read any script you provide. The output goes through a professional post-processing chain: high-pass filter, compressor, gain, EQ, limiter, and EBU R128 normalisation for broadcast-standard loudness.

Two modes:
- **Narrator** — reads a plain prose script in a single cloned voice
- **Conversation** — takes a JSON dialogue and alternates between two cloned voices, with natural pacing between turns

The most common use: generate the cold open from Stage 06 in the host's own voice, ready to attach to the published episode.

---

## Compliance Page — Full Copy (`/compliance`)

**Page headline:** No audio leaves your network. Ever.

**Page subheadline:** This isn't a privacy policy. It's an architecture decision.

---

**Section 1 — The problem with cloud tools**

Headline: Why every other option is off the table.

Body: The best audio tools in the world — ElevenLabs for voice, Descript for editing, Adobe Podcast for enhancement — all have the same architecture: your audio goes to their servers, gets processed, and the result comes back to you.

That's fine for most use cases. For health, government, legal, and any organisation handling sensitive communications, it creates an immediate compliance problem. The audio you're uploading isn't just a recording — it's operational content that may contain patient references, staff names, financial information, or material covered by professional privilege.

Most organisations don't discover this is a problem until someone asks where the audio went.

---

**Section 2 — How this is different**

Headline: The audio never leaves.

Body: This product has one architectural principle: processing happens on your hardware, not ours or anyone else's.

Transcription runs locally using faster-whisper. Speaker diarisation runs locally. Voice synthesis runs locally. The only external call in the default configuration is to the Claude API for text generation — and that call contains only the transcript text, never the audio file.

If you need zero external calls, one environment variable switches the text generation to a local LLM. The same interface, the same output, running entirely on your own servers.

**Diagram:**

```
CLOUD TOOL:     Your audio → Internet → External server → Processed → Result
THIS PRODUCT:   Your audio → Your server → Local processing → Result
                                          (nothing leaves)
```

---

**Section 3 — Deployment options**

Headline: Three ways to deploy. All of them local.

**Option 1 — Default (recommended for most organisations)**
- Transcription: local (faster-whisper)
- Generation: Claude API (text only — no audio sent)
- Voice synthesis: local (Chatterbox TTS)
- Guest research: Wikipedia (offline capable)

**Option 2 — Fully local**
- Transcription: local
- Generation: local LLM via LM Studio (Qwen2.5-14B or equivalent)
- Voice synthesis: local
- Guest research: local
- External calls: none
- Note: Requires GPU with 16GB+ VRAM for reliable structured output

**Option 3 — Air-gapped**
- All of Option 2
- Guest research: Kiwix offline Wikipedia snapshot
- Network: not required after initial setup
- Suitable for: environments with no external network access

---

**Section 4 — What data is stored**

Headline: Nothing persists that shouldn't.

- Audio files are written to a temporary directory and deleted after the pipeline completes
- Results are held in memory during the session (production deployments use your own database)
- No usage logs, no telemetry, no analytics calls to external services
- No model training on your content

---

**Section 5 — NZ HIPC**

Headline: Designed with NZ health privacy requirements in mind.

Body: The architecture was designed specifically for the constraints of NZ health sector deployment — particularly the requirement that health information not be transmitted to overseas servers without explicit consent and controls.

The fully local and air-gapped deployment modes are designed to satisfy these requirements in practice. Your organisation's privacy officer and legal team should review the deployment configuration for your specific context — we're happy to walk through the architecture with them.

CTA: Talk to us about your deployment →
