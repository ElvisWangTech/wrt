import whisper
import sys
from message import SN_TYPE, SN

N_SAMPLES = 480000

model = None
audio_cache = {}


def translate(file_path: str, handle_message=print, progress_callback=print):
    '''
    translate voice to plaintext by whisper.
    If the audio duration exceeds 30 seconds, The audio will be split into segments in 30 seconds.

    file_path: audio or video file path.

    handle_message: handle some message while processing, default way is just to print it.

    progress_callback: handle progress 0 to 1, default way is just to print it.
    '''
    try:
        handle_message(SN(text="start translate...", type=SN_TYPE.processing))
        preloadModel()
        audio = preloadAudio(file_path)
        global model
        audio_size = len(audio)
        processed_size = 0

        while True:
            if processed_size >= audio_size:
                break
            audio_fragment = whisper.pad_or_trim(audio[processed_size:], N_SAMPLES)
            mel = whisper.log_mel_spectrogram(audio_fragment).to(model.device)

            # detect the spoken language
            _, probs = model.detect_language(mel)
            handle_message(SN(text=f"Detected language: {max(probs, key=probs.get)}", type=SN_TYPE.keyInfo))

            # decode the audio
            result = whisper.transcribe(model, audio_fragment, fp16=False)

            # print the recognized text
            segments_size = len(result['segments'])
            for idx, segment in enumerate(result['segments']):
                progress = round((processed_size + (N_SAMPLES * (1 + idx) / segments_size))/audio_size, 2)
                handle_message(SN(text=segment['text'], type=SN_TYPE.dataGenerated, progress=progress))
                progress_callback(progress)

            processed_size += N_SAMPLES

            # time.sleep(0.1)
        handle_message(SN(text="finished", type=SN_TYPE.finished))
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        handle_message(SN(text="Error" + str(e), type=SN_TYPE.error))


def preloadModel():
    global model
    if model is None:
        print("加载模型")
        model = whisper.load_model("small")


def preloadAudio(file_path: str, overload: bool = False):
    global audio_cache
    # target audio not cached or overload force
    audio = audio_cache.get(file_path)
    if overload or file_path not in audio_cache:
        print("加载文件到内存")
        audio = whisper.load_audio(file_path)
        audio_cache[file_path] = audio
    return audio


if __name__ == '__main__':
    # print("test", sys.argv)
    local_media_file_path = "C:/Users/yiwei/cz_126.mp4"
    if len(sys.argv) > 1:
        local_media_file_path = sys.argv[1]
    translate(local_media_file_path)
