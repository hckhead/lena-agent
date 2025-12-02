# config/ 폴더

이 폴더에는 Agent의 설정 파일이 포함됩니다.

## lena_api_spec.md

LENA REST API의 엔드포인트 명세를 정의하는 문서입니다.

### 용도

Agent의 시스템 프롬프트에 자동으로 로드되어, 적절한 API 엔드포인트를 선택하고 호출하는 데 사용됩니다.

### 형식

```markdown
# API 명세

## POST /api/endpoint
- 설명: 엔드포인트 설명
- 파라미터:
  - param1: 설명
  - param2: 설명
- 응답: 응답 형식 설명
```

### 수정 방법

1. `lena_api_spec.md` 파일을 편집합니다
2. Agent를 재시작하면 새로운 명세가 로드됩니다

### 주의사항

- **API 키는 이 파일에 저장하지 마세요!**
- API 키는 `.env` 파일 또는 Claude Desktop 설정에서 관리합니다
- 실제 API URL 예시는 가급적 제외하고, 명세만 기술합니다

## 추가 설정 파일

필요에 따라 추가 설정 파일을 이 폴더에 포함할 수 있습니다.
