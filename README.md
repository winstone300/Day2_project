# LocalHub

서울 공공데이터를 활용하는 지역 정보 공유 커뮤니티의 모노레포입니다.

현재 구현 범위는 1단계 프로젝트 기반입니다. Vue 라우팅, FastAPI 상태 API,
SQLAlchemy SQLite 연결, 환경변수 및 CORS 구성까지만 포함합니다. 게시판 CRUD와
서울 JSON 로딩은 다음 단계에서 구현합니다.

## 디렉터리

```text
day2_project/
├─ frontend/       Vue.js 3 + Vite
├─ backend/        FastAPI + SQLAlchemy
├─ database/       제출용 DB 보관 위치
└─ docs/           산출물 보관 위치
```

## 백엔드 실행

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

- API 문서: `http://localhost:8000/docs`
- 상태 API: `http://localhost:8000/api/health`

## 프론트엔드 실행

```powershell
cd frontend
pnpm install
Copy-Item .env.example .env
pnpm dev
```

- 개발 주소: `http://localhost:5173`

## 환경변수

실제 `.env`는 Git에 포함하지 않습니다. 루트와 각 애플리케이션의
`.env.example`을 복사해 사용합니다.

## 데이터 출처

`backend/data/seoul`에는 한국관광공사 TourAPI 4.0에서 제공된 서울 지역 JSON
원본 7개와 스키마·출처 문서를 보관합니다. 원본은 수정하지 않습니다.
