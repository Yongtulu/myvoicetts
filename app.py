import os
import time
import chardet
import streamlit as st
from docx import Document
from tts_engine import TTSEngine

# ── Page config ───────────────────────────────────────────
st.set_page_config(page_title="My Voice TTS", page_icon="🎙️", layout="wide")
st.title("🎙️ My Voice TTS")

os.makedirs("outputs", exist_ok=True)
os.makedirs("reference", exist_ok=True)


# ── Utility functions ─────────────────────────────────────
def read_txt(file) -> str:
    raw = file.read()
    encoding = chardet.detect(raw)["encoding"] or "utf-8"
    return raw.decode(encoding)


def read_docx(file) -> str:
    doc = Document(file)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


@st.cache_resource
def load_engine():
    with st.spinner("Loading F5-TTS model... This may take a moment on first run."):
        return TTSEngine()


# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.header("Reference Voice")

    uploaded_ref = st.file_uploader(
        "Upload your reference audio (WAV)",
        type=["wav"],
        help="Recommended: 10–30 seconds, recorded in a quiet environment",
    )

    ref_audio_path = "reference/my_voice.wav"
    if uploaded_ref:
        with open(ref_audio_path, "wb") as f:
            f.write(uploaded_ref.read())
        st.success("Reference audio uploaded")
        st.audio(ref_audio_path, format="audio/wav")
    elif os.path.exists(ref_audio_path):
        st.info("Using existing reference audio")
        st.audio(ref_audio_path, format="audio/wav")
    else:
        st.warning("Please upload a reference audio file")

    ref_text = st.text_area(
        "Reference audio transcript",
        placeholder="Type what you said in the reference audio — improves voice matching quality",
        height=100,
    )

    st.divider()
    st.header("Settings")
    speed = st.slider("Speech speed", min_value=0.6, max_value=1.5, value=1.0, step=0.05)


# ── Main area: text input ─────────────────────────────────
st.subheader("Text Input")
tab_manual, tab_upload = st.tabs(["✏️ Type Text", "📄 Upload File (TXT / DOCX)"])

final_text = ""

with tab_manual:
    manual_text = st.text_area(
        "Enter text to read aloud",
        placeholder="Paste or type your content here...",
        height=250,
        label_visibility="collapsed",
    )
    final_text = manual_text

with tab_upload:
    uploaded_doc = st.file_uploader(
        "Upload a TXT or Word document",
        type=["txt", "docx"],
        help="Supports .txt (auto-detects encoding) and .docx formats",
    )
    if uploaded_doc:
        if uploaded_doc.name.endswith(".txt"):
            parsed = read_txt(uploaded_doc)
        else:
            parsed = read_docx(uploaded_doc)

        edited = st.text_area(
            "Parsed content (editable)",
            value=parsed,
            height=250,
        )
        final_text = edited


# ── Generate button ───────────────────────────────────────
st.divider()
ref_ready = os.path.exists(ref_audio_path)
text_ready = bool(final_text.strip())

generate_btn = st.button(
    "🔊 Generate Audio",
    type="primary",
    disabled=not (ref_ready and text_ready),
    use_container_width=True,
)

if not ref_ready:
    st.caption("Please upload a reference audio file in the sidebar first")
if not text_ready:
    st.caption("Please enter or upload the text you want to read aloud")


# ── Generation logic ──────────────────────────────────────
if generate_btn:
    engine = load_engine()
    output_path = f"outputs/output_{int(time.time())}.wav"

    with st.spinner("Synthesizing audio, please wait..."):
        try:
            engine.generate(
                text=final_text,
                ref_audio=ref_audio_path,
                ref_text=ref_text,
                output_path=output_path,
                speed=speed,
            )

            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.insert(
                0,
                {
                    "path": output_path,
                    "text": final_text[:60] + ("..." if len(final_text) > 60 else ""),
                    "time": time.strftime("%H:%M:%S"),
                },
            )

            st.success("Audio generated successfully!")
        except Exception as e:
            st.error(f"Generation failed: {e}")


# ── Latest result ─────────────────────────────────────────
if "history" in st.session_state and st.session_state.history:
    latest = st.session_state.history[0]
    st.subheader("Result")
    st.audio(latest["path"], format="audio/wav")
    with open(latest["path"], "rb") as f:
        st.download_button(
            "⬇️ Download Audio",
            f,
            file_name="output.wav",
            mime="audio/wav",
        )


# ── Session history ───────────────────────────────────────
if "history" in st.session_state and len(st.session_state.history) > 1:
    st.divider()
    with st.expander(f"📋 Session History ({len(st.session_state.history)} items)"):
        for item in st.session_state.history[1:]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"[{item['time']}] {item['text']}")
                st.audio(item["path"], format="audio/wav")
            with col2:
                with open(item["path"], "rb") as f:
                    st.download_button(
                        "⬇️ Download",
                        f,
                        file_name=os.path.basename(item["path"]),
                        mime="audio/wav",
                        key=item["path"],
                    )
