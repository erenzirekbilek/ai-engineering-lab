"""1. Hafta ciktisi: uv ile calisan temel AI Chat ekrani.

Calistir:  uv run streamlit run app.py

Bu ekran bilerek "tek mesajlik": her gonderim bagimsiz bir API istegi.
Sohbet gecmisi ve streaming 2. haftada ekleniyor.
"""

from __future__ import annotations

import streamlit as st

from tools.config import load_settings
from tools.costs import format_cost, known_models
from tools.llm import LabError, chat

st.set_page_config(page_title="AI Engineering Lab", page_icon="🧪", layout="centered")

settings = load_settings()

st.title("🧪 AI Engineering Lab")
st.caption("1. Hafta - LLM ve API temelleri | tek mesajlik sohbet")

with st.sidebar:
    st.subheader("Ayarlar")

    models = known_models()
    default_index = models.index(settings.model) if settings.model in models else 0
    model = st.selectbox("Model", models, index=default_index)

    temperature = st.slider(
        "Temperature", 0.0, 2.0, settings.temperature, 0.1,
        help="Dusuk = tutarli ve tekrarlanabilir, yuksek = yaratici ve degisken.",
    )
    max_tokens = st.number_input(
        "Max output tokens", 64, 4096, settings.max_tokens, 64,
        help="Yanitin uzunluk ustu siniri. Maliyeti dogrudan etkiler.",
    )
    system_prompt = st.text_area(
        "System prompt",
        value="Sen yardimci bir asistansin. Kisa ve net cevap ver.",
        height=100,
    )

    st.divider()
    if settings.is_ready:
        st.success("OPENAI_API_KEY yuklendi")
    else:
        st.error("OPENAI_API_KEY yok - `.env` dosyasini olustur")

prompt = st.text_area("Mesajin", height=140, placeholder="Bir sey sor...")
send = st.button("Gonder", type="primary", disabled=not prompt.strip())

if send:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    try:
        with st.spinner("Model dusunuyor..."):
            result = chat(
                messages,
                model=model,
                temperature=temperature,
                max_tokens=int(max_tokens),
            )
    except LabError as exc:
        st.error(str(exc))
        st.info("Ayrinti icin: logs/usage.jsonl")
    else:
        st.markdown("### Yanit")
        st.write(result.text)

        st.divider()
        st.markdown("### Kullanim")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Input token", result.input_tokens)
        c2.metric("Output token", result.output_tokens)
        c3.metric("Toplam", result.total_tokens)
        c4.metric("Gecikme", f"{result.latency_ms} ms")
        st.caption(f"Tahmini maliyet: {format_cost(result.cost_usd)} | model: {result.model}")
