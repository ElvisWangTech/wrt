# -*- coding: UTF-8 -*-

# from threading import Thread
import gradio as gr
import os
import io
from message import SN, SN_TYPE

from translator import translate

os.environ["no_proxy"] = "localhost,127.0.0.1,::1"

translate_out_io = None


def predict(video_in, audio_in_microphone, audio_in_file):
    if video_in is None and audio_in_microphone is None and audio_in_file is None:
        raise gr.Error("Please upload a video or audio.")
    if audio_in_microphone or audio_in_file:
        print("audio", audio_in_microphone, audio_in_file)
        audio = audio_in_microphone or audio_in_file
    elif video_in:
        audio = video_in
    # translateThread = Thread(target=translate, args=(audio, handle_message, handle_translated_progress,))
    # translateThread.start()
    global translate_out_io
    translate_out_io = io.StringIO()
    translate(audio, handle_message, progress_callback=handle_translated_progress)
    return translate_out_io.getvalue()


def toggle(choice):
    if choice == "upload" or choice == "microphone":
        return gr.update(visible=True, value=None), gr.update(visible=False, value=None)
    else:
        return gr.update(visible=False, value=None), gr.update(visible=True, value=None)


def handle_message(sn: SN):
    if sn.type == SN_TYPE.dataGenerated:
        print('translated text', sn.text)
        translate_out_io.write(sn.text)
        translate_out_io.write('\n')


def handle_translated_progress(progress: float):
    print('progress', progress)


with gr.Blocks() as blocks:
    gr.Markdown("### Choose your media.""")
    with gr.Tab("Video") as tab:
        with gr.Row():
            with gr.Column():
                video_or_file_opt = gr.Radio(["upload"], value="upload",
                                             label="How would you like to upload your video?")
                video_in = gr.Video(source="upload", include_audio=True)
                video_or_file_opt.change(fn=lambda s: gr.update(source=s, value=None), inputs=video_or_file_opt,
                                         outputs=video_in, queue=False, show_progress=False)
            with gr.Column():
                translate_out_com = gr.Textbox(lines=13)
        run_btn = gr.Button("Run")
        run_btn.click(fn=predict, inputs=[video_in], outputs=[translate_out_com], scroll_to_output=True)

    with gr.Tab("Audio"):
        with gr.Row():
            with gr.Column():
                audio_or_file_opt = gr.Radio(["microphone", "file"], value="microphone",
                                             label="How would you like to upload your audio?")
                audio_in_microphone = gr.Audio(source="microphone", type="filepath")
                audio_in_file = gr.Audio(
                    source="upload", visible=False, type="filepath")

                audio_or_file_opt.change(fn=toggle, inputs=[audio_or_file_opt],
                                         outputs=[audio_in_microphone, audio_in_file], queue=False, show_progress=False)
            with gr.Column():
                translate_out_com = gr.Textbox(lines=13)
        run_btn = gr.Button("Run")
        run_btn.click(fn=predict, inputs=[video_in, audio_in_microphone, audio_in_file],
                      outputs=[translate_out_com], scroll_to_output=True)


blocks.queue()
blocks.launch(share=True, show_error=True, debug=True, auth=("wyw", "wyw123"))
