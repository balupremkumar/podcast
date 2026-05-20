"""
Stage 2: Speaker diarisation — who said what.

Tries pyannote.audio first (production-grade, requires HF_TOKEN).
Falls back to a simple VAD-based approach that detects silence gaps and
alternates speaker labels. The fallback works well for structured interviews
where speakers take clear turns. It fails on overlapping speech.

This is an honest architectural choice: pyannote is the right tool, but
the VAD fallback means the demo works without a HuggingFace account.
"""

import os


def diarize(audio_path: str, num_speakers: int = 2) -> list:
    """
    Identify speaker segments in audio.

    Returns:
        [
            {"start": 0.0, "end": 8.2, "speaker": "SPEAKER_00"},
            {"start": 8.2, "end": 15.5, "speaker": "SPEAKER_01"},
            ...
        ]
    """
    hf_token = os.environ.get("HF_TOKEN")

    if hf_token:
        print("  [diarize] Using pyannote.audio (production-grade)")
        try:
            return _diarize_pyannote(audio_path, num_speakers, hf_token)
        except Exception as e:
            print(f"  [diarize] pyannote failed: {e} — falling back to VAD")

    print("  [diarize] Using VAD fallback (set HF_TOKEN for better results)")
    return _diarize_vad(audio_path)


def merge_with_transcript(transcript_segments: list, speaker_segments: list) -> list:
    """
    Assign speaker labels to each transcript segment by finding the
    diarisation segment with maximum overlap at the midpoint.
    """
    merged = []
    for seg in transcript_segments:
        midpoint = (seg["start"] + seg["end"]) / 2
        speaker = "SPEAKER_00"

        best_overlap = 0.0
        for sp in speaker_segments:
            overlap = min(seg["end"], sp["end"]) - max(seg["start"], sp["start"])
            if overlap > best_overlap:
                best_overlap = overlap
                speaker = sp["speaker"]

        merged.append(
            {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"],
                "speaker": speaker,
                "words": seg.get("words", []),
            }
        )

    return merged


def _diarize_pyannote(audio_path: str, num_speakers: int, hf_token: str) -> list:
    from pyannote.audio import Pipeline
    import torch

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token,
    )

    diarization = pipeline(audio_path, num_speakers=num_speakers)

    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append(
            {
                "start": round(turn.start, 2),
                "end": round(turn.end, 2),
                "speaker": speaker,
            }
        )

    print(f"  [diarize] pyannote found {len(set(s['speaker'] for s in segments))} speakers")
    return segments


def _diarize_vad(audio_path: str) -> list:
    """
    Simple VAD-based diarisation.
    Detects silence gaps > 1.5s and alternates speaker labels.
    Works for structured interviews; fails on overlapping speech.
    """
    import numpy as np
    import soundfile as sf

    audio, sr = sf.read(audio_path)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    frame_len = int(sr * 0.1)  # 100ms frames
    n_frames = len(audio) // frame_len

    rms = np.array(
        [
            np.sqrt(np.mean(audio[i * frame_len : (i + 1) * frame_len] ** 2))
            for i in range(n_frames)
        ]
    )

    # Adaptive silence threshold: 20th percentile of non-zero energy
    nonzero = rms[rms > 0]
    if len(nonzero) == 0:
        return [{"start": 0.0, "end": len(audio) / sr, "speaker": "SPEAKER_00"}]

    threshold = np.percentile(nonzero, 20)
    is_speech = rms > threshold

    min_gap_frames = 15   # 1.5s silence triggers speaker change
    min_seg_frames = 5    # 0.5s minimum segment length

    segments = []
    speaker_idx = 0
    in_speech = False
    speech_start = 0.0
    silence_count = 0

    for i, s in enumerate(is_speech):
        if s:
            if not in_speech:
                speech_start = i * 0.1
                in_speech = True
            silence_count = 0
        else:
            if in_speech:
                silence_count += 1
                if silence_count >= min_gap_frames:
                    seg_end = (i - silence_count) * 0.1
                    if (seg_end - speech_start) >= (min_seg_frames * 0.1):
                        segments.append(
                            {
                                "start": round(speech_start, 2),
                                "end": round(seg_end, 2),
                                "speaker": f"SPEAKER_0{speaker_idx % 2}",
                            }
                        )
                        speaker_idx += 1
                    in_speech = False
                    silence_count = 0

    # Final segment
    if in_speech:
        seg_end = round(n_frames * 0.1, 2)
        if (seg_end - speech_start) >= 0.5:
            segments.append(
                {
                    "start": round(speech_start, 2),
                    "end": seg_end,
                    "speaker": f"SPEAKER_0{speaker_idx % 2}",
                }
            )

    print(f"  [diarize] VAD found {len(segments)} segments, {speaker_idx + 1} speaker changes")
    return segments
