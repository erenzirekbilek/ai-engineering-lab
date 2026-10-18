"""1. Hafta ciktisi: uv ile calisan temel AI Chat ekrani (Google Gemini).

Calistir:  uv run streamlit run app.py

Bu ekran bilerek "tek mesajlik": her gonderim bagimsiz bir API istegi.
Sohbet gecmisi ve streaming 2. haftada ekleniyor.
"""

from __future__ import annotations

import streamlit as st

from tools.config import load_settings
from tools.costs import format_cost, known_models, model_info, on_free_tier, supports_temperature
from tools.llm import LabError, chat

st.set_page_config(page_title="AI Engineering Lab", page_icon="🧪", layout="centered")

settings = load_settings()

st.title("🧪 AI Engineering Lab")
st.caption("1. Hafta - LLM ve API temelleri | Google Gemini | tek mesajlik sohbet")

with st.sidebar:
    st.subheader("Ayarlar")

    models = known_models()
    default_index = models.index(settings.model) if settings.model in models else 0
    model = st.selectbox("Model", models, index=default_index)

    info = model_info(model) or {}
    if info.get("note"):
        st.caption(info["note"])
    if not on_free_tier(model):
        st.warning("Bu model ucretsiz kademede yok - cagri 403 donebilir.")

    if supports_temperature(model):
        temperature = st.slider(
            "Temperature", 0.0, 2.0, settings.temperature, 0.1,
            help="Dusuk = tutarli ve tekrarlanabilir, yuksek = yaratici ve degisken.",
        )
    else:
        temperature = None
        st.info("Bu model temperature'i yok sayiyor, bu yuzden gonderilmiyor.")

    max_output_tokens = st.number_input(
        "Max output tokens", 64, 8192, settings.max_output_tokens, 64,
        help="Yanitin uzunluk ustu siniri. Maliyeti dogrudan etkiler.",
    )
    system_instruction = st.text_area(
        "System instruction",
        value="Sen yardimci bir asistansin. Kisa ve net cevap ver.",
        height=100,
    )

    st.divider()
    if settings.is_ready:
        st.success("GEMINI_API_KEY yuklendi")
    else:
        st.error("GEMINI_API_KEY yok - `.env` dosyasini olustur")

prompt = st.text_area("Mesajin", height=140, placeholder="Bir sey sor...")
send = st.button("Gonder", type="primary", disabled=not prompt.strip())

if send:
    try:
        with st.spinner("Model dusunuyor..."):
            result = chat(
                prompt,
                model=model,
                system_instruction=system_instruction,
                temperature=temperature,
                max_output_tokens=int(max_output_tokens),
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
        c3.metric("Dusunme", result.thought_tokens)
        c4.metric("Gecikme", f"{result.latency_ms} ms")

        tier = "ucretsiz kademede $0" if on_free_tier(model) else "ucretli"
        st.caption(
            f"Toplam {result.total_tokens} token | "
            f"ucretli kademe karsiligi: {format_cost(result.cost_usd)} ({tier}) | "
            f"model: {result.model}"
        )
