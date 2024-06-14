import gradio as gr
import torch
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler

model_id = "stabilityai/stable-diffusion-2-base"
scheduler = EulerDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")
pipe = StableDiffusionPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16)

lora_path = "Jl-wei/ui-diffuser-v2"
pipe.load_lora_weights(lora_path)
pipe.to("cuda")


def gui_generation(text, num_imgs):
    prompt = f"Mobile app: {text}"
    images = pipe(prompt, num_inference_steps=30, guidance_scale=7.5, height=512, width=288, num_images_per_prompt=num_imgs).images
    yield images

with gr.Blocks() as demo:
    gallery = gr.Gallery(columns=[3], rows=[1], object_fit="contain", height="auto")
    number_slider = gr.Slider(1, 30, value=2, step=1, label="Batch size")
    prompt_box = gr.Textbox(label="Prompt", placeholder="Health monittoring report")
    gr.Interface(gui_generation, inputs=[prompt_box, number_slider], outputs=gallery)

if __name__ == "__main__":
    demo.launch()
