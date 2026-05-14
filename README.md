# AI Startup Mentor

Türkçe sohbet ile girişim fikirlerini analiz eden, SWOT/pazar/iş modeli raporu üretip skorlayan FastAPI backend.

## Özellikler

- OpenAI tabanlı Türkçe mentör sohbeti (`gpt-4o-mini`)
- Yeterli bilgi toplandığında otomatik **SWOT + pazar + iş modeli** analizi
- Ağırlıklı **0-100 skorlama** algoritması
- Wikipedia REST API üzerinden basit **pazar/rakip veri toplayıcı**
- Fikir başına **CSV** ve **PDF** export
- JWT tabanlı kimlik doğrulama
- PostgreSQL + SQLAlchemy async

## Kurulum

```bash
cd api
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`.env` dosyası oluşturun:

```
OPENAI_API_KEY=sk-...
SECRET_KEY=change-me-in-production

PGUSER=postgres
PGPASSWORD=postgres
PGHOST=localhost
PGPORT=5432
PGDATABASE=ai-mentor-db
```

## Çalıştırma

```bash
cd api
uvicorn main:app --reload
```

Sunucu `http://localhost:8000` adresinde başlar. Swagger UI: `http://localhost:8000/docs`.

## Örnek veri yükleme

```bash
cd api
python seed_data.py
```

Demo kullanıcı: **seed@example.com** / **Seed12345** — altında 5 örnek fikir oluşur.

## API Endpoint'leri

### Auth
| Method | URL | Açıklama |
|---|---|---|
| POST | `/api/auth/register` | Kullanıcı kaydı |
| POST | `/api/auth/login` | Giriş, JWT döner |
| POST | `/api/auth/logout` | Çıkış |
| DELETE | `/api/auth/delete-account` | Hesap silme |

### AI
| Method | URL | Açıklama |
|---|---|---|
| POST | `/api/ai/chat` | Mentör ile sohbet (`{"message": "..."}`) |
| GET | `/api/ai/market-context?topic=...` | Wikipedia'dan pazar/rakip bağlamı |

`/api/ai/chat` cevabında `idea_ready: true` geldiğinde Idea kaydedilmiş ve skorlanmış olur.

### Idea
| Method | URL | Açıklama |
|---|---|---|
| GET | `/api/idea/` | Kullanıcının tüm fikirleri (özet liste) |
| GET | `/api/idea/{id}` | Tek fikir detayı |
| DELETE | `/api/idea/{id}` | Fikir silme |
| GET | `/api/idea/{id}/export.csv` | CSV indirme |
| GET | `/api/idea/{id}/export.pdf` | PDF indirme |

Tüm AI ve Idea endpoint'leri `Authorization: Bearer <token>` ister.

## Skorlama

`score = market_size·0.30 + innovation·0.25 + feasibility·0.25 + competition_advantage·0.20`

Her bileşen AI çıktısındaki SWOT/market_analysis verisinden 0-10 arası heuristik ile türetilir,
ağırlıklı toplam 0-100 ölçeğine normalize edilir. Detay: `src/controllers/idea_controller.py`.

## Proje Yapısı

```
api/
├── main.py
├── requirements.txt
├── seed_data.py
└── src/
    ├── controllers/   # auth_, ai_, idea_controller
    ├── routes/        # auth_, ai_, idea_router
    ├── services/      # ai_service, scraper_service
    └── lib/
        ├── db/
        │   ├── database.py
        │   ├── models/   # user, chat, idea
        │   └── schemas/  # user_, chat_, idea_schema
        └── utils/        # security, error
```
