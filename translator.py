import whisper
import sys
from message import SN_TYPE, SN

N_SAMPLES = 480000


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
        model = whisper.load_model("base")
        audio = whisper.load_audio(file_path)
        audio_size = len(audio)
        processed_size = 0

        while True:
            if processed_size >= audio_size:
                break
            audio_fragment = whisper.pad_or_trim(audio[processed_size:])
            mel = whisper.log_mel_spectrogram(audio_fragment).to(model.device)

            # detect the spoken language
            _, probs = model.detect_language(mel)
            handle_message(SN(text=f"Detected language: {max(probs, key=probs.get)}", type=SN_TYPE.keyInfo))

            # decode the audio
            options = whisper.DecodingOptions(fp16=False)
            result = whisper.decode(model, mel, options)

            # print the recognized text
            handle_message(SN(text=result.text, type=SN_TYPE.dataGenerated))

            processed_size += N_SAMPLES

            print(processed_size, audio_size)
            progress_callback(round(processed_size/audio_size, 2))

            # time.sleep(0.1)
        handle_message(SN(text="finished", type=SN_TYPE.finished))
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        handle_message(SN(text="Error" + str(e), type=SN_TYPE.error))


if __name__ == '__main__':
    # print("test", sys.argv)
    local_media_file_path = "C:/Users/yiwei/Documents/cz_126.mp4"
    if len(sys.argv) > 1:
        local_media_file_path = sys.argv[1]
    translate(local_media_file_path)
