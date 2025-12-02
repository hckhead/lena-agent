# LENA Agent 배포 가이드

이 문서는 LENA Agent를 사용자에게 배포하는 방법을 설명합니다.

---

## 📦 배포 준비

### 1. GitHub 저장소 준비

```bash
# 저장소 생성 (GitHub에서)
# 예: https://github.com/your-org/lena-agent

# 로컬 저장소 초기화 (필요 시)
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-org/lena-agent.git
git push -u origin main
```

### 2. 버전 태그 생성 (권장)

```bash
# 버전 태그 생성
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

---

## 👥 사용자 설치 방법

### Public Repository

사용자에게 제공할 설치 명령:

```bash
# 최신 버전 설치
uv tool install git+https://github.com/your-org/lena-agent.git

# 특정 버전 설치
uv tool install git+https://github.com/your-org/lena-agent.git@v0.1.0

# 특정 브랜치 설치
uv tool install git+https://github.com/your-org/lena-agent.git@develop
```

### Private Repository

사용자가 GitHub에 액세스 권한이 있어야 합니다:

```bash
# SSH 키 설정된 경우
uv tool install git+ssh://git@github.com/your-org/lena-agent.git

# Personal Access Token 사용
uv tool install git+https://YOUR_TOKEN@github.com/your-org/lena-agent.git
```

---

## 🔧 사용자 설정 가이드

### Step 1: 환경 변수 설정

**옵션 A: Claude Desktop 설정에 직접 입력** (권장)

`claude_desktop_config.json`:

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

**옵션 B: .env 파일 사용**

현재 프로젝트 구조에서는 `.env` 파일이 설치 디렉토리에 있어야 합니다:

```bash
# 설치 위치 찾기 (Windows)
where lena-agent

# 설치 위치 찾기 (Linux/Mac)
which lena-agent

# .env 파일 생성
# 위치: uv tool 설치 디렉토리
```

---

## 📝 사용자에게 제공할 문서

### README_FOR_USERS.md

```markdown
# LENA Agent 설치 가이드

## 설치

\```bash
uv tool install git+https://github.com/your-org/lena-agent.git
\```

## 필수 API 키

1. **OpenAI API Key**: RAG 기능용
2. **Tavily API Key**: 웹 검색용

## Claude Desktop 설정

파일: `%APPDATA%\Claude\claude_desktop_config.json`

\```json
{
  "mcpServers": {
    "lena-agent": {
      "command": "lena-agent",
      "env": {
        "OPENAI_API_KEY": "your-openai-key",
        "TAVILY_API_KEY": "your-tavily-key"
      }
    }
  }
}
\```

## 사용 예시

Claude Desktop에서:
- "내부 문서에서 정보 찾아줘"
- "httpbin.org 호출해줘"
- "웹에서 LENA 검색해줘"

## REST API 사용

\```bash
# API 서버 실행
lena-agent-api

# 호출
curl http://localhost:8000/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
\```
```

---

## 🔄 업데이트 배포

### 1. 코드 업데이트

```bash
# 코드 수정 후
git add .
git commit -m "Update: 새로운 기능 추가"
git push origin main

# 새 버전 태그
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

### 2. 사용자 업데이트 안내

```bash
# 방법 1: uv 업그레이드
uv tool upgrade lena-agent

# 방법 2: 재설치
uv tool uninstall lena-agent
uv tool install git+https://github.com/your-org/lena-agent.git@v0.2.0
```

---

## 📊 배포 체크리스트

### 배포 전

- [ ] `pyproject.toml`에서 버전 번호 업데이트
- [ ] `README.md` 업데이트
- [ ] `INSTALL.md` 확인
- [ ] `.env.example` 최신 상태 확인
- [ ] 테스트 실행 (`test_agent.py`, `test_api.py`)
- [ ] docs/ 폴더의 샘플 문서 확인
- [ ] config/ 폴더의 API 명세 확인

### 배포

- [ ] Git 커밋 및 푸시
- [ ] 버전 태그 생성 및 푸시
- [ ] GitHub Release 생성 (선택)
- [ ] CHANGELOG.md 업데이트 (선택)

### 배포 후

- [ ] 사용자 테스트 환경에서 설치 확인
- [ ] MCP 모드 동작 확인
- [ ] API 모드 동작 확인
- [ ] 문서 링크 작동 확인

---

## 🐛 일반적인 문제 및 해결

### "command not found: lena-agent"

사용자에게 안내:

```bash
# PATH 확인
echo $PATH

# uv tool bin 디렉토리를 PATH에 추가
# Windows: 환경 변수 설정
# Linux/Mac: ~/.bashrc 또는 ~/.zshrc에 추가
export PATH="$HOME/.local/bin:$PATH"
```

### "ModuleNotFoundError"

```bash
# 재설치
uv tool uninstall lena-agent
uv tool install git+https://github.com/your-org/lena-agent.git
```

### Private Repo 접근 실패

```bash
# SSH 키 설정 또는
# Personal Access Token 사용
```

---

## 📈 모니터링 및 피드백

### 사용자 피드백 수집

- GitHub Issues 활용
- 사용자 설문조사
- 로그 분석 (선택)

### 버전별 사용 현황

```bash
# GitHub Insights > Traffic
# 다운로드 수, 클론 수 확인
```

---

## 🔐 보안 고려사항

### API 키 관리

- **절대 저장소에 .env 파일을 커밋하지 마세요!**
- `.gitignore`에 `.env` 포함 확인
- 사용자에게 API 키를 안전하게 관리하도록 안내

### Private 문서

- `docs/` 폴더에 민감한 정보가 없는지 확인
- `config/lena_api_spec.md`에 실제 API 키가 포함되지 않도록 확인

---

## 💡 Best Practices

1. **시맨틱 버저닝**: v0.1.0, v0.2.0, v1.0.0
2. **CHANGELOG 유지**: 각 버전의 변경사항 기록
3. **테스트 자동화**: CI/CD 파이프라인 구축 (선택)
4. **문서 최신화**: 기능 추가 시 문서 업데이트
5. **Issue 템플릿**: GitHub Issue 템플릿 제공

---

## 📞 지원

사용자 지원 채널:

- GitHub Issues
- 이메일 지원
- 내부 Slack/Teams 채널
