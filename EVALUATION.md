# Evaluation Summary

## 1. RAG Pipeline

- **Knowledge base**: Curated set of 12 documents in `knowledge_base/` covering algebra, probability, calculus, linear algebra, trigonometry, integration, sequences/series, coordinate geometry, JEE strategies, solution templates, common mistakes, and domain constraints (JEE-style scope).
- **Chunking & embedding**: Text is chunked with overlap; embeddings via sentence-transformers (all-MiniLM-L6-v2). No API key required for embeddings.
- **Vector store**: ChromaDB; persistent index in `chroma_data/`.
- **Retrieval**: Top-k chunks retrieved for the Solver; shown in the UI as "Retrieved context (RAG)" with source filenames.
- **No hallucinated citations**: If retrieval fails or returns empty, the Solver still runs with "No retrieved context" and does not invent sources.

## 2. Multi-Agent System (6 agents — 5 mandatory + 1 bonus)

| Agent | Role |
|-------|------|
| **Guardrail Agent** *(bonus)* | Filters non-math or harmful inputs before processing; returns reason if blocked. |
| **Parser Agent** | Cleans OCR/ASR output; produces structured problem (problem_text, topic, variables, constraints, needs_clarification). Triggers HITL when ambiguous. |
| **Intent Router Agent** | Classifies problem type (algebra, probability, calculus, linear_algebra) and routes workflow. |
| **Solver Agent** | Solves using RAG context + OpenRouter LLM; optional tools (RAG only in this implementation). |
| **Verifier / Critic Agent** | Checks correctness, units/domain, edge cases; outputs is_correct, confidence, issues, suggest_recheck. Triggers HITL when unsure. |
| **Explainer / Tutor Agent** | Produces step-by-step, student-friendly explanation. |

## 3. Human-in-the-Loop (HITL)

All 4 HITL triggers implemented:
1. **OCR / ASR confidence is low** — warning shown; user can edit extracted text before solving.
2. **Parser detects ambiguity** (`needs_clarification=true`) — pipeline pauses; user must clarify.
3. **Verifier is not confident** (`suggest_recheck=true`) — HITL flag shown; sidebar note.
4. **User explicitly requests re-check** — "🔁 Request Human Re-check (HITL)" button in UI; flags the solution and stores it for review.

HITL flow: User can approve, edit, or reject; approved corrections are stored as part of memory (feedback).

## 4. Memory & Self-Learning

- **Stored per interaction**: Raw input, parsed question, retrieved context references, solution preview, verifier outcome, user feedback (correct / incorrect + comment / recheck_requested).
- **Runtime use**: Similar past problems retrieved by embedding similarity and shown in "Similar past problems (Memory)" for pattern reuse. No model retraining; pattern reuse only.

## 5. Multimodal Input

- **Image**: JPG/PNG upload; EasyOCR for extraction; confidence shown; user can edit; calculus-specific and algebra post-processing for common OCR errors.
- **Audio**: WAV/MP3 upload; Whisper for ASR; transcript shown for confirmation; math-phrase normalization.
- **Text**: Direct input with no extra processing.

## 6. Application UI (Streamlit)

- Input mode selector (Text / Image / Audio)
- Extraction preview (OCR or transcript), editable
- Agent trace (every agent logged: Guardrail → Parser → Router → Solver → Verifier → Explainer)
- Retrieved context panel (RAG chunks with source filenames)
- Final answer + step-by-step explanation
- Verifier confidence metric
- Feedback buttons: ✅ Correct / ❌ Incorrect + comment
- 🔁 Request Human Re-check (HITL) button

## 7. Deployment

- App is deployable to Streamlit Community Cloud, Hugging Face Spaces, Render, or Railway.
- `Dockerfile`, `render.yaml`, `packages.txt`, and `.env.example` are all present.
- README includes step-by-step deployment instructions.
- No DevOps depth required; reviewer can open a link and test.
