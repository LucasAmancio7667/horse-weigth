# Peso do Cavalo

App que estima o peso de um cavalo a partir de uma foto lateral. Este repositório está no fim da **Sprint 1**: ambiente, API, banco modelado, Blob Storage e teste isolado do marcador ArUco.

## Stack

| Camada | Tecnologia |
| --- | --- |
| Cliente | React + Vite (PWA na Sprint 2) |
| API | FastAPI (Python) |
| Banco | SQLite via SQLAlchemy 2 |
| Imagens | Azure Blob Storage (emulador Azurite no desenvolvimento) |
| Visão | OpenCV com marcador ArUco |

## Estrutura

```
backend/
  app/
    main.py          # app FastAPI, CORS, criação das tabelas
    config.py        # configurações (variáveis de ambiente / .env)
    db.py            # engine e sessão
    models.py        # Animal, Photo, Landmark, Measurement, WeightEstimate
    schemas.py       # validação de entrada e saída
    storage.py       # Azure Blob (upload, download, health)
    routers/         # /api/health e /api/animals
    vision/aruco.py  # detecção do marcador e escala px/cm
  scripts/aruco_demo.py
  tests/
frontend/            # React + Vite, tela de estado do sistema
docker-compose.yml   # azurite + api + web
```

## Como rodar

### Com Docker

```bash
docker compose up --build
```

Web em http://localhost:5173, API em http://localhost:8000 (documentação em `/docs`).

### Sem Docker (três terminais)

```bash
# 1. Emulador do Blob Storage
npx azurite-blob --location azurite-data

# 2. API
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 3. Frontend
cd frontend
npm install
npm run dev
```

Os valores padrão já apontam para o Azurite local e para um SQLite em `backend/data/`. Para mudar algo, copie `.env.example` para `backend/.env`.

## Testes

```bash
cd backend && pytest
```

Cobrem a API (saúde, cadastro, validação), o modelo de dados (relações, cascata, restrições) e o ArUco (escala, rotação, ausência de marcador).

## Teste do ArUco

```bash
cd backend
python scripts/aruco_demo.py                    # gera marker_0.png e uma cena de teste
python scripts/aruco_demo.py foto.jpg 10        # detecta numa foto sua (lado real em cm)
```

Ao imprimir `marker_0.png`, **meça com régua o lado do quadrado preto** (sem a margem branca). Esse valor é o `marker_size_cm` usado no cálculo da escala.

## Decisões da Sprint 1

- **Tabelas criadas no startup** (`create_all`). Se o esquema começar a mudar com frequência, trocar por Alembic.
- **Peso real da balança** é um campo opcional em `Photo`, para a coleta futura entrar sem alterar o esquema.
- **`/api/health`** devolve o estado do banco e do storage separadamente; a API é considerada de pé se o banco responde.
- **Escala** vem do lado médio do marcador em pixels dividido pelo tamanho real em cm; com vários marcadores, usa o maior.

## Próxima: Sprint 2

Cliente PWA com câmera, upload da foto para o Blob, registro no banco, listagem de fotos e escala px/cm calculada no backend.
