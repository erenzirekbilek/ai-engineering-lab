# 1. Hafta - LLM ve API Temelleri

## Kavramlar

| Kavram | Kisa tanim | Pratikte neye etki eder |
|---|---|---|
| **LLM** | Bir sonraki token'i tahmin etmek icin egitilmis model | Deterministik degil; ayni girdi farkli cikti verebilir |
| **Inference** | Egitilmis modeli calistirip cikti uretme | Her istek para ve zaman harcar |
| **Token** | Metnin model icin parcalanmis hali (~4 karakter) | Faturalandirma birimi: input + output ayri fiyatlanir |
| **Context window** | Input + output icin toplam token siniri | Asilirsa istek hata verir; uzun sohbette kirpmak gerekir |
| **Temperature** | Ornekleme rastgeleligi (0 - 2) | Dusuk = tutarli/tekrarlanabilir, yuksek = yaratici/degisken |

## API tarafi

- **HTTP**: Istek `POST https://api.openai.com/v1/chat/completions` adresine gider.
- **JSON**: Govde `{"model": ..., "messages": [...], "temperature": ...}` seklinde.
- **API key**: `Authorization: Bearer sk-...` basliginda gider. Koda yazilmaz, `.env`'de durur.
- **SDK**: `openai` paketi bu HTTP cagrisini, retry ve hata tiplerini sarmalar.

## Bu haftanin deney notlari

> Asagisini kendin doldur.

- [ ] Ayni promptu temperature 0 ve 1.5 ile calistir - fark ne?
- [ ] Max tokens'i 64'e dusur - yanit nerede kesiliyor?
- [ ] Gecersiz bir model adi gir - hangi hata tipi geliyor?
- [ ] `logs/usage.jsonl` dosyasina bak - 10 istegin toplam maliyeti ne?

## Cikti

- `uv run python -m lessons.week01_first_request` → terminalden ilk istek
- `uv run streamlit run app.py` → temel AI Chat ekrani
