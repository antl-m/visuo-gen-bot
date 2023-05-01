import logging
import asyncio
import aiogram

from os import getenv
from io import BytesIO
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, BotCommand
from visuo_gen import txt2img_async, txt2gif_async


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

class BotState(StatesGroup):
    txt2img_prompt_wait = State()
    txt2gif_prompt_wait = State()
    generation_in_progress = State()

async def txt2img_handler(message: Message):
    await message.answer('Input prompt')
    await BotState.txt2img_prompt_wait.set()

async def txt2img_prompt_handler(message: Message, state: aiogram.dispatcher.FSMContext):
    try:
        await BotState.generation_in_progress.set()
        await message.answer('Ok, image generation in progress')
        image = await txt2img_async(message.text) 
        bytes = BytesIO()
        image.save(bytes, 'JPEG')
        bytes.seek(0)
        await message.answer_photo(bytes)
    except:
        await message.answer(f'Error occured during generation, try later')
    finally:
        await state.reset_state()

async def txt2gif_handler(message: Message):
    await message.answer('Input prompt')
    await BotState.txt2gif_prompt_wait.set()

async def txt2gif_prompt_handler(message: Message, state: aiogram.dispatcher.FSMContext):
    try:
        await BotState.generation_in_progress.set()
        await message.answer('Ok, animation generation in progress')
        buf, img = await txt2gif_async(message.text)

        bytes = BytesIO()
        img.save(bytes, 'JPEG')
        bytes.seek(0)
        await message.answer_photo(bytes)

        buf.name = 'image.gif'
        buf.seek(0)
        await message.answer_animation(buf)
    except Exception as ex:
        await message.answer(f'Error occured during generation, try later:\n{str(ex)}')
    finally:
        await state.reset_state()
    
async def wait_handler(message: Message):
    await message.answer("Generation in progress, please wait")

async def main():
    bot = aiogram.Bot(getenv("BOT_TOKEN"))
    await bot.set_my_commands([
        BotCommand('txt2img', 'Generate image from text'),
        BotCommand('txt2gif', 'Create gif of image generation progress'),
    ])

    storage = MemoryStorage()
    dispatcher = aiogram.Dispatcher(bot, storage = storage)
    
    dispatcher.register_message_handler(txt2img_handler, commands=['txt2img'])
    dispatcher.register_message_handler(txt2img_prompt_handler,
                                        state=BotState.txt2img_prompt_wait,
                                        content_types=aiogram.types.ContentType.TEXT)
    
    dispatcher.register_message_handler(txt2gif_handler, commands=['txt2gif'])
    dispatcher.register_message_handler(txt2gif_prompt_handler,
                                        state=BotState.txt2gif_prompt_wait,
                                        content_types=aiogram.types.ContentType.TEXT)
    
    dispatcher.register_message_handler(wait_handler, state=BotState.generation_in_progress)

    await dispatcher.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
