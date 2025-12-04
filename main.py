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
temperature = float(getenv('temperature', '0.7'))

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
    await message.reply(response['message']['content'].lower())

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
    await message.reply(response['message']['content'].lower())

async def main():
    await dp.start_polling(Bot(token=getenv('apikey')))

if __name__ == "__main__":
    run(main())
