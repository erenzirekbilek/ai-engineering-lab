# 🧪 AI Engineering Lab

`uv` tabanli, 6 haftalik uygulamali AI Engineering ogrenme workspace'i.
Kaynak plan: [roadmap.sh/ai-engineer](https://roadmap.sh/ai-engineer)

Her hafta calisan bir cikti birakir; kod onceki haftanin uzerine eklenir.

---

## Kurulum

```bash
git clone https://github.com/erenzirekbilek/ai-engineering-lab.git
cd ai-engineering-lab

cp .env.example .env        # OPENAI_API_KEY'ini yaz
uv sync                     # bagimliliklari temiz ortamda kur
```

> `.env` `.gitignore` icinde. Repo **public** - API anahtarini asla commit etme.

## Calistirma

```bash
uv run streamlit run app.py                      # AI Chat ekrani -> localhost:8501
uv run python -m lessons.week01_first_request    # terminalden ilk model istegi
uv run pytest                                    # testler (API cagrisi yapmaz)
uv run python --version                          # 3.12.x olmali
```

## Yapi

```
app.py                 Streamlit arayuzu (haftalar ilerledikce buyur)
lessons/               Hafta hafta calisma dosyalari ve notlar
tools/                 Paylasilan moduller
  config.py            .env -> Settings
  llm.py               OpenAI sarmalayicisi (gecikme + token + hata yonetimi)
  costs.py             Token -> tahmini USD maliyet
  pricing.json         Fiyat tablosu (degisince elle guncelle)
  logging_utils.py     logs/usage.jsonl yazici
knowledge/             4. hafta RAG belgeleri buraya
tests/                 pytest
logs/                  usage.jsonl (git'e girmez)
```

## Maliyet ve log takibi

Her API cagrisi `logs/usage.jsonl` dosyasina tek satir JSON olarak yazilir:
model, token sayilari, gecikme ve tahmini maliyet. Hatalar da `chat.error`
olarak loglanir. 6. haftadaki olcum adimi bu dosyayi okuyacak.

Fiyatlar `tools/pricing.json` icinde ve **elle guncellenir**. Tabloda olmayan
bir model icin maliyet `None` doner - yanlis rakam gostermek yerine
"fiyat bilinmiyor" denir. Guncel fiyat: [platform.openai.com/docs/pricing](https://platform.openai.com/docs/pricing)

---

## 6 haftalik plan

### Hazirlik - Workspace ✅
- [x] `uv init` + `uv python pin 3.12`
- [x] `uv add openai streamlit python-dotenv`
- [x] `pyproject.toml` + `uv.lock` git'te, `.venv` ve `.env` disarida
- [x] `.env.example`, `lessons/`, `tools/`, `knowledge/`, `tests/`, `logs/`
- [x] `uv run python --version` ve `uv run streamlit run app.py` dogrulandi

### 1. Hafta - LLM ve API Temelleri ✅
- [x] LLM, inference, token, context window, temperature → `lessons/week01_notes.md`
- [x] HTTP, JSON, API key, SDK akisi → `tools/llm.py`
- [x] Terminalden ilk istek + usage verisi → `lessons/week01_first_request.py`
- [x] Tek mesajlik Streamlit sohbet ekrani → `app.py`
- [x] Hata ve tahmini token maliyeti kaydi → `logs/usage.jsonl`
- [ ] `lessons/week01_notes.md` icindeki deney notlarini doldur

**Cikti:** uv ile calisan temel AI Chat ekrani.

### 2. Hafta - Prompt ve Context Engineering
- [ ] System/user mesajlariyla farkli promptlar
- [ ] Zero-shot ve few-shot karsilastirmasi
- [ ] JSON yapilandirilmis cikti + dogrulama
- [ ] Sohbet gecmisi ve uzun baglam testi
- [ ] Streaming yanit

**Cikti:** Prompt Playground ve sohbet gecmisi.

### 3. Hafta - Function Calling ve Tools
- [ ] Tool schema yapisi
- [ ] Hesap makinesi fonksiyonu
- [ ] Ikinci arac: ornek veri arama
- [ ] Model arac secimi, parametre uretimi, sonucu kullanma
- [ ] Hatali parametre, arac hatasi, kullanici onayi senaryolari

**Cikti:** Iki araci calistirabilen AI asistani.

### 4. Hafta - Embeddings, Vector DB ve RAG
- [ ] Embedding, semantic search, chunking
- [ ] `uv add chromadb`
- [ ] `knowledge/` altindaki belgeleri parcala ve indeksle
- [ ] Kaynakli yanit uretimi
- [ ] Belgede olmayan bilgi testleri

**Cikti:** Kaynak gosteren belge soru-cevap modulu.

### 5. Hafta - AI Agents, MCP ve Otomasyon
- [ ] Agent vs chatbot farki
- [ ] Cok araçli adim adim is akisi
- [ ] MCP server/client denemesi
- [ ] Arac cagri siniri, retry, hata yonetimi
- [ ] n8n webhook tetikleyici

**Cikti:** Arac kullanan ve n8n ile calisan mini agent.

### 6. Hafta - Evaluation, Guvenlik ve Yayinlama
- [ ] 20+ ornekli test veri seti
- [ ] Yanit dogrulugu, arac secimi, kaynak kullanimi degerlendirmesi
- [ ] Prompt injection ve hatali arac cagrisi testleri
- [ ] Loglama, gecikme, maliyet olcumu
- [ ] `uv add fastapi uvicorn` + basit endpoint
- [ ] `uv sync` ile temiz kurulum testi + yayin

**Cikti:** Test edilmis, belgelenmis ve erisilebilir AI Engineering Lab.

---

## Tamamlama kontrol listesi

- [x] Workspace uv ile kuruluyor; `uv.lock` ve `pyproject.toml` repoda
- [x] Chat ekrani calisiyor ve model API cagrisi yapiyor
- [ ] Prompt Playground farkli promptlari karsilastiriyor
- [ ] Function Calling en az iki araci guvenli calistiriyor
- [ ] RAG modulu kaynakli yanit uretiyor
- [ ] Mini agent n8n tetikleyicisini yonetiyor
- [ ] Testler, loglar, maliyet takibi ve README tamamlandi
