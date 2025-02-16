import gradio as gr
from pytube import YouTube
from pytube.exceptions import RegexMatchError, VideoUnavailable, LiveStreamError, AgeRestrictedError, PytubeError

def download_video_gradio(youtube_url, output_dir="."): # output_dir 파라미터 추가, 기본값 현재 디렉토리
    if not youtube_url:
        return "YouTube 링크를 입력하세요." # 오류 메시지 반환

    try:
        yt = YouTube(youtube_url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        if stream:
            download_path = output_dir  # 다운로드 경로 설정
            stream.download(output_path=download_path)
            return f"'{yt.title}' 다운로드 완료! (저장 위치: {download_path})" # 성공 메시지 반환
        else:
            return "프로그레시브 MP4 스트림을 찾을 수 없습니다." # 오류 메시지 반환

    except RegexMatchError:
        return "오류: 유효하지 않은 유튜브 URL입니다."
    except VideoUnavailable:
        return "오류: 영상이 더 이상 존재하지 않거나 비공개 영상입니다."
    except LiveStreamError:
        return "오류: 라이브 스트리밍 영상은 다운로드할 수 없습니다."
    except AgeRestrictedError:
        return "오류: 연령 제한 영상입니다. (pytube 자체적으로는 다운로드 어려움)"
    except PytubeError as e:
        return f"Pytube 오류 발생: {e}"
    except Exception as e:
        return f"예상치 못한 오류 발생: {e}"

iface = gr.Interface(
    fn=download_video_gradio, # 다운로드 기능을 수행할 함수
    inputs=[
        gr.Textbox(label="YouTube 링크", placeholder="다운로드할 유튜브 영상 주소를 입력하세요"), # 텍스트 입력 필드
        gr.Textbox(label="저장 위치 (선택 사항, 기본: 현재 폴더)", placeholder="다운로드 폴더 경로를 입력하세요 (예: ./Downloads)") # 저장 위치 입력 필드 추가
    ],
    outputs=gr.Textbox(label="결과 메시지"), # 결과 메시지 출력
    title="YouTube Downloader GUI (Gradio)",
    description="유튜브 영상 링크를 입력하고 다운로드 버튼을 누르세요. 최고 화질의 MP4 파일로 다운로드됩니다.",
)

if __name__ == "__main__":
    iface.launch()