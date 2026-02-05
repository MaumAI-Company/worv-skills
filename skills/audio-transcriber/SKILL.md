---
name: audio-transcriber
description: OpenAI Whisper API를 사용하여 오디오 파일을 텍스트로 변환합니다. m4a, WAV 등 다양한 포맷 지원. gpt-4o-transcribe-diarize 모델로 화자분리(Speaker Diarization)도 지원.
---

# Audio Transcriber - 오디오 STT 스킬

OpenAI Whisper API를 사용하여 오디오 파일을 텍스트로 변환하는 스킬입니다.

## 사용 시점

- "녹음 파일 변환해줘"
- "오디오를 텍스트로 만들어줘"
- "STT 해줘"
- "화자분리해서 변환해줘" (--diarize 옵션)

## 기능

- **기본 STT**: OpenAI Whisper API (whisper-1 모델)
- **화자분리 STT**: gpt-4o-transcribe-diarize 모델 (2025년 12월 출시)
- 지원 포맷: m4a, WAV, mp3, mp4, mpeg, mpga, webm
- 자동 청크 분할 (25MB 제한)
- 타임스탬프 포함 옵션
- 언어 자동 감지 (한국어/영어)

## 환경 설정

`.env` 파일에 API 키 필요:
```
OPENAI_API_KEY=sk-...
```

## 사용 방법

### 기본 STT (whisper-1)
```bash
python scripts/transcribe.py <audio_file> [--output output.txt] [--language ko]
```

### 화자분리 STT (gpt-4o-transcribe-diarize)
```bash
python scripts/transcribe.py <audio_file> --diarize [--language ko]
```

### 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `-o, --output` | 출력 파일 경로 | 입력파일명.txt |
| `-l, --language` | 언어 코드 (ko, en, auto) | ko |
| `-t, --timestamp` | 타임스탬프 포함 | False |
| `-m, --model` | Whisper 모델 | whisper-1 |
| `-d, --diarize` | 화자분리 활성화 | False |
| `-f, --force` | 대화형 확인 건너뛰기 | False |

## 출력 형식

### 기본 모드
```
전사된 텍스트 내용...
```

### 타임스탬프 모드 (--timestamp)
```
[00:00:00] 텍스트 내용
[00:00:15] 다음 내용
```

### 화자분리 모드 (--diarize)
```
[A] 안녕하세요, 오늘 미팅 시작하겠습니다.

[B] 네, 반갑습니다. 지난번 논의한 내용부터 시작하죠.

[A] 좋습니다. 먼저 프로젝트 진행 상황을 공유드리면...
```

## 화자분리 기능 상세

### 모델 정보
- **모델명**: `gpt-4o-transcribe-diarize`
- **출시일**: 2025년 12월
- **공식 문서**: https://platform.openai.com/docs/models/gpt-4o-transcribe-diarize

### 특징
- 자동 화자 감지 및 라벨링 (A, B, C...)
- 화자별 발언 그룹핑
- 30초 이상 오디오에서 `chunking_strategy="auto"` 자동 적용

### 제한사항
- 화자 이름 자동 매칭 미지원 (A, B 등 라벨로 출력)
- prompt 파라미터 미지원
- timestamp_granularities 미지원
- 가끔 화자 수를 과다 추정하는 경우 있음 (hallucination)

## 처리 흐름

1. 오디오 파일 검증
2. 25MB 초과 시 자동 분할 (ffmpeg 사용)
3. 화자분리 모드 확인
   - True: gpt-4o-transcribe-diarize API 호출
   - False: whisper-1 API 호출
4. 결과를 .txt 파일로 저장
5. 성공 여부 반환

## 참고 자료

- [OpenAI Speech-to-Text Guide](https://platform.openai.com/docs/guides/speech-to-text)
- [GPT-4o Transcribe Diarize Model](https://platform.openai.com/docs/models/gpt-4o-transcribe-diarize)
- [OpenAI Community: Introducing GPT-4o Transcribe Diarize](https://community.openai.com/t/introducing-gpt-4o-transcribe-diarize-now-available-in-the-audio-api/1362933)
