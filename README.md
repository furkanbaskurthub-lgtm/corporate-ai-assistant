# Kurumsal AI Asistan

PDF, TXT ve LOG dosyalarınızı yükleyip bu dokümanlar üzerinden yapay zeka ile sohbet edebildiğiniz bir platformdur. Yüklediğiniz dosyalar otomatik olarak parçalanır, vektör veritabanına kaydedilir ve siz soru sorduğunuzda ilgili bölümler bulunup GPT modeline bağlam olarak verilir. Bu sayede yapay zeka genel bilgi yerine sizin dokümanlarınıza dayalı cevap üretir. Buna RAG (Retrieval-Augmented Generation) denir.

Her kullanıcının kendi hesabı, kendi dokümanları ve kendi sohbet geçmişi vardır. Cevaplar ChatGPT'deki gibi anlık akış (streaming) şeklinde gelir ve her cevabın hangi dokümanın hangi sayfasından alındığı gösterilir.

## Ne yapabilirsiniz?

- PDF, TXT veya LOG dosyası yükleyebilirsiniz (maks 50MB)
- Yüklenen dosyalar otomatik olarak işlenir: metin çıkarılır, parçalara ayrılır, embedding vektörleri oluşturulur
- Sohbet sayfasından dokümanlarınız hakkında sorular sorabilirsiniz
- GPT-3.5 Turbo, GPT-4 veya GPT-4 Turbo arasında model değiştirebilirsiniz
- Her cevabın altında kaynak doküman ve sayfa bilgisini görebilirsiniz
- Birden fazla sohbet oturumu açıp yönetebilirsiniz

## Kullanılan Teknolojiler

**Backend:**
- Python 3.11 ve FastAPI — async API sunucusu
- SQLAlchemy (async) + SQLite — veritabanı
- PyMuPDF — PDF'lerden metin çıkarma
- OpenAI API — embedding oluşturma ve GPT ile cevap üretme
- FAISS (Facebook AI Similarity Search) — vektör benzerlik araması
- JWT + bcrypt — kullanıcı kimlik doğrulama
- WebSocket — gerçek zamanlı streaming chat

**Frontend:**
- React 18 + Vite 5 — hızlı geliştirme ve build
- TailwindCSS — stil ve tasarım
- Zustand — state yönetimi
- React Router — sayfa yönlendirme
- Axios — HTTP istekleri

**DevOps:**
- Docker + docker-compose — konteynerize deployment
- Nginx — frontend sunucu (production)

## Sistem Nasıl Çalışıyor?

1. Kullanıcı bir PDF yükler
2. Backend dosyayı okur, metni çıkarır ve 1000 karakterlik parçalara böler
3. Her parça OpenAI embedding API'sine gönderilip vektöre dönüştürülür
4. Vektörler FAISS indeksine kaydedilir
5. Kullanıcı sohbette soru sorduğunda, soru da vektöre dönüştürülür
6. FAISS'te en benzer 5 parça bulunur
7. Bu parçalar + soru birlikte GPT'ye gönderilir
8. GPT, doküman bağlamına dayalı cevap üretir ve WebSocket ile anlık olarak kullanıcıya iletilir

## Kurulum

### Gereksinimler

- Python 3.11 veya üzeri
- Node.js 20 veya üzeri
- Bir OpenAI API key'i (https://platform.openai.com/api-keys adresinden alabilirsiniz, bakiye yüklemeniz gerekir)

### 1. Projeyi klonlayın

```bash
git clone https://github.com/furkanbaskurthub-lgtm/corporate-ai-assistant.git
cd corporate-ai-assistant
```

### 2. Backend ortam değişkenlerini ayarlayın

```bash
cp .env.example backend/.env
```

`backend/.env` dosyasını açıp `OPENAI_API_KEY` satırına kendi API anahtarınızı yazın. `SECRET_KEY` için rastgele bir değer üretebilirsiniz:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Backend'i başlatın

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend açıldığında http://localhost:8000/docs adresinden API dokümantasyonunu görebilirsiniz.

### 4. Frontend'i başlatın

Yeni bir terminal açın:

```bash
cd frontend
npm install
npm run dev
```

Tarayıcıda http://localhost:5173 adresine gidin.

### 5. Kullanmaya başlayın

1. Kayıt olun (Register sayfası)
2. Giriş yapın
3. Dokümanlar sayfasından PDF/TXT/LOG dosyası yükleyin
4. Dosya işlenene kadar bekleyin (durum "Hazır" olacak)
5. Sohbet sayfasına geçin ve dokümanınız hakkında soru sorun

## Docker ile Çalıştırma

Eğer Docker kuruluysa tek komutla her şeyi ayağa kaldırabilirsiniz:

```bash
docker-compose up --build
```

Frontend http://localhost adresinde, backend http://localhost:8000 adresinde çalışacaktır.

## Proje Klasör Yapısı

```
corporate-ai-assistant/
├── backend/
│   ├── app/
│   │   ├── api/v1/              # API endpoint'leri (auth, chat, documents, users)
│   │   ├── ai/                  # RAG pipeline, embedding, FAISS, doküman işleme
│   │   ├── core/                # Config, JWT güvenlik, loglama
│   │   ├── db/                  # Veritabanı bağlantısı ve repository katmanı
│   │   ├── models/              # SQLAlchemy veritabanı modelleri
│   │   ├── schemas/             # Pydantic istek/yanıt şemaları
│   │   ├── services/            # İş mantığı katmanı
│   │   └── main.py              # FastAPI uygulaması giriş noktası
│   ├── requirements.txt         # Python bağımlılıkları
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # React bileşenleri (Auth, Chat, Documents, Layout)
│   │   ├── pages/               # Sayfa bileşenleri
│   │   ├── hooks/               # Custom hook'lar (useAuth, useDocuments)
│   │   ├── services/            # API ve WebSocket istemcileri
│   │   └── stores/              # Zustand state yönetimi
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example                 # Ortam değişkenleri şablonu
├── .gitignore
└── README.md
```

## API Endpoint'leri

**Kimlik Doğrulama:**
- `POST /api/v1/auth/register` — Yeni kullanıcı kaydı
- `POST /api/v1/auth/login` — Giriş yapma (JWT token döner)
- `GET /api/v1/auth/me` — Giriş yapan kullanıcının bilgileri

**Doküman Yönetimi:**
- `POST /api/v1/documents/upload` — Dosya yükleme
- `GET /api/v1/documents/` — Kullanıcının doküman listesi
- `DELETE /api/v1/documents/{id}` — Doküman silme

**Sohbet:**
- `POST /api/v1/chat/sessions` — Yeni sohbet oturumu oluşturma
- `GET /api/v1/chat/sessions` — Oturum listesi
- `GET /api/v1/chat/sessions/{id}/messages` — Mesaj geçmişi
- `DELETE /api/v1/chat/sessions/{id}` — Oturum silme
- `WS /api/v1/chat/ws/{session_id}?token=JWT` — Gerçek zamanlı streaming sohbet

## Ortam Değişkenleri

`backend/.env` dosyasında ayarlanması gereken değerler:

- `OPENAI_API_KEY` — OpenAI API anahtarınız (zorunlu)
- `SECRET_KEY` — JWT token imzalama anahtarı
- `DATABASE_URL` — Veritabanı bağlantı adresi (varsayılan: SQLite)
- `OPENAI_MODEL` — Kullanılacak GPT modeli (varsayılan: gpt-3.5-turbo)
- `CHUNK_SIZE` — Doküman parça boyutu (varsayılan: 1000 karakter)
- `TOP_K_RESULTS` — Aramada dönen parça sayısı (varsayılan: 5)
- `MAX_FILE_SIZE` — Maksimum dosya boyutu (varsayılan: 50MB)
- `DEBUG` — true yaparsanız /docs endpoint'i aktif olur

## Lisans

MIT
