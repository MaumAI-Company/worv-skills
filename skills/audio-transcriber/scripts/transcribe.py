#!/usr/bin/env python3
"""
OpenAI Whisper API를 사용한 오디오 파일 STT
- whisper-1: 기본 STT 모델
- gpt-4o-transcribe-diarize: 화자분리(Speaker Diarization) 지원 모델
"""
import os
import sys
import argparse
import subprocess
import tempfile
import shutil
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 화자분리 모델 상수
DIARIZE_MODEL = "gpt-4o-transcribe-diarize"
DEFAULT_MODEL = "whisper-1"

def split_audio_file(audio_path: Path, chunk_size_mb: int = 20) -> list:
    """
    큰 오디오 파일을 작은 청크로 분할

    Args:
        audio_path: 오디오 파일 경로
        chunk_size_mb: 각 청크의 목표 크기 (MB)

    Returns:
        분할된 파일 경로 리스트
    """
    # 파일 정보 가져오기
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_path)],
        capture_output=True, text=True
    )

    try:
        total_duration = float(result.stdout.strip())
    except ValueError:
        print(f"❌ 파일 길이를 확인할 수 없습니다: {audio_path}")
        return []

    file_size_mb = audio_path.stat().st_size / (1024 * 1024)
    num_chunks = int(file_size_mb / chunk_size_mb) + 1
    chunk_duration = total_duration / num_chunks

    print(f"📦 파일 분할 시작...")
    print(f"   전체 길이: {total_duration/60:.1f}분")
    print(f"   분할 개수: {num_chunks}개")
    print(f"   청크당 길이: {chunk_duration/60:.1f}분")

    # 임시 디렉토리 생성
    temp_dir = Path(tempfile.mkdtemp(prefix="audio_split_"))
    chunk_files = []

    try:
        for i in range(num_chunks):
            start_time = i * chunk_duration
            output_file = temp_dir / f"chunk_{i:03d}.m4a"

            # ffmpeg로 청크 추출
            cmd = [
                'ffmpeg', '-i', str(audio_path),
                '-ss', str(start_time),
                '-t', str(chunk_duration),
                '-c:a', 'aac',  # WAV 등 모든 포맷을 m4a로 재인코딩
                '-b:a', '128k',  # 적정 비트레이트
                '-y',  # 덮어쓰기
                str(output_file)
            ]

            subprocess.run(cmd, capture_output=True, check=True)
            chunk_files.append(output_file)
            print(f"   ✓ 청크 {i+1}/{num_chunks} 생성")

        return chunk_files

    except subprocess.CalledProcessError as e:
        print(f"❌ 파일 분할 실패: {e}")
        # 임시 파일 정리
        shutil.rmtree(temp_dir, ignore_errors=True)
        return []

def transcribe_with_diarization(audio_path: Path, client=None, language: str = "ko") -> str:
    """
    화자분리를 포함한 오디오 파일 변환 (gpt-4o-transcribe-diarize 모델 사용)

    Args:
        audio_path: 오디오 파일 경로
        client: OpenAI 클라이언트 (None이면 새로 생성)
        language: 언어 코드

    Returns:
        화자 라벨이 포함된 변환 텍스트 (실패 시 빈 문자열)
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
        return ""

    try:
        if client is None:
            client = OpenAI(api_key=api_key)

        with open(audio_path, "rb") as audio:
            # gpt-4o-transcribe-diarize API 호출
            # 참고: https://platform.openai.com/docs/models/gpt-4o-transcribe-diarize
            response = client.audio.transcriptions.create(
                model=DIARIZE_MODEL,
                file=audio,
                language=language if language != "auto" else None,
                response_format="diarized_json",
                chunking_strategy="auto"  # 30초 이상 오디오에서 필수
            )

        # diarized_json 응답 파싱
        return format_diarized_response(response)

    except Exception as e:
        print(f"❌ 화자분리 STT 실패: {e}")
        return ""


def format_diarized_response(response) -> str:
    """
    diarized_json 응답을 읽기 좋은 형식으로 변환

    Args:
        response: OpenAI API 응답 객체

    Returns:
        포맷된 텍스트 (화자 라벨 + 타임스탬프 포함)
    """
    try:
        # 응답을 dict로 변환
        if hasattr(response, 'to_dict'):
            data = response.to_dict()
        elif hasattr(response, 'model_dump'):
            data = response.model_dump()
        else:
            data = response

        # segments 추출
        segments = data.get('segments', [])
        if not segments:
            # segments가 없으면 text만 반환
            return data.get('text', '')

        # 화자별로 그룹핑하여 출력
        lines = []
        current_speaker = None
        current_texts = []

        for segment in segments:
            speaker = segment.get('speaker', 'Unknown')
            text = segment.get('text', '').strip()
            start = segment.get('start', 0)

            if not text:
                continue

            # 화자가 바뀌면 이전 발언 저장
            if speaker != current_speaker:
                if current_speaker and current_texts:
                    lines.append(f"[{current_speaker}] {' '.join(current_texts)}")
                current_speaker = speaker
                current_texts = [text]
            else:
                current_texts.append(text)

        # 마지막 화자 발언 추가
        if current_speaker and current_texts:
            lines.append(f"[{current_speaker}] {' '.join(current_texts)}")

        return '\n\n'.join(lines)

    except Exception as e:
        print(f"⚠️  응답 파싱 중 오류: {e}")
        # 파싱 실패 시 원본 텍스트 반환
        if hasattr(response, 'text'):
            return response.text
        return str(response)


def transcribe_single_file(audio_path: Path, client=None, language: str = "ko",
                          timestamp: bool = False, model: str = "whisper-1",
                          diarize: bool = False) -> str:
    """
    단일 오디오 파일을 텍스트로 변환

    Args:
        audio_path: 오디오 파일 경로
        client: OpenAI 클라이언트 (None이면 새로 생성)
        language: 언어 코드
        timestamp: 타임스탬프 포함 여부
        model: Whisper 모델
        diarize: 화자분리 사용 여부 (True면 gpt-4o-transcribe-diarize 모델 사용)

    Returns:
        변환된 텍스트 (실패 시 빈 문자열)
    """
    # 화자분리 모드면 전용 함수 사용
    if diarize:
        return transcribe_with_diarization(audio_path, client, language)

    # API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
        return ""

    try:
        # OpenAI 클라이언트 초기화
        if client is None:
            client = OpenAI(api_key=api_key)

        # 오디오 파일 열기
        with open(audio_path, "rb") as audio:
            # Whisper API 호출
            if timestamp:
                response = client.audio.transcriptions.create(
                    model=model,
                    file=audio,
                    language=language if language != "auto" else None,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )
                # 타임스탬프 포함 텍스트 생성
                text = ""
                for segment in response.segments:
                    start_time = format_timestamp(segment['start'])
                    text += f"[{start_time}] {segment['text']}\n"
            else:
                response = client.audio.transcriptions.create(
                    model=model,
                    file=audio,
                    language=language if language != "auto" else None,
                    response_format="text"
                )
                text = response

        return text

    except Exception as e:
        print(f"❌ STT 실패: {e}")
        return ""

def transcribe_audio(audio_path: str, output_path: str = None, language: str = "ko",
                     timestamp: bool = False, model: str = "whisper-1", force: bool = False,
                     diarize: bool = False) -> bool:
    """
    오디오 파일을 텍스트로 변환

    Args:
        audio_path: 오디오 파일 경로
        output_path: 출력 텍스트 파일 경로 (None이면 자동 생성)
        language: 언어 코드 (ko, en, auto 등)
        timestamp: 타임스탬프 포함 여부
        model: Whisper 모델 (기본: whisper-1)
        force: 강제 실행 (대화형 확인 건너뛰기)
        diarize: 화자분리 사용 여부 (gpt-4o-transcribe-diarize 모델 사용)

    Returns:
        성공 여부
    """
    audio_file = Path(audio_path)

    # 파일 존재 확인
    if not audio_file.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {audio_path}")
        return False

    # 출력 파일 경로 설정
    if output_path is None:
        output_path = audio_file.with_suffix('.txt')

    output_file = Path(output_path)

    # 파일 크기 확인 (25MB 제한)
    file_size_mb = audio_file.stat().st_size / (1024 * 1024)

    # 25MB 초과 시 자동 분할
    if file_size_mb > 25:
        print(f"⚠️  파일 크기가 {file_size_mb:.1f}MB입니다. 25MB를 초과하여 자동 분할합니다.")
        chunk_files = split_audio_file(audio_file, chunk_size_mb=15)

        if not chunk_files:
            print("❌ 파일 분할에 실패했습니다.")
            return False

        # 각 청크를 변환하고 결과 병합
        all_text = ""
        temp_dir = chunk_files[0].parent

        try:
            for i, chunk_file in enumerate(chunk_files):
                print(f"\n🎤 청크 {i+1}/{len(chunk_files)} 변환 중...")
                chunk_text = transcribe_single_file(chunk_file, client=None, language=language,
                                                   timestamp=timestamp, model=model, diarize=diarize)
                if chunk_text:
                    all_text += chunk_text + "\n\n"
                else:
                    print(f"⚠️  청크 {i+1} 변환 실패, 계속 진행...")

            # 임시 파일 정리
            shutil.rmtree(temp_dir, ignore_errors=True)

            # 결과 저장
            if not all_text.strip():
                print("❌ 모든 청크 변환에 실패했습니다.")
                return False

            output_file.write_text(all_text, encoding='utf-8')
            print(f"\n✅ 분할 STT 완료!")
            print(f"📝 출력 파일: {output_file}")
            print(f"📊 텍스트 길이: {len(all_text):,} 글자")
            return True

        except Exception as e:
            print(f"❌ 분할 STT 실패: {e}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False

    # 25MB 이하 파일: 일반 처리
    print(f"🎤 STT 시작: {audio_file.name}")
    print(f"📏 파일 크기: {file_size_mb:.1f}MB")
    print(f"🌐 언어: {language}")
    if diarize:
        print(f"👥 화자분리: 활성화 (gpt-4o-transcribe-diarize)")

    text = transcribe_single_file(audio_file, client=None, language=language,
                                  timestamp=timestamp, model=model, diarize=diarize)

    if not text:
        print("❌ STT 실패")
        return False

    # 텍스트 파일로 저장
    output_file.write_text(text, encoding='utf-8')

    print(f"✅ STT 완료!")
    print(f"📝 출력 파일: {output_file}")
    print(f"📊 텍스트 길이: {len(text):,} 글자")

    return True


def format_timestamp(seconds: float) -> str:
    """초를 HH:MM:SS 형식으로 변환"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def main():
    parser = argparse.ArgumentParser(description="OpenAI Whisper API로 오디오 파일 STT")
    parser.add_argument("audio_file", help="오디오 파일 경로")
    parser.add_argument("-o", "--output", help="출력 텍스트 파일 경로")
    parser.add_argument("-l", "--language", default="ko", help="언어 코드 (ko, en, auto)")
    parser.add_argument("-t", "--timestamp", action="store_true", help="타임스탬프 포함")
    parser.add_argument("-m", "--model", default="whisper-1", help="Whisper 모델")
    parser.add_argument("-f", "--force", action="store_true", help="강제 실행 (대화형 확인 건너뛰기)")
    parser.add_argument("-d", "--diarize", action="store_true",
                        help="화자분리 활성화 (gpt-4o-transcribe-diarize 모델 사용)")

    args = parser.parse_args()

    success = transcribe_audio(
        args.audio_file,
        args.output,
        args.language,
        args.timestamp,
        args.model,
        args.force,
        args.diarize
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
