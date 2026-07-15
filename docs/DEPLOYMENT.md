# LocalHub 임시 배포 가이드

9단계 배포는 Netlify 프론트엔드와 Render 무료 백엔드로 구성한다. 백엔드는
영구 디스크 없이 `/tmp/localhub.db`를 사용하는 **임시 SQLite** 방식이다.

## 주의 사항

- Render 무료 서비스가 재시작·재배포되거나 유휴 상태에서 종료되면 SQLite의
  게시글 데이터가 삭제될 수 있다.
- 서버가 다시 시작되면 애플리케이션이 테이블과 환영 게시글을 자동 생성한다.
- 제출·시연용 임시 환경에만 사용한다. 실제 운영에서는 Render Postgres 또는
  유료 영구 디스크로 전환해야 한다.
- `.env`와 API 키는 저장소에 커밋하지 않는다.

## 1. Render 백엔드 생성

1. Render에서 **New > Blueprint**를 선택하고 GitLab 저장소를 연결한다.
2. 저장소 루트의 `render.yaml`을 선택한다.
3. `CORS_ORIGINS`에는 우선 `http://localhost:5173`을 입력한다.
4. Blueprint를 적용하고 `localhub-api` 배포가 완료될 때까지 기다린다.
5. 발급된 주소를 기록한다. 예: `https://localhub-api.onrender.com`
6. 아래 주소가 HTTP 200과 `status: ok`를 반환하는지 확인한다.

```text
https://<Render 주소>/api/health
https://<Render 주소>/docs
```

Render 설정의 핵심 값은 다음과 같다.

```text
Root Directory: backend
Build Command: pip install --no-cache-dir -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
DATABASE_URL: sqlite:////tmp/localhub.db
```

## 2. Netlify 프론트엔드 생성

1. Netlify에서 **Add new project > Import an existing project**를 선택한다.
2. 동일한 GitLab 저장소를 연결한다.
3. 저장소 루트의 `netlify.toml` 설정이 인식됐는지 확인한다.
4. Netlify 환경변수에 다음 값을 등록한다.

```text
VITE_API_BASE_URL=https://<Render 주소>
```

5. 배포를 실행하고 발급된 `https://<사이트명>.netlify.app` 주소를 기록한다.
6. `/posts`, `/posts/new`, `/posts/1`을 직접 새로고침해도 화면이 열리는지
   확인한다. `netlify.toml`의 SPA rewrite가 이 경로를 처리한다.

## 3. CORS 최종 연결

Render의 `CORS_ORIGINS`를 아래처럼 변경하고 백엔드를 재배포한다.

```text
http://localhost:5173,https://<사이트명>.netlify.app
```

여러 주소는 쉼표로 구분하며 끝에 `/`를 붙이지 않는다. Netlify에서 홈·게시판
CRUD·지역정보 챗봇·게시글 검색 챗봇을 차례로 확인한다.

## 4. 임시 SQLite 초기화 확인

1. 시연용 게시글을 하나 작성한다.
2. Render에서 서비스를 재시작한다.
3. 작성한 게시글이 사라지고 환영 게시글이 다시 생성되는지 확인한다.

이 동작은 이번 단계에서 의도한 임시 저장 방식이다.

## 최종 제출 값

```text
Frontend URL: https://<사이트명>.netlify.app
Backend URL: https://<서비스명>.onrender.com
API Docs: https://<서비스명>.onrender.com/docs
Health Check: https://<서비스명>.onrender.com/api/health
```
