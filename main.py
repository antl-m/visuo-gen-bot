import logging
import asyncio
import aiogram

from os import getenv
from io import BytesIO
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from visuo_gen import txt2img_async

from aiogram.types import (
    Message,
    BotCommand
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

class BotState(StatesGroup):
    waiting_for_prompt = State()
    generation_in_progress = State()

async def txt2img_handler(message: Message):
    await message.answer('Input prompt')
    await BotState.waiting_for_prompt.set()

async def prompt_handler(message: Message, state: aiogram.dispatcher.FSMContext):
    try:
        await BotState.generation_in_progress.set()
        await aiogram.types.ChatActions.upload_photo()
        image = await txt2img_async(message.text) 
        bytes = BytesIO()
        image.save(bytes, 'JPEG')
        bytes.seek(0)
        await message.answer_photo(bytes, message.text)
    except:
        await message.answer(f'Error occured during generation, try later')
    finally:
        await state.reset_state()

async def echo(message: Message):
    await message.answer(message.text)

async def main():
    bot = aiogram.Bot(getenv("BOT_TOKEN"))
    await bot.set_my_commands([
        BotCommand('txt2img', 'Generate image from text')
    ])

    storage = MemoryStorage()
    dispatcher = aiogram.Dispatcher(bot, storage = storage)
    dispatcher.register_message_handler(txt2img_handler, commands=['txt2img'])
    dispatcher.register_message_handler(prompt_handler,
                                        state=BotState.waiting_for_prompt,
                                        content_types=aiogram.types.ContentType.TEXT)
    dispatcher.register_message_handler(echo, state=BotState.generation_in_progress)

    await dispatcher.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
