import gradio as gr
from gradio_iframe import iFrame
from llm_gen import html_generation, html_edit


def gui_generation(prompt, temperature, html_file):
    if html_file:
        _, file_path = html_edit(prompt, open(html_file, "r").read(), temperature)
    else:
        _, file_path = html_generation(prompt, temperature)
        
    html_code = f"""<iframe height="667" width="375" src="file={file_path}"></iframe>"""
    yield html_code


with gr.Blocks() as demo:
    html_file = gr.File(label="HTML to edit")
    temp_slider = gr.Slider(0, 2, value=1, step=0.01, label="Temperature")
    prompt_box = gr.Textbox(label="Prompt", placeholder="Health monitoring report")
    gr.Interface(
        fn=gui_generation,
        inputs=[prompt_box, temp_slider, html_file],
        outputs=iFrame()
    )

if __name__ == '__main__':
    demo.launch(allowed_paths=["./output", "./assets"])
