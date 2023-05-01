from diffusers import(
    StableDiffusionPipeline,
)
from PIL import Image
import torch
from torch import FloatTensor
import asyncio
import io

def create_gif_cb(pipe: StableDiffusionPipeline, images):
    def display_cb(step: int, timestep: int, tensor: FloatTensor):
        images.append(pipe.numpy_to_pil(pipe.decode_latents(tensor))[0])
    return display_cb

def txt2img(prompt: str) -> Image:
    model_id = 'runwayml/stable-diffusion-v1-5'
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to("cuda")
    image = pipe(prompt, 512, 512, 50).images[0]
    return image

def make_gif(images) -> io.BytesIO:
    buffer = io.BytesIO()
    images[0].save(buffer, format='GIF', save_all=True, optimize=True, append_images=images[1:], loop=0)
    return buffer

def txt2gif(prompt: str) -> io.BytesIO:
    model_id = 'runwayml/stable-diffusion-v1-5'
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to("cuda")
    images = []
    pipe(prompt, 512, 512, 50, callback=create_gif_cb(pipe, images))
    return make_gif(images)

async def txt2img_async(prompt: str) -> Image:
    loop = asyncio.get_running_loop()
    image = await loop.run_in_executor(None, txt2img, prompt)
    return image
    