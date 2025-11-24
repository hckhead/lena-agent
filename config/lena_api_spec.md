# LENA REST API Specification

이 파일에 LENA REST API의 명세를 정의해주세요. 에이전트는 이 정보를 바탕으로 적절한 API를 호출합니다.

## Base URL

환경 변수 `LENA_API_URL`에 설정된 URL을 기본으로 사용합니다.

## Authentication

모든 요청에는 환경 변수 `LENA_API_KEY`가 쿼리 파라미터 `key`로 자동 추가됩니다. (예: `?key=VALUE`)

## Endpoints

### 1. 서버 상태 확인

* **Method**: GET
* **Path**: /status
* **Description**: LENA 서버의 현재 상태를 확인합니다.
* **Parameters**: 없음

### 2. 애플리케이션 목록 조회

* **Method**: GET
* **Path**: /apps
* **Description**: 배포된 애플리케이션 목록을 반환합니다.
* **Parameters**:
  * `type` (optional): 애플리케이션 타입 필터 (e.g., 'web', 'was')

### 3. (예시) 특정 서버 재시작

* **Method**: POST
* **Path**: /servers/{serverId}/restart
* **Description**: 지정된 ID의 서버를 재시작합니다.
* **Body**:
  * `force`: boolean (강제 재시작 여부)

---
**작성 팁:**

* API의 경로(Path)와 메서드(Method)를 명확히 적어주세요.
* 어떤 상황에서 이 API를 써야 하는지 설명(Description)을 자세히 적으면 에이전트의 정확도가 올라갑니다.
