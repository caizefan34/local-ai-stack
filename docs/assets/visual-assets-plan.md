# Visual Assets Plan

> Project: local-ai-stack / Repository: caizefan34/local-ai-stack
> Purpose: Define specifications for all visual assets for README, GitHub Pages, and social sharing.

---

## 1. Hero Screenshot -- `hero-screenshot.png`

### Purpose
Primary README hero image showing the FastGPT UI in action. Communicates `this is what you get` at a glance.

### Composition
- **Main area:** FastGPT chat with Q&A conversation showing retrieved answer with citations
- **Side panel:** Knowledge base panel visible with imported documents (PDFs, notes) and vector search results
- **Status bar** (optional): Service health indicators (Ollama online, Reranker online)

### Technical Specs
| Property | Value |
|----------|-------|
| Resolution | 1280 x 800 px |
| Format | PNG (lossless) |
| Color space | sRGB |
| Max file size | < 2 MB |

### Style Guide
- **Background:** Dark theme (FastGPT default dark mode or custom indigo #1e1b4b)
- **Accent color:** Indigo #6366f1 (matches README badge color)
- **Typography:** System UI font for screenshots
- **Annotations:** Minimal -- subtle arrow or highlight boxes for key features
- **Border radius:** 12 px rounded corners

### Suggested Tools
| Tool | Pros | Cons |
|------|------|------|
| **ShareX** (Windows) | Free, region capture, annotation | Overkill for one screenshot |
| **Flameshot** (Linux/Win) | Free, inline annotation | Fewer export options |
| **Browser DevTools** | Free, built-in, exact viewport | No annotation |

### Workflow
1. Start all services: `docker compose --env-file .env -f docker/docker-compose.yml up -d`
2. Open http://localhost:3000
3. Import a test document (e.g., a sample PDF from tests/ or a paper abstract)
4. Ask a question about the document to generate a Q&A response with citations
5. Capture the viewport at 1280x800 using browser DevTools or ShareX
6. Add subtle annotations if needed
7. Export as PNG to `docs/assets/hero-screenshot.png`

---

## 2. Architecture Diagram -- `architecture-diagram.png`

### Purpose
Modern bento-style architecture visualization showing component connections.

### Components to Include

| Component | Role | Color |
|-----------|------|-------|
| **User / Client** | Browser accessing FastGPT UI | User icon |
| **Ollama** | LLM inference (Qwen3 models) | Purple #a855f7 |
| **FastGPT** | RAG platform, visual workflow engine | Blue #3b82f6 |
| **BGE Reranker** | Reranking service (FastAPI) | Teal #14b8a6 |
| **PostgreSQL / pgvector** | Vector database + metadata store | Orange #f97316 |
| **Knowledge Base** | Document import & sync pipeline | Green #22c55e |
| **Dashboard** | Desktop monitor + controls | Slate #64748b |

### Layout (Bento Grid)

```
+----------------------------------------------------------+
|                     User (Browser)                        |
+--------------+---------------------------+----------------+
|              |                           |                |
|   Ollama     |       FastGPT             |  BGE Reranker  |
|   (Qwen3)    |   (RAG Workflows)        |  (Re-rank)     |
|              |                           |                |
+--------------+---------------------------+----------------+
|                     PostgreSQL / pgvector                  |
+----------------------------+-------------------------------+
|    Knowledge Base          |       Desktop Dashboard       |
|    (Sync Pipeline)         |       (Service Monitor)       |
+----------------------------+-------------------------------+
```

Arrows/connectors:
- User -> FastGPT (HTTP)
- FastGPT -> Ollama (Ollama API, port 11434)
- FastGPT -> BGE Reranker (HTTP, port 18888)
- FastGPT -> PostgreSQL (pgvector, port 5432)
- Knowledge Base -> PostgreSQL (document chunk ingestion)
- Dashboard -> all services (health check API calls)

### Technical Specs
| Property | Value |
|----------|-------|
| Resolution | 1920 x 1080 px |
| Format | PNG (lossless) |
| Color space | sRGB |
| Max file size | < 3 MB |
| Border radius | 16 px on each cell |
| Font | Inter or system sans-serif, 14-18 px |

### Style
- **Background:** Dark slate (#0f172a) or white (#ffffff)
- **Bento cells:** Semi-transparent glassmorphism (backdrop-blur, subtle border)
- **Gradients:** Each cell uses a subtle gradient of its base color
- **Connection lines:** 2 px stroke, dashed for async, solid for request/response
- **Icons:** Simple icon in each cell header

### Suggested Tools
| Tool | Pros | Cons |
|------|------|------|
| **Excalidraw** | Free, hand-drawn style, PNG/SVG export | Less modern look |
| **Figma** | Professional, exact pixel control | Requires account |
| **Draw.io** | Free, desktop app, structured shapes | Limited gradient options |
| **Mermaid** | Version-control friendly | Limited bento aesthetics |

### Recommended Approach
Use Excalidraw for clean bento layout + gradient exports, or Figma for maximum polish.
Keep the source file in docs/assets/ alongside the PNG export.

---

## 3. Demo GIF -- `demo.gif`

### Purpose
Show the complete user journey from importing a document to getting an AI answer with citations. Used in README to demonstrate core workflow in under 15 seconds.

### Storyboard (4 Scenes)

#### Scene 1: Import Document (2-3 sec)
- User navigates to Knowledge Base panel in FastGPT
- Clicks Import button
- Selects a PDF file (e.g., a research paper abstract)
- File uploads and appears in the document list
**Overlay text:** `:page_facing_up: Import a PDF`

#### Scene 2: Auto-Sync Pipeline (2-3 sec)
- Document processing indicator (spinner / progress bar)
- Chunking, embedding, and vector insertion complete
- Document status changes to Ready

**Overlay text:** `:zap: Auto-sync pipeline processes it`

#### Scene 3: Ask a Question (3-4 sec)
- User switches to FastGPT chat interface
- Types a question about the imported document
- Loading indicator as the system retrieves

**Overlay text:** `:question: Ask a question`

#### Scene 4: Retrieved Answer (4-5 sec)
- FastGPT responds with a detailed answer
- Citations highlighted (source document, page number)
- Reranker confidence score visible

**Overlay text:** `:white_check_mark: Answer with citations`

### Technical Specs
| Property | Value |
|----------|-------|
| Duration | 10-15 seconds (total) |
| Resolution | 1280 x 720 px (720p) |
| Format | GIF (or WebP/MP4 as fallback) |
| Frame rate | 10-15 FPS |
| File size target | < 10 MB (GIF), < 5 MB (WebP/MP4) |

### Optimization Notes
- **GIF is preferred for universal README compatibility** (renders natively on GitHub without autoplay restrictions)
- If file size exceeds 10 MB, consider:
  - Using **WebP** format (smaller, supported by modern browsers)
  - Using **video (MP4)** with loop + muted + autoplay attributes
  - Reducing frame rate to 10 FPS
  - Cropping to only the relevant UI region

### Suggested Tools
| Tool | Pros | Cons |
|------|------|------|
| **ScreenToGif** (Windows) | Free, lightweight, built-in editor | Windows only |
| **OBS Studio + FFmpeg** | Free, high-quality, any platform | Post-processing needed |
| **Peek** (Linux) | Free, simple, direct GIF output | Linux only |
| **CleanShot X** (macOS) | Polished, annotations, GIF export | Paid |

### Workflow
1. Prepare test content: a PDF and a pre-written question with known answer
2. Record using ScreenToGif or OBS at 1280x720, 15 FPS
3. Trim to 10-15 seconds covering the 4 scenes
4. Add overlay text using ScreenToGif's built-in editor
5. Optimize palette (reduce colors to ~128-256 for smaller size)
6. Export as GIF and place in `docs/assets/demo.gif`
7. Verify rendering in Markdown preview or GitHub PR preview

---

## File Placement Summary

```
docs/
+-- assets/
|   +-- hero-screenshot.png      # README hero image
|   +-- architecture-diagram.png # Architecture diagram (bento grid)
|   +-- architecture.excalidraw  # Source file (recommended)
|   +-- demo.gif                 # Workflow demo GIF
+-- visual-assets-plan.md        # This file
```

---

## Usage in README

```markdown
<!-- Hero screenshot -- placed below tagline -->
<p align="center">
  <img src="docs/assets/hero-screenshot.png" alt="Local AI Stack UI" width="80%">
</p>

<!-- Architecture diagram -- in Features or Tech Stack section -->
<p align="center">
  <img src="docs/assets/architecture-diagram.png" alt="Architecture Diagram" width="100%">
</p>

<!-- Demo GIF -- in Demo section -->
<p align="center">
  <img src="docs/assets/demo.gif" alt="Demo" width="80%">
</p>
```
