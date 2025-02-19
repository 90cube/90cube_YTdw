import gradio as gr
import os
from urllib.parse import unquote
import re
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError  # yt-dlp DownloadError 예외 클래스 임포트

def download_video_gradio_optimized(youtube_url, output_dir="."):
    """
    YouTube Downloader GUI (Gradio + yt-dlp) - 최적화 버전
    """
    print("[INFO] 다운로드 요청 수신...")
    if not youtube_url:
        error_message = "[ERROR] 유효하지 않은 URL 입력: YouTube 링크를 입력하세요."
        print(error_message)
        return error_message

    # URL 디코딩 (URL 인코딩된 문자 -> 사람이 읽을 수 있는 문자)
    youtube_url = unquote(youtube_url)
    print(f"[INFO] 디코딩된 URL: {youtube_url}")

    # URL 정규화 (http:// 또는 https:// 로 시작하도록, 올바른 YouTube URL 형식으로 변환)
    if not youtube_url.startswith('http'):
        youtube_url = 'https://' + youtube_url

    # video ID 추출 (URL에서 video ID 부분을 추출하여 YouTube 시청 URL 형태로 재구성)
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_url)
    if video_id_match:
        video_id = video_id_match.group(1)
        youtube_url = f'https://www.youtube.com/watch?v={video_id}'

    print(f"[INFO] 정규화된 YouTube URL: {youtube_url}")

    # 저장 경로 처리 (output_dir 인자 유효성 검사 및 폴더 생성)
    if output_dir and output_dir.strip():
        output_dir = os.path.abspath(output_dir) # 절대 경로로 변환
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir) # 폴더 생성 시도
                print(f"[INFO] 저장 경로 생성 완료: {output_dir}")
            except Exception as e:
                error_message = f"[ERROR] 저장 경로 생성 실패: {e}"
                print(error_message)
                return error_message
    else:
        output_dir = "." # 기본 저장 경로: 현재 폴더

    try:
        print("[INFO] yt-dlp를 사용하여 다운로드 시작...")
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best', # 최고 화질 비디오+오디오 또는 최고 화질
            'outtmpl': f"{output_dir}/%(title)s.%(ext)s", # 저장 템플릿: 제목.확장자
            'noplaylist': True, # 플레이리스트 다운로드 비활성화 (단일 영상만)
            'progress_hooks': [], # 다운로드 진행 상황 후크 (현재는 비어 있음, 향후 구현 가능)
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url]) # yt-dlp 다운로드 실행

        success_message = "[SUCCESS] 다운로드 완료!"
        print(success_message)
        return success_message

    except DownloadError as e: # yt-dlp DownloadError 예외 처리 (다운로드 실패)
        error_message = str(e)
        print(f"[ERROR] yt-dlp 다운로드 오류 발생: {error_message}")
        if "HTTP Error 403" in error_message:
            return f"다운로드 실패: HTTP Error 403 Forbidden (유튜브 서버가 다운로드를 거부했습니다. 😭 영상, 채널, 또는 유튜브 정책 문제일 수 있습니다. 다른 영상이나 채널을 시도해 보세요.)" # HTTP 403 오류 안내 메시지
        elif "Video unavailable" in error_message:
            return "다운로드 실패: Video unavailable (😭 영상이 존재하지 않거나 비공개 영상입니다.)" # 영상 없음 오류 안내 메시지
        elif "Age-restricted video" in error_message:
            return "다운로드 실패: Age-restricted video (🔞 연령 제한 영상입니다. 😥 로그인이 필요하거나, 성인 인증이 필요할 수 있습니다. yt-dlp 설정 또는 우회 방법을 알아보세요.)" # 연령 제한 오류 안내 메시지
        else:
            return f"다운로드 실패: {error_message}" # 기타 yt-dlp 오류 메시지 그대로 반환

    except Exception as e: # 예상치 못한 예외 처리 (프로그램 오류)
        error_message = f"[ERROR] 예상치 못한 프로그램 오류 발생: {e}"
        print(error_message)
        return f"다운로드 오류: 예상치 못한 오류가 발생했습니다. 😥 오류 내용을 확인하고, 다시 시도해 주세요. \n\n오류 정보: {e}" # 포괄적인 오류 안내 메시지


iface = gr.Interface(
    fn=download_video_gradio_optimized, # 최적화된 다운로드 함수 사용
    inputs=[
        gr.Textbox(label="YouTube 링크", placeholder="다운로드할 유튜브 영상 주소를 입력하세요"),
        gr.Textbox(label="저장 위치 (선택 사항)", placeholder="다운로드 폴더 경로를 입력하세요 (예: ./Downloads)")
    ],
    outputs=gr.Textbox(label="결과 메시지"),
    title="YouTube Downloader GUI (최적 버전)", # GUI 제목 변경
    description="""
    ## YouTube Downloader GUI (최적 버전 - yt-dlp 기반)

    유튜브 영상 링크를 입력하고 "Submit" 버튼을 누르면, 최고 화질의 MP4 파일로 다운로드됩니다. 🚀

    **주요 기능:**
    - yt-dlp 엔진 사용: 최신 유튜브 변화에 빠르게 대응, 강력한 다운로드 성능 💪
    - 다양한 오류 처리: 다운로드 실패 시 친절한 안내 메시지 제공 😊
    - URL 자동 정규화: 다양한 형태의 YouTube 링크 지원 🔗
    - 저장 위치 설정: 다운로드 폴더를 자유롭게 지정 가능 📁

    **주의 사항:**
    - YouTube 정책 변경으로 인해 다운로드가 안 될 수 있습니다. 😥
    - 개인적인 용도로만 사용하시고, 저작권 침해에 유의하세요. ⚠️
    """, # GUI 설명 개선 (기능, 주의사항 강조, Markdown 형식 적용)
    examples=[
        ["https://www.youtube.com/watch?v=dQw4w9WgXcQ", "./Downloads"], # 예시 URL 및 저장 경로 추가
        ["https://youtu.be/abcdefg123", ""], # 짧은 URL 예시
        ["youtube.com/watch?v=xyz7890ABC", "."], # 도메인 생략 URL 예시
    ], # 예시 입력 추가
    cache_examples=False, # examples 캐싱 비활성화 (필요에 따라 활성화 가능)
)

if __name__ == "__main__":
    print("[INFO] Gradio 인터페이스 실행 준비 완료...")
    print("[INFO] Gradio 인터페이스 실행 중... (웹 브라우저를 열고 GUI를 시작합니다.)")
    iface.launch() # Gradio GUI 실행
    print("[INFO] Gradio 인터페이스 실행 종료.")