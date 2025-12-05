# LENA Agent Demo

LENA Agent API를 테스트할 수 있는 웹 기반 데모 사이트입니다.

## 설치

```bash
# Git에서 설치 (권장)
uv tool install git+https://github.com/username/lena-agent.git

# 또는 로컬에서
uv sync
```

## 실행 방법

### 1. API 서버 실행

먼저 LENA Agent API 서버를 실행합니다:

```bash
# 설치 후
lena-agent-api

# 또는 로컬에서
uv run api_server.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

### 2. 데모 서버 실행

```bash
# 설치 후
lena-agent-demo

# 또는 로컬에서
uv run python -m demo.server
# 또는
python demo/server.py
```

### 3. 데모 사용

1. 브라우저에서 `http://localhost:3000` 접속
2. "연결 확인" 버튼 클릭하여 API 서버 연결 확인
3. 메시지 입력 또는 예시 버튼 클릭하여 테스트

## CLI 옵션

```bash
lena-agent-demo --help

Options:
  --port, -p      포트 번호 (기본: 3000)
  --api-url       API 서버 URL (기본: http://localhost:8000)
  --no-browser    브라우저 자동 열기 비활성화
```

예시:

```bash
# 다른 포트 사용
lena-agent-demo --port 8080

# 원격 API 서버 사용
lena-agent-demo --api-url http://api.example.com:8000
```

## Docker 실행

```bash
# 데모만 실행 (API 서버 별도 필요)
docker compose up lena-agent-demo

# API + 데모 함께 실행
docker compose up lena-agent-full
```

## 기능

- **RAG 검색**: 내부 문서(`docs/` 폴더) 검색
- **HTTP 요청**: 외부 API 호출
- **Tavily 검색**: LENA 관련 웹 검색
- **Context7**: Apache/Nginx/Tomcat 문서 검색

## 프로젝트 구조

```
demo/
├── __init__.py     # 패키지 초기화
├── index.html      # 데모 웹 UI
├── server.py       # 데모 서버 (HTTP)
└── README.md       # 이 문서
```
