from asyncio import run
from aiogram import types, Bot, Dispatcher
from aiogram.filters.command import Command
from os import getenv
from dotenv import load_dotenv; load_dotenv()

import logging
logging.basicConfig(level = logging.INFO)

from random import randint

probability = int(getenv('probability'))
chatid = int(getenv('chat'))
seed = randint(1, probability)
model = getenv('model')
temperature = float(getenv('temperature'))

from ollama import chat
from ollama import ChatResponse

dp = Dispatcher()

@dp.message(Command("ask"))
async def ask(message: types.Message): 
    if message.chat.id != chatid: return
    response: ChatResponse = chat(model=model, messages=[
    {
        'role': 'user',
        'content': message.text[5:],
    }], options={'temperature': temperature})
    text = response['message']['content'].lower()
    if len(text) < 2000:
        await message.reply(text)
    else:
        stext = [text[i:i+2000] for i in range(0, len(text), 2000)]
        for i in stext:
            await message.reply(i)

@dp.message()
async def message(message: types.Message):
    if message.chat.id != chatid: return
    if message.text == None: return
    if '@holinimbot' not in message.text:
        if randint(1, probability) != seed: return
    response: ChatResponse = chat(model=model, messages=[
    {
        'role': 'user',
        'content': message.text,
    }], options={'temperature': temperature})
    text = response['message']['content'].lower()
    if len(text) < 2000:
        await message.reply(text)
    else:
        stext = [text[i:i+2000] for i in range(0, len(text), 2000)]
        for i in stext:
            await message.reply(i)

async def main():
    await dp.start_polling(Bot(token=getenv('apikey')))

if __name__ == "__main__":
    run(main())
