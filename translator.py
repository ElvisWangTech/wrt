import whisper
import sys
import time
from message import SN_TYPE, SN

N_SAMPLES = 480000

def translate(file_path: str, handleMessage = print):
    try:
        handleMessage(SN(text="start translate...", type=SN_TYPE.processing))
        model = whisper.load_model("base")
        audio = whisper.load_audio(file_path)
        audio_size = len(audio)
        index = 0

        while True:
            if index >= audio_size:
                break
            audio_fragment = whisper.pad_or_trim(audio[index:])
            mel = whisper.log_mel_spectrogram(audio_fragment).to(model.device)

            # detect the spoken language
            _, probs = model.detect_language(mel)
            handleMessage(SN(text = f"Detected language: {max(probs, key=probs.get)}", type=SN_TYPE.keyInfo))

            # decode the audio
            options = whisper.DecodingOptions(fp16=False)
            result = whisper.decode(model, mel, options)

            # print the recognized text
            handleMessage(SN(text = result.text, type=SN_TYPE.dataGenerated))

            index += N_SAMPLES

            time.sleep(0.1)
            
        handleMessage(SN(text="finished", type=SN_TYPE.finished))
    except Exception as e:
        handleMessage(SN(text="Error" + str(e), type=SN_TYPE.error))

if __name__ == '__main__':
    # print("test", sys.argv)
    local_media_file_path = "C:/Users/yiwei/Documents/cz.mp4"
    if len(sys.argv) > 1:
        local_media_file_path = sys.argv[1]
    translate(local_media_file_path)