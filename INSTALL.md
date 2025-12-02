# LENA Agent 설치 가이드

## 📋 요구사항

- **Python**: 3.10 이상
- **uv**: Python 패키지 관리자 ([설치 방법](https://docs.astral.sh/uv/))
- **필수 API 키**:
  - OpenAI API Key (RAG 기능용)
  - Tavily API Key (웹 검색용)
- **선택적**:
  - LENA REST API URL 및 Key (HTTP 요청 기능용)
  - Context7 MCP 서버 (Apache/Nginx/Tomcat 문서 검색용)

---

## 🚀 설치 방법

### Option 1: Git에서 직접 설치 (권장)

```bash
# Git 저장소에서 설치
uv tool install git+https://github.com/username/lena-agent.git

# 또는 특정 브랜치
uv tool install git+https://github.com/username/lena-agent.git@main

# 또는 특정 태그
uv tool install git+https://github.com/username/lena-agent.git@v0.1.0
```

### Option 2: 로컬 클론 후 설치

```bash
# 1. 저장소 클론
git clone https://github.com/username/lena-agent.git
cd lena-agent

# 2. 의존성 설치
uv sync

# 3. 개발 모드로 설치 (선택사항)
uv pip install -e .
```

---

## ⚙️ 환경 설정

### 1. .env 파일 생성

```bash
# .env.example을 .env로 복사
cp .env.example .env

# Windows PowerShell
Copy-Item .env.example .env
```

### 2. API 키 입력

`.env` 파일을 편집하여 실제 API 키 입력:

```bash
# OpenAI API Key (required for RAG)
OPENAI_API_KEY=sk-proj-your-actual-key-here

# Tavily API Key (required for web search)
TAVILY_API_KEY=tvly-your-actual-key-here

# LENA REST API Configuration (optional)
LENA_API_URL=http://your-lena-api.com
LENA_API_KEY=your-lena-api-key

# RAG Configuration (optional)
# RAG_ENABLE_RERANK=true
```

---

## 🎯 사용 방법

### Mode 1: MCP 서버 (Claude Desktop용)

#### Claude Desktop 설정

**설정 파일 위치**:

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Git 설치 후** (`uv tool install git+...`):

```json
{
  "mcpServers": {
    "lena-agent": {
      "command": "lena-agent",
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "TAVILY_API_KEY": "tvly-...",
        "LENA_API_URL": "http://...",
        "LENA_API_KEY": "..."
      }
    }
  }
}
```

**로컬 클론 후**:

```json
{
  "mcpServers": {
    "lena-agent": {
      "command": "uv",
      "args": ["--directory", "/path/to/lena-agent", "run", "server.py"],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "TAVILY_API_KEY": "tvly-..."
      }
    }
  }
}
```

> **💡 Tip**: Git 설치 방식이 더 간단합니다!

#### Claude Desktop 재시작

설정 후 Claude Desktop을 완전히 종료하고 재시작합니다.

#### 사용 예시

Claude Desktop 채팅에서 자연스럽게 대화:

```
"내부 문서에서 Project X 정보 찾아줘"
→ RAG 도구 자동 사용

"httpbin.org/get 호출해줘"
→ HTTP 요청 도구 자동 사용

"docs.lenalab.org에서 LENA 검색해줘"
→ Tavily 검색 도구 자동 사용
```

---

### Mode 2: REST API 서버

#### 서버 실행

**Git 설치 후**:

```bash
lena-agent-api
```

**로컬 클론 후**:

```bash
uv run api_server.py
```

서버는 `http://localhost:8000`에서 실행됩니다.

#### API 호출 예시

**Python**:

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "LENA에 대해 알려줘"}
        ]
    }
)

print(response.json()["choices"][0]["message"]["content"])
```

**cURL (PowerShell)**:

```powershell
$body = @{
    messages = @(
        @{
            role = "user"
            content = "LENA에 대해 알려줘"
        }
    )
} | ConvertTo-Json -Depth 10

Invoke-WebRequest -Uri "http://localhost:8000/v1/chat/completions" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

---

## 🧪 테스트

```bash
# 기능 테스트
uv run test_agent.py

# API 테스트
uv run test_api.py
```

---

## 🔧 문제 해결

### Git 설치 실패

```bash
# SSH 키 설정이 안된 경우, HTTPS 사용
uv tool install git+https://github.com/username/lena-agent.git

# Private 저장소의 경우 Personal Access Token 필요
uv tool install git+https://YOUR_TOKEN@github.com/username/lena-agent.git
```

### MCP 서버 연결 실패

1. Claude Desktop을 완전히 종료
2. 설정 파일 경로 확인
3. API 키 확인
4. Claude Desktop 재시작

### API 서버 포트 충돌

```bash
# 다른 포트로 실행 (코드 수정 필요)
# api_server.py의 port=8000을 원하는 포트로 변경
```

### RAG 임베딩 오류

- `OPENAI_API_KEY`가 올바른지 확인
- `chroma_db/` 폴더 삭제 후 재시작

---

## 📁 프로젝트 구조

```
lena-agent/
├── agent/
│   ├── __init__.py
│   ├── graph.py          # LangGraph Agent
│   ├── tools.py          # HTTP, Tavily 도구
│   ├── rag.py            # RAG 검색
│   ├── context7.py       # Context7 MCP
│   └── state.py          # Agent 상태
├── config/
│   └── lena_api_spec.md  # LENA API 명세
├── docs/
│   ├── test_doc.txt      # 테스트 문서
│   └── project_x.txt     # 프로젝트 문서
├── server.py             # MCP 서버
├── api_server.py         # REST API 서버
├── pyproject.toml        # 프로젝트 설정
├── .env.example          # 환경 변수 예시
└── README.md             # 프로젝트 설명
```

---

## 🆘 지원

문제가 발생하면:

1. [Issues](https://github.com/username/lena-agent/issues)에 문의
2. README.md의 트러블슈팅 섹션 확인
3. 로그 확인 (`chroma_db/` 및 콘솔 출력)

---

## 📝 업데이트

```bash
# Git 설치 버전 업데이트
uv tool upgrade lena-agent

# 또는 재설치
uv tool uninstall lena-agent
uv tool install git+https://github.com/username/lena-agent.git
```

---

## ✅ 설치 완료 확인

**MCP 모드**:

- Claude Desktop에서 🔧 아이콘 확인

**API 모드**:

```bash
curl http://localhost:8000/
# {"status":"ok","service":"LENA Agent API","version":"1.0.0"}
```
