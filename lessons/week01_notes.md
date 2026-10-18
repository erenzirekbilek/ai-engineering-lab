# 1. Hafta - LLM ve API Temelleri (Google Gemini)

## Kavramlar

| Kavram | Kisa tanim | Pratikte neye etki eder |
|---|---|---|
| **LLM** | Bir sonraki token'i tahmin etmek icin egitilmis model | Deterministik degil; ayni girdi farkli cikti verebilir |
| **Inference** | Egitilmis modeli calistirip cikti uretme | Her istek zaman harcar; ucretli kademede para da harcar |
| **Token** | Metnin model icin parcalanmis hali (~4 karakter) | Faturalandirma birimi: input ve output ayri fiyatlanir |
| **Context window** | Input + output icin toplam token siniri | Gemini 4 Argon'da 1M token; asilirsa istek hata verir |
| **Temperature** | Ornekleme rastgeleligi | **Dikkat:** Gemini 3.6+ ve 4 bunu yok sayiyor (asagiya bak) |
| **Thought token** | Modelin "dusunurken" urettigi gizli token'lar | Yanitta gorunmez ama cikti tarafinda faturalanir |

## API tarafi

- **HTTP**: Istek Gemini **Interactions API**'sine gider (`client.interactions.create`).
- **JSON**: Govde `{"model": ..., "input": ..., "system_instruction": ..., "generation_config": {...}}`.
- **API key**: `GEMINI_API_KEY` ortam degiskeninden okunur. Koda yazilmaz, `.env`'de durur.
- **SDK**: `google-genai` paketi bu HTTP cagrisini, hata tiplerini ve yeniden denemeyi sarmalar.

### Interactions API'nin eski `generate_content`'tan farki

Interactions API sohbet gecmisini **sunucuda tutabiliyor**. Her yanitin bir `id`'si
var; bir sonraki istekte `previous_interaction_id` olarak gonderince model onceki
turlari hatirliyor - tum gecmisi her seferinde yeniden gondermek gerekmiyor.
Stateless calismak istersen `store=False` verip `steps` listesini kendin tasiyorsun.

2. haftadaki "sohbet gecmisi" adiminda bu iki yaklasimi karsilastiracagiz.

### Temperature tuzagi

Google'in dokumanina gore **Gemini 4 ve 3.6+ modelleri `temperature`, `top_p` ve
`top_k` degerlerini yok sayar** ve deprecation uyarisi dondurur. Bu yuzden
`tools/llm.py` bu parametreyi sadece destekleyen modellerde gonderiyor
(`tools/pricing.json` icindeki `supports_temperature` alani).

Temperature deneyi yapmak istiyorsan **`gemini-3.5-flash-lite`** sec - o hala
dikkate aliyor.

## Ucretsiz kademe

AI Studio'da proje acmak yeterli; kart gerekmiyor. Flash ve Flash-Lite modelleri
ucretsiz kademede. **`gemini-4-argon` ucretsiz kademede yok** - secersen 403 gelir.

Ucretsiz kademede dakikalik (RPM) ve gunluk (RPD) istek siniri var ve bu limitler
hesaba gore degisiyor; kendi limitlerini buradan gor:
https://aistudio.google.com/rate-limit

> Ucretsiz kademede istek ve yanitlarin Google tarafindan urun gelistirmek icin
> kullanilabildigini unutma. Hassas veri gonderme.

## Bu haftanin deney notlari

> Asagisini kendin doldur.

- [ ] Ayni promptu `gemini-3.5-flash-lite` ile temperature 0 ve 1.5'te calistir - fark ne?
- [ ] Ayni deneyi `gemini-3.8-flash` ile yap - fark olusuyor mu? (Olmamali, neden?)
- [ ] Max output tokens'i 64'e dusur - yanit nerede kesiliyor?
- [ ] Gecersiz bir model adi gir - hangi hata kodu geliyor?
- [ ] `gemini-4-argon` sec - hangi hata geliyor?
- [ ] Uzun bir soru sor ve `dusunme` token sayisina bak - cikti token'indan fazla mi?
- [ ] `logs/usage.jsonl` dosyasina bak - 10 istegin ucretli kademe karsiligi ne?

## Cikti

- `uv run python -m lessons.week01_first_request` → terminalden ilk istek
- `uv run streamlit run app.py` → temel AI Chat ekrani
