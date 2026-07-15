# LocalHub

서울 공공데이터를 활용하는 지역 정보 공유 커뮤니티의 모노레포입니다.

현재 구현 범위는 6-1단계 서울 지역정보 챗봇 API입니다. 서울 JSON 7개·6,518건을
서버 시작 시 메모리에 적재하고, 게시판 CRUD·검색·정렬과 Vue 화면을 제공합니다.
챗봇은 외부 API 키 없이 서울 원본 데이터에서 장소를 찾아 답변합니다.

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
- 서울 지역 요약: `http://localhost:8000/api/region/summary`
- 지역정보 챗봇: `POST http://localhost:8000/api/chat`

### 지역정보 챗봇 API

```json
{
  "message": "강남 문화시설 추천해줘",
  "max_results": 3
}
```

응답에는 안내 문장과 함께 `title`, `category`, `address`, 좌표, 이미지 URL을
포함한 장소 목록이 반환됩니다. `max_results`는 1~5 사이이며 기본값은 3입니다.
게시글 검색 의도와 챗봇 UI는 다음 단계에서 연동합니다.

### 게시판 API

```text
GET    /api/posts
GET    /api/posts/{id}
POST   /api/posts
POST   /api/posts/{id}/verify-password
PUT    /api/posts/{id}
DELETE /api/posts/{id}
```

목록 API는 다음 쿼리를 지원합니다.

```text
GET /api/posts?page=1&size=10&query=한강&sort=latest
GET /api/posts?page=1&size=10&sort=views
```

목록 응답은 `items`, `total`, `page`, `size`, `total_pages`를 포함하며 게시글
상세 조회가 성공할 때마다 조회수가 1씩 증가합니다.

초기 DB에는 환영 게시글 한 건이 생성됩니다. 시연용 수정 비밀번호는
`localhub-demo`이며 실제 운영 서비스에서는 사용하지 않습니다.

> RFP 요구에 따라 수정용 비밀번호를 평문으로 저장합니다. 이는 교육용으로만
> 허용된 설계이며 실제 서비스에서는 반드시 안전한 비밀번호 해시를 사용해야 합니다.

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

## 백엔드 테스트

```powershell
cd backend
.venv\Scripts\python.exe -m unittest discover -s tests -v
```
