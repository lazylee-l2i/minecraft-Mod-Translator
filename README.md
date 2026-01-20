# Minecraft Mod Translator v2.0

![Minecraft Logo](./mdimg/minecraft_logo_icon_168974.webp)

**AI 기반 마인크래프트 모드 자동 번역기**

> 다중 LLM 지원 | 번역 캐시 | GUI 인터페이스 | Resource Pack 생성 | 비영어권 모드 지원

---

## 📸 미리보기

### 프로그램 인터페이스
![GUI](./mdimg/GUI.PNG)
*직관적인 GUI를 통해 번역 엔진 설정, 모드 관리, 진행 상황 확인이 가능합니다.*

### 번역 결과 예시
![Translation Result](./mdimg/01.png)
*AI를 통해 문맥에 맞는 자연스러운 한국어 번역을 제공합니다.*

---

## 1. 프로젝트 소개

### 1.1 개요
**Minecraft Mod Translator v2.0**은 최신 AI 모델(GPT-4o, Claude 3, Llama 3 등)을 활용하여 마인크래프트 모드를 자동으로 한글화하는 도구입니다.

**모드 파일을 직접 수정하지 않고** Resource Pack(리소스팩) 형태로 번역을 생성하므로, 모드 원본의 무결성을 유지하면서 안전하게 번역을 적용할 수 있습니다.

### 1.2 v2.0의 주요 특징

| 기능 | 설명 |
|------|------|
| **다중 LLM 지원** | OpenAI, OpenRouter, Ollama(로컬) 등 다양한 엔진 선택 가능 |
| **모델 자동 탐색** | Ollama 로컬 모델 및 API 기반 모델 목록 자동 동기화 |
| **스마트 캐시** | 동일한 모드/버전은 재번역 없이 즉시 로드하여 비용과 시간 절감 |
| **원본 번역 보존** | 모드 내에 이미 한글 번역이 포함된 경우 자동으로 감지하여 생략 가능 |
| **다국어 지원** | 포르투갈어, 중국어 등 영어가 아닌 언어로 작성된 모드도 한국어로 번역 |
| **배치 최적화** | 대용량 언어 파일을 분할 처리하여 로컬 LLM의 VRAM 부족 문제 해결 |

---

## 2. 시작하기

### 2.1 필수 요구사항
- **Python 3.10 이상**
- **Ollama** (로컬 모델 사용 시)
- **API Key** (OpenAI 또는 OpenRouter 사용 시)

### 2.2 설치 방법
```bash
# 저장소 클론
git clone https://github.com/lazylee-l2i/minecraft-Mod-Translator.git
cd minecraft-Mod-Translator

# 의존성 설치
pip install -r requirements.txt
```

---

## 3. 사용 방법

### 3.1 프로그램 실행
```bash
python -m src.main
```

### 3.2 번역 엔진 설정

이 프로그램은 **OpenAI**, **OpenRouter**, **Ollama (로컬)** 세 가지 LLM 제공자를 지원합니다.

---

#### 🔷 OpenAI 사용하기

OpenAI의 GPT 모델을 사용하여 고품질 번역을 수행합니다.

**1. API 키 발급**
1. [OpenAI Platform](https://platform.openai.com/)에 접속하여 계정 생성
2. [API Keys 페이지](https://platform.openai.com/api-keys)에서 새 API 키 생성
3. 생성된 키를 안전한 곳에 복사 (한 번만 표시됨)

**2. 프로그램에서 설정**
1. 번역 엔진에서 `OpenAI` 선택
2. API Key 입력란에 발급받은 키 입력
3. `🔄 모델 목록` 클릭하여 사용 가능한 모델 불러오기
4. 원하는 모델 선택 (추천: `gpt-4o` 또는 `gpt-4o-mini`)

**추천 모델**
| 모델 | 특징 |
|------|------|
| `gpt-4o` | 최고 품질, 비용 높음 |
| `gpt-4o-mini` | 빠른 속도, 합리적인 가격, 품질 우수 |

> 💡 **Tip**: `gpt-4o-mini`는 비용 대비 성능이 뛰어나 대량 번역에 추천됩니다.

---

#### 🔶 OpenRouter 사용하기

OpenRouter는 다양한 AI 모델을 **단일 API**로 접근할 수 있는 서비스입니다. OpenAI, Anthropic, Meta 등 여러 제공자의 모델을 사용할 수 있습니다.

**1. API 키 발급**
1. [OpenRouter](https://openrouter.ai/)에 접속하여 계정 생성
2. [Keys 페이지](https://openrouter.ai/keys)에서 새 API 키 생성
3. 생성된 키를 복사

**2. 프로그램에서 설정**
1. 번역 엔진에서 `OpenRouter` 선택
2. API Key 입력란에 발급받은 키 입력
3. `🔄 모델 목록` 클릭하여 사용 가능한 모델 불러오기
4. 원하는 모델 선택

**추천 모델**
| 모델 | 특징 |
|------|------|
| `openai/gpt-4o` | OpenAI GPT-4o |
| `anthropic/claude-3.5-sonnet` | Claude 3.5, 뛰어난 한국어 번역 |
| `google/gemini-2.0-flash-001` | Google Gemini 2.0, 빠른 속도 |
| `meta-llama/llama-3.3-70b-instruct` | Llama 3.3 70B, 무료 티어 가능 |

> 💡 **Tip**: OpenRouter는 무료 크레딧을 제공하므로 부담 없이 시작할 수 있습니다.

---

#### 🟢 Ollama (로컬 LLM) 사용하기

Ollama를 사용하면 **인터넷 연결 없이** 로컬에서 LLM을 실행할 수 있습니다. API 키가 필요 없으며, 무료로 사용할 수 있습니다.

**1. Ollama 설치**
1. [Ollama 공식 사이트](https://ollama.com/)에서 설치 파일 다운로드
2. 설치 후 터미널/PowerShell에서 Ollama 실행 확인:
   ```bash
   ollama --version
   ```

**2. 모델 다운로드**
사용할 모델을 미리 다운로드해야 합니다:
```bash
# 추천 모델 다운로드 예시
ollama pull llama3.2        # 8GB VRAM 권장
ollama pull qwen2.5:7b      # 6GB VRAM 권장
ollama pull gemma2:2b       # 4GB VRAM 권장
```

**3. Ollama 서버 실행**
```bash
ollama serve
```
> 기본 포트는 `http://localhost:11434`입니다.

**4. 프로그램에서 설정**
1. 번역 엔진에서 `Ollama` 선택
2. 서버 URL 확인 (기본값: `http://localhost:11434`)
3. `🔄 모델 목록` 클릭하여 다운로드된 모델 불러오기
4. 원하는 모델 선택

---

### 3.3 VRAM별 추천 모델 (Ollama)

로컬 LLM 사용 시 그래픽카드의 VRAM에 따라 적절한 모델을 선택해야 합니다.

| VRAM 용량 | 추천 모델 | 다운로드 명령어 | 비고 |
|-----------|----------|-----------------|------|
| **4GB 이하** | `gemma2:2b`, `qwen2.5:1.5b` | `ollama pull gemma2:2b` | 기본적인 번역 가능, 복잡한 문장은 품질 저하 |
| **6GB** | `qwen2.5:7b`, `llama3.2:3b` | `ollama pull qwen2.5:7b` | 일반적인 모드 번역에 적합 |
| **8GB** | `llama3.2`, `qwen2.5:7b` | `ollama pull llama3.2` | 균형 잡힌 선택, 대부분의 번역에 충분 |
| **12GB** | `qwen2.5:14b`, `llama3.1:8b` | `ollama pull qwen2.5:14b` | 높은 번역 품질 |
| **16GB 이상** | `qwen2.5:32b`, `llama3.3:70b` | `ollama pull qwen2.5:32b` | 최고 품질, 느린 속도 |

> ⚠️ **VRAM이 부족한 경우**: 클라우드 API(OpenAI, OpenRouter)를 사용하는 것이 더 효율적입니다.

---

### 3.4 번역 단계

1. **엔진 설정**: 위 가이드를 참고하여 LLM 제공자를 설정합니다.
2. **모델 선택**: `🔄 모델 목록` 버튼을 눌러 사용 가능한 모델을 불러온 후 선택합니다.
3. **버전 설정**: 대상 마인크래프트 버전을 선택합니다 (리소스팩 포맷 자동 결정).
4. **모드 추가**: 번역할 모드(`.jar`) 파일을 `input_mods` 폴더에 넣거나 UI에서 추가합니다.
5. **옵션 확인**: '번역 캐시 사용' 및 '원본 번역 포함 모드 생략' 옵션을 확인합니다.
6. **번역 시작**: `🚀 번역 시작` 버튼을 클릭합니다.

---

### 3.5 리소스팩 적용

번역이 완료되면 `result_pack/Translated_ResourcePack.zip` 파일이 생성됩니다.

**적용 방법:**
1. 생성된 `Translated_ResourcePack.zip` 파일을 복사
2. 마인크래프트 `resourcepacks` 폴더에 붙여넣기
   - Windows: `%appdata%\.minecraft\resourcepacks`
   - macOS: `~/Library/Application Support/minecraft/resourcepacks`
   - Linux: `~/.minecraft/resourcepacks`
3. 게임 실행 후 **설정 → 리소스 팩**에서 활성화

---

## 4. 트러블슈팅

### ❌ 배치 크기 관련 오류

일부 모델(특히 로컬 LLM)은 큰 배치 크기에서 다음과 같은 오류가 발생할 수 있습니다:
- `Invalid JSON in response`
- `Translation request timed out`
- `CUDA out of memory`

**해결 방법:**
1. **배치 크기 줄이기**: 기본값 50에서 20~30으로 줄여보세요
2. **더 작은 모델 사용**: VRAM에 맞는 모델을 선택하세요
3. **클라우드 API 사용**: VRAM이 부족하다면 OpenAI/OpenRouter 활용

### ❌ Ollama 연결 오류

```
Cannot connect to Ollama server at http://localhost:11434
```

**해결 방법:**
1. Ollama가 실행 중인지 확인: `ollama serve`
2. 방화벽이 11434 포트를 차단하지 않는지 확인
3. 서버 URL이 올바른지 확인

### ❌ API 키 오류

```
401 Unauthorized
```

**해결 방법:**
1. API 키가 올바르게 입력되었는지 확인
2. API 키에 충분한 크레딧이 있는지 확인
3. OpenRouter의 경우 [Keys 페이지](https://openrouter.ai/keys)에서 키 상태 확인

### ❌ 번역 결과가 이상한 경우

**해결 방법:**
1. 더 큰 모델 사용 (예: `gpt-4o`, `qwen2.5:14b` 이상)
2. 배치 크기를 줄여서 모델이 더 집중할 수 있게 함
3. 로컬 모델보다 클라우드 API가 일반적으로 품질이 높음

---

## 5. 프로젝트 구조
```
src/
├── core/           # 번역 엔진, JAR 추출, 리소스팩 생성 로직
├── ui/             # Tkinter 기반 GUI 컴포넌트 및 스타일
├── config/         # 앱 상수 및 마인크래프트 버전별 설정
├── models/         # 데이터 구조 정의
└── utils/          # 로깅, 파일 관리, 예외 처리
```

---

## 6. 라이선스
이 프로젝트는 **MIT License**를 따릅니다.

---

## 7. 기여하기
버그 제보나 기능 제안은 Issue를 통해 남겨주세요. PR은 언제나 환영합니다!
