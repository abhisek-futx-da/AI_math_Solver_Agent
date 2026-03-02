# Evaluation Summary

## 1. RAG Pipeline

- **Knowledge base**: Curated set of 7 documents in `knowledge_base/` covering algebra, probability, calculus, linear algebra, solution templates, common mistakes, and domain constraints (JEE-style scope).
- **Chunking & embedding**: Text is chunked with overlap; embeddings via sentence-transformers (all-MiniLM-L6-v2). No API key required for embeddings.
- **Vector store**: ChromaDB; persistent index in `chroma_data/`.
- **Retrieval**: Top-k chunks retrieved for the Solver; shown in the UI as “Retrieved context (RAG)” with source filenames.
- **No hallucinated citations**: If retrieval fails or returns empty, the Solver still runs with “No retrieved context” and does not invent sources.

## 2. Multi-Agent System (5 agents)

| Agent | Role |
|-------|------|
| **Parser Agent** | Cleans OCR/ASR output; produces structured problem (problem_text, topic, variables, constraints, needs_clarification). Triggers HITL when ambiguous. |
| **Intent Router Agent** | Classifies problem type (algebra, probability, calculus, linear_algebra) and routes workflow. |
| **Solver Agent** | Solves using RAG context + OpenRouter LLM; optional tools (RAG only in this implementation). |
| **Verifier / Critic Agent** | Checks correctness, units/domain, edge cases; outputs is_correct, confidence, issues, suggest_recheck. Triggers HITL when unsure. |
| **Explainer / Tutor Agent** | Produces step-by-step, student-friendly explanation. |

## 3. Human-in-the-Loop (HITL)

- **When HITL triggers**: (1) OCR or ASR confidence below threshold (user can edit extracted text), (2) Parser sets `needs_clarification`, (3) Verifier sets `suggest_recheck`, (4) user can always edit input before solving.
- **Flow**: User can approve, edit, or reject; approved corrections are stored as part of memory (feedback).

## 4. Memory & Self-Learning

- **Stored per interaction**: Raw input, parsed question, retrieved context references, solution preview, verifier outcome, user feedback (correct / incorrect + comment).
- **Runtime use**: Similar past problems retrieved by embedding similarity and shown in “Similar past problems (Memory)” for pattern reuse. No model retraining; pattern reuse only.

## 5. Multimodal Input

- **Image**: JPG/PNG upload; EasyOCR for extraction; confidence shown; user can edit; calculus-specific and algebra post-processing for common OCR errors.
- **Audio**: WAV/MP3 upload; Whisper for ASR; transcript shown for confirmation; math-phrase normalization.
- **Text**: Direct input with no extra processing.

## 6. Application UI (Streamlit)

- Input mode selector (Text / Image / Audio), extraction preview (OCR or transcript), agent trace, retrieved context panel, final answer + explanation, verifier confidence, feedback buttons (correct / incorrect + comment). Scope limited to algebra, probability, basic calculus, linear algebra (JEE-style).

## 7. Deployment

- App can be deployed to Streamlit Community Cloud, Hugging Face Spaces, Render, or Railway. README includes deployment steps and `.env.example` for `OPENROUTER_API_KEY`. No DevOps depth required; reviewer can open a link and test.
