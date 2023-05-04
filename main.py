import logging
import asyncio
import aiogram

from os import getenv

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, BotCommand
from aiogram import executor

from visuo_gen import txt2img_async, txt2gif_async

logging.basicConfig(level=logging.INFO)

bot = aiogram.Bot(getenv("BOT_TOKEN"))
storage = MemoryStorage()
dp = aiogram.Dispatcher(bot, storage=storage)

class BotState(StatesGroup):
    txt2img_prompt_wait = State()
    txt2gif_prompt_wait = State()
    generation_in_progress = State()

@dp.message_handler(commands=['txt2img'])
async def txt2img_handler(message: Message):
    await message.answer('Input prompt')
    await BotState.txt2img_prompt_wait.set()

@dp.message_handler(state=BotState.txt2img_prompt_wait, content_types=aiogram.types.ContentType.TEXT)
async def txt2img_prompt_handler(message: Message, state: FSMContext):
    try:
        await BotState.generation_in_progress.set()
        await message.answer('Ok, image generation in progress')
        await message.answer_photo(await txt2img_async(message.text))
    except:
        await message.answer(f'Error occured during generation, try later')
    finally:
        await state.reset_state()

@dp.message_handler(commands=['txt2gif'])
async def txt2gif_handler(message: Message):
    await message.answer('Input prompt')
    await BotState.txt2gif_prompt_wait.set()

@dp.message_handler(state=BotState.txt2gif_prompt_wait, content_types=aiogram.types.ContentType.TEXT)
async def txt2gif_prompt_handler(message: Message, state: FSMContext):
    try:
        await BotState.generation_in_progress.set()
        await message.answer('Ok, animation generation in progress')
        gif, img = await txt2gif_async(message.text)
        await message.answer_photo(img)
        await message.answer_animation(gif)
    except Exception as ex:
        await message.answer(f'Error occured during generation, try later:\n{str(ex)}')
    finally:
        await state.reset_state()
    
@dp.message_handler(state=BotState.generation_in_progress)
async def wait_handler(message: Message):
    await message.answer("Generation in progress, please wait")

async def set_commands():
    await bot.set_my_commands([
        BotCommand('txt2img', 'Generate image from text'),
        BotCommand('txt2gif', 'Create gif of image generation progress'),
    ])

if __name__ == '__main__':
    executor.start(dp, set_commands())
    executor.start_polling(dp, skip_updates=True)
