from diffusers import(
    StableDiffusionPipeline,
    StableDiffusionImg2ImgPipeline,
    StableDiffusionInpaintPipeline
)
from img_utils import make_gif, img2bytes
import PIL as pil
import torch
import asyncio
import io

def txt2img(prompt: str) -> io.BytesIO:
    model_id = 'runwayml/stable-diffusion-v1-5'
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to("cuda")
    image = pipe(prompt, 512, 512, 50).images[0]
    return img2bytes(image)

async def txt2img_async(prompt: str) -> io.BytesIO:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, txt2img, prompt)

def txt2gif(prompt: str) -> tuple[io.BytesIO, io.BytesIO]:
    model_id = 'runwayml/stable-diffusion-v1-5'
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to("cuda")
    images = []

    def save_decoded_latent(step: int, timestep: int, tensor: torch.FloatTensor):
        images.append(pipe.numpy_to_pil(pipe.decode_latents(tensor))[0])

    pipe(prompt, 512, 512, 50, callback=save_decoded_latent, callback_steps=5)
    return make_gif(images), img2bytes(images[-1])

async def txt2gif_async(prompt: str) -> tuple[io.BytesIO, io.BytesIO]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, txt2gif, prompt)
