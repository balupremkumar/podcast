const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageNumber, Header, Footer, TableOfContents
} = require('docx');
const fs = require('fs');

const ACCENT = "1F6B8E";
const ACCENT_LIGHT = "E8F4FA";
const GREY_LIGHT = "F5F5F5";
const BORDER_COLOR = "CCCCCC";
const WHITE = "FFFFFF";

const cellBorder = { style: BorderStyle.SINGLE, size: 1, color: BORDER_COLOR };
const allBorders = { top: cellBorder, bottom: cellBorder, left: cellBorder, right: cellBorder };
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 120 },
    children: [new TextRun({ text, bold: true, size: 36, font: "Arial", color: "1A1A1A" })]
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 80 },
    children: [new TextRun({ text, bold: true, size: 28, font: "Arial", color: ACCENT })]
  });
}

function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 60 },
    children: [new TextRun({ text, bold: true, size: 24, font: "Arial", color: "333333" })]
  });
}

function body(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 60, after: 60 },
    children: [new TextRun({ text, size: 22, font: "Arial", ...opts })]
  });
}

function bullet(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "bullets", level },
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, size: 22, font: "Arial" })]
  });
}

function numbered(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "numbers", level },
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, size: 22, font: "Arial" })]
  });
}

function spacer() {
  return new Paragraph({ spacing: { before: 60, after: 60 }, children: [new TextRun("")] });
}

function divider() {
  return new Paragraph({
    spacing: { before: 120, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: BORDER_COLOR, space: 1 } },
    children: [new TextRun("")]
  });
}

function calloutBox(label, text) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [
      new TableRow({
        children: [new TableCell({
          borders: { top: { style: BorderStyle.SINGLE, size: 8, color: ACCENT }, bottom: cellBorder, left: { style: BorderStyle.SINGLE, size: 8, color: ACCENT }, right: cellBorder },
          shading: { fill: ACCENT_LIGHT, type: ShadingType.CLEAR },
          width: { size: 9360, type: WidthType.DXA },
          margins: { top: 140, bottom: 140, left: 200, right: 200 },
          children: [
            new Paragraph({ spacing: { before: 0, after: 60 }, children: [new TextRun({ text: label, bold: true, size: 22, font: "Arial", color: ACCENT })] }),
            new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text, size: 22, font: "Arial", color: "1A1A1A" })] })
          ]
        })]
      })
    ]
  });
}

function phaseBox(phase, duration, items) {
  const rows = [
    new TableRow({
      children: [new TableCell({
        borders: allBorders,
        shading: { fill: ACCENT, type: ShadingType.CLEAR },
        width: { size: 9360, type: WidthType.DXA },
        margins: { top: 100, bottom: 100, left: 200, right: 200 },
        children: [new Paragraph({
          children: [
            new TextRun({ text: phase, bold: true, size: 24, font: "Arial", color: WHITE }),
            new TextRun({ text: "  —  " + duration, size: 20, font: "Arial", color: "D0E8F5" })
          ]
        })]
      })]
    }),
    ...items.map(item => new TableRow({
      children: [new TableCell({
        borders: allBorders,
        shading: { fill: WHITE, type: ShadingType.CLEAR },
        width: { size: 9360, type: WidthType.DXA },
        margins: { top: 80, bottom: 80, left: 200, right: 200 },
        children: [new Paragraph({
          children: [
            new TextRun({ text: "•  ", size: 22, font: "Arial", color: ACCENT }),
            new TextRun({ text: item, size: 22, font: "Arial" })
          ]
        })]
      })]
    }))
  ];
  return new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: [9360], rows });
}

function pricingTable() {
  const headerCell = (text) => new TableCell({
    borders: allBorders,
    shading: { fill: ACCENT, type: ShadingType.CLEAR },
    width: { size: 2340, type: WidthType.DXA },
    margins: { top: 100, bottom: 100, left: 160, right: 160 },
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, size: 20, font: "Arial", color: WHITE })] })]
  });
  const dataCell = (text, shade = WHITE) => new TableCell({
    borders: allBorders,
    shading: { fill: shade, type: ShadingType.CLEAR },
    width: { size: 2340, type: WidthType.DXA },
    margins: { top: 80, bottom: 80, left: 160, right: 160 },
    children: [new Paragraph({ children: [new TextRun({ text, size: 20, font: "Arial" })] })]
  });

  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2340, 2340, 2340, 2340],
    rows: [
      new TableRow({ children: [headerCell("Tier"), headerCell("Target"), headerCell("Staff Size"), headerCell("Annual Price (NZD)")] }),
      new TableRow({ children: [dataCell("Starter"), dataCell("Small PHOs, iwi providers"), dataCell("Under 50 staff"), dataCell("$8,000 – $12,000")] }),
      new TableRow({ children: [dataCell("Standard", GREY_LIGHT), dataCell("Mid-size PHOs, NGOs", GREY_LIGHT), dataCell("50–200 staff", GREY_LIGHT), dataCell("$18,000 – $28,000", GREY_LIGHT)] }),
      new TableRow({ children: [dataCell("Enterprise"), dataCell("Large PHOs, regional networks"), dataCell("200+ staff"), dataCell("$45,000 – $70,000")] }),
      new TableRow({ children: [dataCell("Implementation fee", GREY_LIGHT), dataCell("All tiers", GREY_LIGHT), dataCell("One-off", GREY_LIGHT), dataCell("$2,000 – $5,000", GREY_LIGHT)] }),
    ]
  });
}

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 560, hanging: 280 } } } },
          { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1000, hanging: 280 } } } }
        ]
      },
      {
        reference: "numbers",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 560, hanging: 280 } } } }
        ]
      }
    ]
  },
  styles: {
    default: {
      document: { run: { font: "Arial", size: 22 } }
    },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 36, bold: true, font: "Arial", color: "1A1A1A" }, paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 28, bold: true, font: "Arial", color: ACCENT }, paragraph: { spacing: { before: 280, after: 80 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true, font: "Arial", color: "333333" }, paragraph: { spacing: { before: 200, after: 60 }, outlineLevel: 2 } },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: BORDER_COLOR, space: 1 } },
          children: [
            new TextRun({ text: "Health Audio Studio", bold: true, size: 18, font: "Arial", color: ACCENT }),
            new TextRun({ text: "   —   Product Plan", size: 18, font: "Arial", color: "888888" })
          ]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: BORDER_COLOR, space: 1 } },
          children: [
            new TextRun({ text: "Page ", size: 18, font: "Arial", color: "888888" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 18, font: "Arial", color: "888888" }),
            new TextRun({ text: " of ", size: 18, font: "Arial", color: "888888" }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, font: "Arial", color: "888888" })
          ]
        })]
      })
    },
    children: [

      // ── TITLE PAGE ──────────────────────────────────────────────────────────
      spacer(), spacer(),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 480, after: 120 },
        children: [new TextRun({ text: "Health Audio Studio", bold: true, size: 64, font: "Arial", color: ACCENT })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 80 },
        children: [new TextRun({ text: "Product Plan", size: 32, font: "Arial", color: "555555" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 480 },
        children: [new TextRun({ text: "AI-Powered Audio Intelligence for NZ Health Organisations", size: 24, font: "Arial", color: "777777" })]
      }),
      divider(),
      spacer(),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 120, after: 60 },
        children: [new TextRun({ text: "Confidential — May 2026", size: 20, font: "Arial", color: "999999" })]
      }),
      spacer(), spacer(),

      // Page break before TOC
      new Paragraph({ pageBreakBefore: true, children: [new TextRun("")] }),

      // ── TABLE OF CONTENTS ───────────────────────────────────────────────────
      h1("Contents"),
      new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-3" }),
      new Paragraph({ pageBreakBefore: true, children: [new TextRun("")] }),

      // ── SECTION 1: OVERVIEW ─────────────────────────────────────────────────
      h1("1. What Is Health Audio Studio?"),
      body("Health Audio Studio is a fully local AI tool built specifically for New Zealand health organisations. It turns recorded audio — meetings, clinical briefings, patient education sessions — into structured, usable content. Everything runs on your own hardware. No data leaves your organisation."),
      spacer(),

      calloutBox(
        "Privacy by design",
        "Voice recordings are classified as biometric personal health information under the NZ Health Information Privacy Code 2020. Health Audio Studio processes all audio on-device — nothing is sent to cloud services, external APIs, or third-party servers. Compliance is built into the architecture, not bolted on."
      ),
      spacer(),

      h2("What it does"),
      numbered("Clones a staff member’s voice from a short 10–30 second audio sample"),
      numbered("Processes a recorded clinical briefing, meeting, or podcast episode"),
      numbered("Automatically generates: timestamped transcript, show notes, chapter markers, a cold open script, and an episode quality score"),
      numbered("Synthesises the output back into audio using the cloned voice — so your content sounds like your people, at scale"),
      spacer(),

      h2("Why it matters for health organisations"),
      body("Health organisations produce large volumes of written content that frequently goes unread. Audio is more accessible and more engaging — particularly for Pacific and Māori communities where trusted voices matter. Health Audio Studio lets a single communicator produce professional audio content without re-recording every time."),
      spacer(),
      body("The fully local architecture satisfies a requirement that cloud tools like Otter.ai, Descript, and similar products cannot meet: no staff or patient voice data leaves the device."),
      spacer(),

      new Paragraph({ pageBreakBefore: true, children: [new TextRun("")] }),

      // ── SECTION 2: HOW IT WORKS ──────────────────────────────────────────────
      h1("2. How It Works"),
      body("The product has two connected capabilities that work together as a single system."),
      spacer(),

      h2("Voice cloning"),
      body("A staff member records 10–30 seconds of natural speech. The system analyses their vocal characteristics and stores a voice profile. That profile can then be used to synthesise any text in their voice — without the person needing to re-record."),
      spacer(),
      body("Voice profiles are stored locally. They can be named, managed, and deleted at any time. No voice data leaves the machine."),
      spacer(),

      h2("The 7-stage AI pipeline"),
      body("When you upload an audio file, it passes through seven AI processing stages in sequence:"),
      spacer(),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [600, 2200, 6560],
        rows: [
          new TableRow({
            children: [
              new TableCell({ borders: allBorders, shading: { fill: ACCENT, type: ShadingType.CLEAR }, width: { size: 600, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "#", bold: true, size: 20, font: "Arial", color: WHITE })] })] }),
              new TableCell({ borders: allBorders, shading: { fill: ACCENT, type: ShadingType.CLEAR }, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Stage", bold: true, size: 20, font: "Arial", color: WHITE })] })] }),
              new TableCell({ borders: allBorders, shading: { fill: ACCENT, type: ShadingType.CLEAR }, width: { size: 6560, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "What it produces", bold: true, size: 20, font: "Arial", color: WHITE })] })] }),
            ]
          }),
          ...[
            ["1", "Transcription", "Full text transcript with word-level timestamps"],
            ["2", "Speaker identification", "Labels who said what throughout the recording"],
            ["3", "Guest research", "Automatically pulls context about speakers from offline sources"],
            ["4", "Show notes", "Structured summary: title, themes, notable moments, quotable lines"],
            ["5", "Chapter markers", "Detects topic shifts and generates timestamped chapters"],
            ["6", "Cold open script", "A 30-second spoken hook to introduce the content"],
            ["7", "Quality score", "Per-segment scoring for clarity, structure, pacing, and engagement"],
          ].map(([num, stage, what], i) =>
            new TableRow({
              children: [
                new TableCell({ borders: allBorders, shading: { fill: i % 2 === 0 ? WHITE : GREY_LIGHT, type: ShadingType.CLEAR }, width: { size: 600, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: num, bold: true, size: 20, font: "Arial", color: ACCENT })] })] }),
                new TableCell({ borders: allBorders, shading: { fill: i % 2 === 0 ? WHITE : GREY_LIGHT, type: ShadingType.CLEAR }, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: stage, size: 20, font: "Arial", bold: true })] })] }),
                new TableCell({ borders: allBorders, shading: { fill: i % 2 === 0 ? WHITE : GREY_LIGHT, type: ShadingType.CLEAR }, width: { size: 6560, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: what, size: 20, font: "Arial" })] })] }),
              ]
            })
          )
        ]
      }),
      spacer(),

      h2("The full loop"),
      body("Audio in → intelligence out → audio back out. The cold open script produced by stage 6 can be synthesised immediately in any registered cloned voice. One recording becomes both structured written content and production-ready audio — without a studio."),
      spacer(),

      new Paragraph({ pageBreakBefore: true, children: [new TextRun("")] }),

      // ── SECTION 3: USER INTERFACE ────────────────────────────────────────────
      h1("3. User Interface"),
      body("The interface runs in a browser at localhost (on the same machine as the processing). No internet connection is required. No login is needed."),
      spacer(),

      h2("Layout"),
      body("The screen is divided into two zones:"),
      bullet("Sidebar (left): Lists registered voice profiles and recent sessions. Shows a permanent privacy notice at the bottom."),
      bullet("Main canvas (right): Switches between three views depending on where you are in the workflow."),
      spacer(),

      h2("Three views"),

      h3("1. Upload"),
      body("Give the session a name, drop in an audio file, and start processing. Clean, minimal — one thing to do."),
      spacer(),

      h3("2. Processing"),
      body("A step-by-step progress list shows each of the 7 AI stages, with a tick when done, a progress indicator for the active stage, and real elapsed time for completed stages. The screen shows one clear line of reassurance:"),
      spacer(),
      new Paragraph({
        spacing: { before: 80, after: 80 },
        indent: { left: 720 },
        children: [new TextRun({ text: "“Running locally on your machine. Audio is not transmitted anywhere.”", italics: true, size: 22, font: "Arial", color: "555555" })]
      }),
      spacer(),

      h3("3. Results"),
      body("Five tabs present the pipeline output:"),
      bullet("Transcript: Full speaker-labelled transcript. Speaker names are editable. Timestamps in monospaced font."),
      bullet("Show Notes: Structured summary. All text is click-to-edit — AI output is a first draft, not a final product."),
      bullet("Chapters: Timestamped chapter list. Chapter titles are editable."),
      bullet("Cold Open: The 30-second script, editable, with a voice synthesis panel below it."),
      bullet("Quality Score: Numeric scores for clarity, structure, pacing, and engagement, with specific suggestions."),
      spacer(),

      h2("Voice synthesis in the results view"),
      body("On the Cold Open tab, a dropdown lists all registered voice profiles. Select a voice, click Generate, and an audio player appears with the synthesised cold open. Download as MP3."),
      spacer(),
      body("If the script is edited after generating audio, the player is greyed out with a prompt to regenerate. The system never serves stale audio."),
      spacer(),

      h2("Privacy signals"),
      body("Trust signals are built into the interface at three levels:"),
      bullet("Always visible: A small badge at the bottom of the sidebar reads “All data stays local. No cloud. No login.” Calm, always present, never alarming."),
      bullet("At the moment of risk: While a file is processing, the screen includes one plain line about local processing. This is the moment users are most likely to wonder about data handling."),
      bullet("On demand: A help icon opens a plain-language explainer for IT or privacy officers: what files are stored, where processing runs, what leaves the machine (nothing)."),
      spacer(),

      new Paragraph({ pageBreakBefore: true, children: [new TextRun("")] }),

      // ── SECTION 4: ARCHITECTURE ──────────────────────────────────────────────
      h1("4. Technical Architecture"),
      body("This section is intended for IT staff and procurement reviewers. Plain-language summary first, then detail."),
      spacer(),

      calloutBox(
        "Plain language summary",
        "Three small software services run on your machine and talk only to each other. No network connection is required or used. All files — audio uploads, transcripts, voice profiles, generated audio — are stored in a single directory on your hardware. A compliance flag prevents the system from starting if any cloud path is accidentally enabled."
      ),
      spacer(),

      h2("Three services"),
      bullet("API Gateway (port 8000): Handles browser requests. Never does AI work. Always stays responsive."),
      bullet("Pipeline Worker: Runs the 7 AI stages in sequence. Processes one job at a time."),
      bullet("Synthesis Worker: Handles voice generation. Runs separately so slow synthesis jobs do not block new uploads."),
      spacer(),
      body("All three services bind to the local machine only (127.0.0.1). They cannot be reached from outside the device."),
      spacer(),

      h2("Data storage"),
      body("All data lives under a single configurable root directory:"),
      bullet("uploads/ — incoming audio files"),
      bullet("voice_samples/ — voice registration audio"),
      bullet("voice_embeddings/ — processed voice profiles"),
      bullet("outputs/{job_id}/ — all pipeline outputs per job"),
      spacer(),
      body("Jobs are tracked in a local SQLite database. Each job records its stage-by-stage progress, so if a process restarts mid-job, work is not lost."),
      spacer(),

      h2("Compliance mode"),
      body("A single environment flag — COMPLIANCE_MODE=strict — enforces local-only operation at startup:"),
      bullet("Asserts the AI inference backend is local (LM Studio + Qwen2.5 model)"),
      bullet("Asserts the voice synthesis backend is local (Chatterbox TTS)"),
      bullet("Asserts the research backend is offline (local Wikipedia mirror)"),
      bullet("Binds all services to localhost only"),
      bullet("Logs a compliance confirmation line at startup"),
      spacer(),
      body("If any assertion fails, the application refuses to start. This is a structural guarantee, not a setting that can be accidentally overridden at runtime."),
      spacer(),

      h2("What can be switched to cloud (for non-health use)"),
      body("The architecture supports optional cloud backends for organisations that do not require full local operation:"),
      bullet("LLM inference: Claude Sonnet API (Anthropic) instead of local Qwen model"),
      bullet("Voice synthesis: Azure Speech instead of local Chatterbox"),
      bullet("Research: Live Wikipedia API instead of offline mirror"),
      spacer(),
      body("Switching is done via environment variables, not code changes. Health sector deployments use COMPLIANCE_MODE=strict, which disables all of the above."),
      spacer(),

      h2("What stays from the existing build"),
      body("The existing pipeline is already working. The following components carry forward unchanged:"),
      bullet("All 7 AI stage modules and their prompt templates"),
      bullet("faster-whisper transcription engine"),
      bullet("pyannote speaker diarisation"),
      bullet("LLM dual-backend switch (cloud ↔ local)"),
      bullet("TTS dual-backend switch (Chatterbox ↔ Azure)"),
      spacer(),

      h2("Open technical question"),
      calloutBox(
        "Action required before full build",
        "Chatterbox TTS currently accepts a voice sample at inference time. The architecture requires a ‘register once, reuse’ pattern where a voice embedding is stored and loaded per-job. This needs a one-day technical spike to confirm it works before committing to the full voice profile build."
      ),
      spacer(),

      new Paragraph({ pageBreakBefore: true, children: [new TextRun("")] }),

      // ── SECTION 5: BUSINESS STRATEGY ─────────────────────────────────────────
      h1("5. Business Strategy"),

      h2("Positioning"),
      new Paragraph({
        spacing: { before: 80, after: 80 },
        indent: { left: 360 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 8 } },
        children: [new TextRun({ text: "“The only AI content production tool built for NZ health organisations that keeps patient and staff voice data entirely on your own hardware.”", italics: true, bold: true, size: 24, font: "Arial", color: "1A1A1A" })]
      }),
      spacer(),
      body("Lead with what the product removes — compliance risk, re-recording time, data handling anxiety — before what it adds."),
      spacer(),

      h2("Ideal customer"),
      body("Primary Health Organisations (PHOs) serving Māori and Pacific communities are the first target. Specifically:"),
      bullet("[PHO name]"),
      bullet("[PHO name]"),
      bullet("[PHO name]"),
      bullet("[PHO name]"),
      spacer(),
      body("Why PHOs first: they have Ministry ring-fenced funding for accessible and culturally appropriate content production, they are large enough to have a genuine content problem, and they are small enough to make procurement decisions without a 12-month committee process."),
      spacer(),
      body("Hold off on Health NZ / Te Whatu Ora: procurement is currently frozen following the DHB merger restructure. Return once a PHO reference customer exists."),
      spacer(),
      body("Secondary target: iwi health providers. Smaller organisations, but the data sovereignty framing resonates strongly with existing values around tino rangatiratanga over organisational data."),
      spacer(),

      h2("Pricing"),
      body("Annual site licence, tiered by organisation size. Site licences are the right model for health organisations — they think in sites and budgets, not individual seats."),
      spacer(),
      pricingTable(),
      spacer(),
      body("Anchored against the cost of a part-time communications contractor: $40,000–$60,000 per year. The product should cost less than the human it augments."),
      spacer(),
      body("The implementation fee covers on-site setup, hardware assessment, and staff onboarding. It signals that this is a serious enterprise deployment and protects margin on smaller customers."),
      spacer(),

      h2("The HIPC compliance advantage"),
      body("Most NZ health organisations using cloud transcription tools (Otter.ai, Descript, Teams transcription) have not worked through the implications of the NZ Health Information Privacy Code 2020 for voice recordings. Staff voice recordings used to create AI profiles are biometric information. Processing them on a cloud server without a data processing agreement creates material legal risk."),
      spacer(),
      body("Recommended action: Commission a one-page legal opinion (~$1,500 NZD) from a NZ health privacy specialist confirming this risk. This transforms the compliance claim from a marketing statement into a documented legal position that a procurement officer can put in a file. Cloud competitors cannot replicate this."),
      spacer(),
      body("For Māori and Pacific health providers, frame data sovereignty in terms of tino rangatiratanga: your staff voices and patient data remain under your control, on your hardware, under your kaitiakitanga."),
      spacer(),

      h2("How to reach buyers without a sales team"),
      numbered("HINZ conference (Health Informatics New Zealand): The primary conference for the exact buyer persona — digital health leads, communications managers, CIOs. 400–600 qualified contacts. A demo or lightning talk is the highest-ROI activity available."),
      numbered("Warm introductions: The NZ health sector is a small, networked community. One warm introduction to a PHO digital health or communications lead is worth more than 200 cold approaches."),
      numbered("LinkedIn content: One practical explainer on the HIPC/cloud risk for health organisations using standard transcription tools. Creates the category problem your product solves. Tag toward health communications and digital health audiences."),
      spacer(),

      h2("Pilot structure"),
      body("An 8-week pilot with one communications team on one use case (e.g. converting recorded staff briefings into accessible audio for a Pacific patient cohort)."),
      spacer(),
      bullet("Price: Free, or a nominal $1,500 setup fee to establish a real procurement relationship"),
      bullet("From them: honest feedback, a written testimonial if it works, permission to be referenced by name"),
      bullet("Design the pilot to produce measurable outputs: hours saved per piece, number of audio outputs, staff time freed"),
      bullet("These numbers become the sales narrative for every subsequent conversation"),
      spacer(),

      h2("On the job-demo origin"),
      body("Do not hide where this came from. The right frame:"),
      spacer(),
      new Paragraph({
        spacing: { before: 80, after: 80 },
        indent: { left: 720 },
        children: [new TextRun({ text: "“I built this to solve data sovereignty from the architecture up. Organisations I showed it to said they’d pay for it. So I’m finding out if that’s true.”", italics: true, size: 22, font: "Arial", color: "555555" })]
      }),
      spacer(),
      body("In the NZ health sector, a locally built, problem-first origin story is a credibility signal. Practitioners respond better to a builder who started with the problem than to a startup founder running a pitch."),
      spacer(),

      new Paragraph({ pageBreakBefore: true, children: [new TextRun("")] }),

      // ── SECTION 6: PHASED PLAN ───────────────────────────────────────────────
      h1("6. Phased Build Plan"),
      body("Total estimated time to pilot-ready: 6–10 weeks. Phase 4 (market) runs in parallel with Phase 3."),
      spacer(),

      phaseBox("Phase 1 — Foundation", "3–4 weeks", [
        "Voice profile registration and embedding storage",
        "Split into three separate processes: API, pipeline worker, synthesis worker",
        "SQLite job table with per-stage state tracking",
        "COMPLIANCE_MODE=strict startup enforcement block",
        "Chatterbox embedding spike — confirm store-once/reuse pattern (do this first)",
      ]),
      spacer(),

      phaseBox("Phase 2 — Unified Interface", "2–3 weeks", [
        "Sidebar with voice profiles list and session history",
        "Voice registration wizard (3-step: name → upload sample → cloning progress)",
        "Processing view with stage-by-stage progress indicators",
        "Cold Open tab synthesis wired to registered voice profiles",
        "Three-layer privacy signal implementation",
      ]),
      spacer(),

      phaseBox("Phase 3 — Pilot Ready", "1–2 weeks", [
        "DELETE endpoints for jobs and voice profiles (data minimisation)",
        "Session naming and history",
        "Speaker renaming in transcript (propagates through all outputs)",
        "Inline text editing across all result tabs",
        "Single launcher script: one command starts all three processes",
        "Commission HIPC legal opinion",
      ]),
      spacer(),

      phaseBox("Phase 4 — Market", "Parallel to Phase 3", [
        "Publish LinkedIn HIPC/cloud risk explainer",
        "Identify and contact three warm PHO leads",
        "Register for HINZ conference (or submit a talk proposal)",
        "Secure first pilot agreement",
      ]),
      spacer(),

      new Paragraph({ pageBreakBefore: true, children: [new TextRun("")] }),

      // ── SECTION 7: RISKS & DEPENDENCIES ──────────────────────────────────────
      h1("7. Risks and Dependencies"),
      spacer(),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2400, 3480, 3480],
        rows: [
          new TableRow({
            children: [
              new TableCell({ borders: allBorders, shading: { fill: ACCENT, type: ShadingType.CLEAR }, width: { size: 2400, type: WidthType.DXA }, margins: { top: 100, bottom: 100, left: 140, right: 140 }, children: [new Paragraph({ children: [new TextRun({ text: "Item", bold: true, size: 20, font: "Arial", color: WHITE })] })] }),
              new TableCell({ borders: allBorders, shading: { fill: ACCENT, type: ShadingType.CLEAR }, width: { size: 3480, type: WidthType.DXA }, margins: { top: 100, bottom: 100, left: 140, right: 140 }, children: [new Paragraph({ children: [new TextRun({ text: "Detail", bold: true, size: 20, font: "Arial", color: WHITE })] })] }),
              new TableCell({ borders: allBorders, shading: { fill: ACCENT, type: ShadingType.CLEAR }, width: { size: 3480, type: WidthType.DXA }, margins: { top: 100, bottom: 100, left: 140, right: 140 }, children: [new Paragraph({ children: [new TextRun({ text: "Resolution", bold: true, size: 20, font: "Arial", color: WHITE })] })] }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: allBorders, shading: { fill: WHITE, type: ShadingType.CLEAR }, width: { size: 2400, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 140, right: 140 }, children: [new Paragraph({ children: [new TextRun({ text: "Chatterbox embedding storage", bold: true, size: 20, font: "Arial", color: "CC3300" })] })] }),
              new TableCell({ borders: allBorders, shading: { fill: WHITE, type: ShadingType.CLEAR }, width: { size: 3480, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 140, right: 140 }, children: [new Paragraph({ children: [new TextRun({ text: "Current TTS requires voice sample at inference time. Architecture needs store-once/reuse. Unconfirmed.", size: 20, font: "Arial" })] })] }),
              new TableCell({ borders: allBorders, shading: { fill: WHITE, type: ShadingType.CLEAR }, width: { size: 3480, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 140, right: 140 }, children: [new Paragraph({ children: [new TextRun({ text: "One-day spike before committing to full voice profile build. Do this first in Phase 1.", size: 20, font: "Arial" })] })] }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: allBorders, shading: { fill: GREY_LIGHT, type: ShadingType.CLEAR }, width: { size: 2400, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 140, right: 140 }, children: [new Paragraph({ children: [new TextRun({ text: "Pilot timeline", bold: true, size: 20, font: "Arial" })] })] }),
              new TableCell({ borders: allBorders, shading: { fill: GREY_LIGHT, type: ShadingType.CLEAR }, width: { size: 3480, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 140, right: 140 }, children: [new Paragraph({ children: [new TextRun({ text: "Growth target is 8 weeks. Architecture build is 3–5 weeks. Tight overlap.", size: 20, font: "Arial" })] })] }),
              new TableCell({ borders: allBorders, shading: { fill: GREY_LIGHT, type: ShadingType.CLEAR }, width: { size: 3480, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 140, right: 140 }, children: [new Paragraph({ children: [new TextRun({ text: "Scope pilot to one use case and one voice profile. Existing pipeline already works — pilot can start on Phase 3 foundations.", size: 20, font: "Arial" })] })] }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: allBorders, shading: { fill: WHITE, type: ShadingType.CLEAR }, width: { size: 2400, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 140, right: 140 }, children: [new Paragraph({ children: [new TextRun({ text: "Hardware (AMD GPU)", bold: true, size: 20, font: "Arial" })] })] }),
              new TableCell({ borders: allBorders, shading: { fill: WHITE, type: ShadingType.CLEAR }, width: { size: 3480, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 140, right: 140 }, children: [new Paragraph({ children: [new TextRun({ text: "AMD RX 9070 XT, ROCm blocked on Windows. TTS runs CPU-only at ~3x realtime (30s audio = ~90s synthesis).", size: 20, font: "Arial" })] })] }),
              new TableCell({ borders: allBorders, shading: { fill: WHITE, type: ShadingType.CLEAR }, width: { size: 3480, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 140, right: 140 }, children: [new Paragraph({ children: [new TextRun({ text: "Architecture handles this correctly — synthesis runs as a background job. Acceptable for async delivery. Improves if ROCm support matures.", size: 20, font: "Arial" })] })] }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: allBorders, shading: { fill: GREY_LIGHT, type: ShadingType.CLEAR }, width: { size: 2400, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 140, right: 140 }, children: [new Paragraph({ children: [new TextRun({ text: "Health NZ procurement", bold: true, size: 20, font: "Arial" })] })] }),
              new TableCell({ borders: allBorders, shading: { fill: GREY_LIGHT, type: ShadingType.CLEAR }, width: { size: 3480, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 140, right: 140 }, children: [new Paragraph({ children: [new TextRun({ text: "Centralised procurement at Health NZ is slow and currently disrupted.", size: 20, font: "Arial" })] })] }),
              new TableCell({ borders: allBorders, shading: { fill: GREY_LIGHT, type: ShadingType.CLEAR }, width: { size: 3480, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 140, right: 140 }, children: [new Paragraph({ children: [new TextRun({ text: "Target PHOs first. Return to Health NZ once a reference customer exists.", size: 20, font: "Arial" })] })] }),
            ]
          }),
        ]
      }),
      spacer(), spacer(),

      // ── SECTION 8: FIRST 90 DAYS ─────────────────────────────────────────────
      h1("8. First 90 Days — Action List"),
      body("In priority order:"),
      spacer(),
      numbered("Run the Chatterbox embedding spike — one day, confirms or changes the voice profile architecture"),
      numbered("Commission the HIPC legal opinion — ~$1,500, turns compliance into a documented legal position"),
      numbered("Identify three warm PHO contacts via clinical networks"),
      numbered("Publish the LinkedIn HIPC/cloud risk explainer"),
      numbered("Secure one pilot agreement with a PHO or iwi health provider"),
      numbered("Register for the HINZ conference, or submit a talk proposal"),
      spacer(),

      calloutBox(
        "The critical path",
        "The product is ready enough to pilot. The commercial risk is not product readiness — it is getting in front of the right buyer before the early-mover window closes. That window is approximately 12–18 months, after which larger vendors will solve the compliance problem or Health NZ will issue guidance that commoditises it. Move fast on the pilot. Everything else follows from that reference customer."
      ),
      spacer(), spacer(),

      divider(),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 120, after: 60 },
        children: [new TextRun({ text: "Health Audio Studio — Product Plan — May 2026", size: 18, font: "Arial", color: "999999" })]
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("C:\\AI\\projects\\Podcast\\Health_Audio_Studio_Product_Plan.docx", buffer);
  console.log("Done: Health_Audio_Studio_Product_Plan.docx");
});
