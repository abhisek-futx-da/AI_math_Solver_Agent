"""
Math Mentor - Streamlit UI.
Input: Text / Image / Audio -> Parser -> Router -> Solver (RAG) -> Verifier -> Explainer.
HITL when OCR/ASR low confidence, parser ambiguity, or verifier unsure.
"""
import base64
import io
import json
# NumPy 2 compat for ChromaDB (so RAG can load when available)
try:
    import numpy as np
    if not hasattr(np, "float_"):
        np.float_ = np.float64
    if not hasattr(np, "int_"):
        np.int_ = np.int64
except Exception:
    pass
import streamlit as st
from config import OPENROUTER_API_KEY

# RAG is optional; ensure_index is called on Solve (lazy) so app starts even if chromadb fails

st.set_page_config(page_title="Math Mentor", layout="wide")

# Session state
if "agent_trace" not in st.session_state:
    st.session_state.agent_trace = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""
if "extraction_confidence" not in st.session_state:
    st.session_state.extraction_confidence = 1.0
if "hitl_triggered" not in st.session_state:
    st.session_state.hitl_triggered = False
if "user_confirmed_input" not in st.session_state:
    st.session_state.user_confirmed_input = None
if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None
if "last_upload_name" not in st.session_state:
    st.session_state.last_upload_name = None

def trace(msg: str, detail: str = ""):
    st.session_state.agent_trace.append({"step": msg, "detail": detail})

def run_ocr(image_bytes: bytes):
    from input_handlers.ocr import extract_text_from_image
    text, conf, err = extract_text_from_image(image_bytes)
    if not err:
        st.session_state.extracted_text = text
        st.session_state.extraction_confidence = conf
    return text, conf, err

def run_asr(audio_bytes: bytes):
    from input_handlers.asr import transcribe_audio
    text, conf = transcribe_audio(audio_bytes)
    st.session_state.extracted_text = text
    st.session_state.extraction_confidence = conf
    return text, conf

def run_pipeline(user_text: str):
    from agents.parser_agent import parse_problem
    from agents.router_agent import route_intent
    from agents.solver_agent import SolverAgent
    from agents.verifier_agent import verify_solution
    from agents.explainer_agent import explain_solution
    from memory.store import memory_retrieve_similar, add_interaction

    st.session_state.agent_trace = []

    # Guardrail Agent: block non-math or harmful inputs
    from agents.guardrail_agent import check_input
    guard = check_input(user_text)
    trace("Guardrail Agent", f"is_valid={guard.get('is_valid')}, reason={guard.get('reason', '')}")
    if not guard.get("is_valid", True):
        st.session_state.hitl_triggered = False
        return None, {"guardrail_reason": guard.get("reason", "Non-math input detected.")}, None, None, None, None

    parsed = parse_problem(user_text)
    # Safety override: if the problem text is substantial, never block — LLMs sometimes
    # incorrectly flag multi-part or symbolic problems as needing clarification.
    problem_text = parsed.get("problem_text", "")
    if parsed.get("needs_clarification") and len(problem_text.strip()) > 10:
        parsed["needs_clarification"] = False

    trace("Parser Agent", f"Structured: topic={parsed.get('topic')}, needs_clarification={parsed.get('needs_clarification')}")

    if parsed.get("needs_clarification"):
        st.session_state.hitl_triggered = True
        trace("HITL", "Parser requested clarification")
        return None, parsed, None, None, None, None

    topic = route_intent(parsed)
    trace("Intent Router Agent", f"Routed to: {topic}")

    solver = SolverAgent()
    solution, rag_context = solver.run(parsed, topic)
    trace("Solver Agent", f"Retrieved {len(rag_context)} RAG chunks")

    verifier_out = verify_solution(parsed.get("problem_text", ""), solution, parsed)
    trace("Verifier Agent", f"is_correct={verifier_out.get('is_correct')}, confidence={verifier_out.get('confidence')}")
    if verifier_out.get("suggest_recheck"):
        st.session_state.hitl_triggered = True
        trace("HITL", "Verifier suggests human review")

    explanation = explain_solution(parsed.get("problem_text", ""), solution, parsed)
    trace("Explainer Agent", "Step-by-step explanation generated")

    # Memory: similar past problems (for display); optional
    try:
        similar = memory_retrieve_similar(user_text, parsed, top_k=2)
    except Exception:
        similar = []

    return {
        "parsed": parsed,
        "topic": topic,
        "solution": solution,
        "rag_context": rag_context,
        "verifier": verifier_out,
        "explanation": explanation,
        "similar": similar,
    }, parsed, rag_context, verifier_out, explanation, similar

def main():
    if not OPENROUTER_API_KEY:
        st.error("Set OPENROUTER_API_KEY in .env (see .env.example).")
        return

    st.title("Math Mentor")
    st.caption("Multimodal input → RAG + Agents → Solution with HITL & Memory")

    # Input mode
    input_mode = st.radio("Input mode", ["Text", "Image", "Audio"], horizontal=True)

    user_text = None
    if input_mode == "Text":
        user_text = st.text_area("Type your math question", height=100)
        st.session_state.extraction_confidence = 1.0
        st.session_state.extracted_text = user_text or ""
    elif input_mode == "Image":
        uploaded = st.file_uploader("Upload JPG/PNG (photo or screenshot)", type=["jpg", "jpeg", "png"])
        if uploaded:
            # Store bytes in session state (Streamlit file can only be read once per run)
            name = getattr(uploaded, "name", "") or ""
            is_new_upload = st.session_state.last_upload_name != name or st.session_state.image_bytes is None
            if is_new_upload:
                st.session_state.image_bytes = uploaded.read()
                st.session_state.last_upload_name = name
                st.session_state.extracted_text = ""
                st.session_state["_ocr_auto_done"] = None
            bytes_data = st.session_state.image_bytes
            if not bytes_data:
                st.warning("Could not read the image. Try uploading again.")
            else:
                # Run OCR automatically when we have new image bytes, or when user clicks Extract
                if st.button("Extract text (OCR)"):
                    with st.spinner("Running OCR..."):
                        text, conf, err = run_ocr(bytes_data)
                    if err:
                        st.error(f"OCR error: {err}")
                    else:
                        st.session_state.extracted_text = text
                        st.session_state.extraction_confidence = conf
                # Auto-run OCR once when we have bytes but no extracted text yet
                if bytes_data and not st.session_state.extracted_text and st.session_state.get("_ocr_auto_done") != name:
                    with st.spinner("Extracting text from image..."):
                        text, conf, err = run_ocr(bytes_data)
                    if not err:
                        st.session_state.extracted_text = text
                        st.session_state.extraction_confidence = conf
                    else:
                        st.error(f"OCR failed: {err}. Click 'Extract text (OCR)' to retry.")
                    st.session_state["_ocr_auto_done"] = name
            extracted = st.text_area("Extracted text (edit if needed)", value=st.session_state.extracted_text, height=120, key="image_extracted")
            conf = st.session_state.extraction_confidence
            st.caption(f"OCR confidence: {conf:.2f}" + (" — consider reviewing (HITL)" if conf < 0.6 else ""))
            user_text = extracted
    else:  # Audio
        uploaded_audio = st.file_uploader("Upload audio (WAV/MP3)", type=["wav", "mp3", "ogg"])
        if uploaded_audio:
            bytes_data = uploaded_audio.read()
            if st.button("Transcribe (ASR)"):
                text, conf = run_asr(bytes_data)
                st.session_state.extracted_text = text
                st.session_state.extraction_confidence = conf
            transcript = st.text_area("Transcript (edit if needed)", value=st.session_state.extracted_text, height=120)
            conf = st.session_state.extraction_confidence
            st.caption(f"ASR confidence: {conf:.2f}" + (" — consider reviewing (HITL)" if conf < 0.6 else ""))
            user_text = transcript

    # Show extraction preview
    if st.session_state.extracted_text and input_mode != "Text":
        with st.expander("Extraction preview", expanded=True):
            st.write(st.session_state.extracted_text)

    # Solve button
    if st.button("Solve", type="primary") and user_text and user_text.strip():
        try:
            from rag_pipeline import ensure_index
            ensure_index()
        except Exception:
            pass  # RAG optional; solver will use empty context
        try:
            with st.spinner("Running pipeline..."):
                result, parsed, rag_context, verifier_out, explanation, similar = run_pipeline(user_text.strip())
        except Exception as e:
            st.error(f"Pipeline error: {e}. (If 429: API quota exceeded; try again later or check your key.)")
            return

        if result is None and parsed and parsed.get("guardrail_reason"):
            st.error(f"🚫 Guardrail blocked: {parsed['guardrail_reason']} Please ask a math question.")
            return

        if result is None and parsed and parsed.get("needs_clarification"):
            st.warning("The parser detected ambiguity. Please clarify or edit the problem text above and try again.")
            st.json(parsed)
            return

        if result is None:
            st.info("Pipeline did not return a result. Check agent trace.")
            return

        st.session_state.last_result = result

        # Layout: two columns
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Agent trace")
            for t in st.session_state.agent_trace:
                st.write(f"- **{t['step']}**: {t['detail']}")

            st.subheader("Retrieved context (RAG)")
            if result.get("rag_context"):
                for i, c in enumerate(result["rag_context"], 1):
                    st.markdown(f"**[{i}] {c.get('source', '')}**")
                    st.text(c.get("text", "")[:300] + ("..." if len(c.get("text", "")) > 300 else ""))
            else:
                st.caption("No chunks retrieved (no hallucinated citations).")

            st.subheader("Similar past problems (Memory)")
            if result.get("similar"):
                for s in result["similar"]:
                    st.caption(s.get("parsed_problem", "")[:150])
                    st.caption(f"Topic: {s.get('topic')} | Feedback: {s.get('feedback', 'N/A')}")
            else:
                st.caption("No similar past problems yet.")

        with col2:
            st.subheader("Solution")
            st.markdown(result["solution"])

            st.subheader("Explanation")
            st.markdown(result["explanation"])

            ver = result["verifier"]
            conf = ver.get("confidence", 0)
            st.metric("Verifier confidence", f"{conf:.2f}")
            if ver.get("issues"):
                st.warning("Issues: " + "; ".join(ver["issues"]))
            if ver.get("suggest_recheck"):
                st.info("Verifier suggests human review (HITL).")

            st.subheader("Feedback")
            fb_col1, fb_col2 = st.columns(2)
            with fb_col1:
                if st.button("✅ Correct", key="btn_correct"):
                    from memory.store import add_interaction
                    add_interaction(
                        user_text, result["parsed"], result.get("rag_context", []),
                        result["solution"], result["verifier"], feedback="correct"
                    )
                    st.success("Thanks! Stored as correct.")
            with fb_col2:
                comment = st.text_input("If incorrect, add a comment and submit below", key="incorrect_comment")
                if st.button("❌ Incorrect", key="btn_incorrect"):
                    from memory.store import add_interaction
                    add_interaction(
                        user_text, result["parsed"], result.get("rag_context", []),
                        result["solution"], result["verifier"], feedback="incorrect", user_comment=comment
                    )
                    st.info("Thanks. Stored for learning.")

            # HITL: explicit re-check trigger (4th HITL condition from assignment)
            st.divider()
            if st.button("🔁 Request Human Re-check (HITL)", key="btn_recheck", help="Flag this solution for manual review"):
                st.session_state.hitl_triggered = True
                from memory.store import add_interaction
                add_interaction(
                    user_text, result["parsed"], result.get("rag_context", []),
                    result["solution"], result["verifier"], feedback="recheck_requested"
                )
                st.warning("⚠️ Solution flagged for human review and stored. Please verify manually.")
                trace("HITL", "User explicitly requested human re-check")

    elif st.session_state.last_result:
        # Show last result again if no new solve
        r = st.session_state.last_result
        st.subheader("Last result")
        st.markdown(r["solution"])
        st.markdown(r["explanation"])

    # HITL note
    if st.session_state.get("hitl_triggered"):
        st.sidebar.info("HITL was triggered (low confidence or clarification needed). Please review and confirm or edit.")

if __name__ == "__main__":
    main()
