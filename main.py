from asyncio import run, to_thread
from os import getenv
import logging
import re
from random import randint

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ChatAction
from aiogram.filters.command import Command
from dotenv import load_dotenv
from ollama import chat
from ollama import ChatResponse

load_dotenv()
logging.basicConfig(level=logging.INFO)

probability = int(getenv("probability"))
chatid = int(getenv("chat"))
seed = randint(1, probability)
model = getenv("model")
temperature = float(getenv("temperature"))

proxy = getenv("proxy", None)

if proxy:
    from aiogram.client.session.aiohttp import AiohttpSession
    session = AiohttpSession(proxy=proxy)
    bot = Bot(token=getenv("apikey"), session=session)
else:
    bot = Bot(token=getenv("apikey"))

dp = Dispatcher()
conversation_context: list[dict[str, str]] = []
bot_username: str | None = None
bot_id: int | None = None


async def generate_response(messages: list[dict[str, str]]) -> str:
    response: ChatResponse = await to_thread(
        chat,
        model=model,
        messages=messages,
        options={"temperature": temperature},
    )
    return response["message"]["content"].strip()


def split_long_text(text: str) -> list[str]:
    return [text[i : i + 2000] for i in range(0, len(text), 2000)]


def append_user_message(content: str) -> list[dict[str, str]]:
    conversation_context.append({"role": "user", "content": content})
    return conversation_context


def append_assistant_message(content: str) -> None:
    conversation_context.append({"role": "assistant", "content": content})


@dp.message(Command(commands=["clear"]))
async def clear_context(message: types.Message):
    if message.chat.id != chatid:
        return
    conversation_context.clear()
    await message.reply("context cleared 🧹")


@dp.message(Command(commands=["ask"]))
async def ask(message: types.Message):
    if message.chat.id != chatid:
        return

    prompt = message.text.removeprefix("/ask").strip()
    if not prompt:
        await message.reply("no prompt 😮")
        return

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    messages = append_user_message(prompt)
    text = await generate_response(messages)

    if not text:
        await message.reply("no response 😮")
        return

    append_assistant_message(text)
    for chunk in split_long_text(text):
        await message.reply(chunk)


@dp.message()
async def message_handler(message: types.Message):
    if message.chat.id != chatid:
        return
    if not message.text:
        return

    mention_text = f"@{bot_username}" if bot_username else ""
    is_mention = mention_text and mention_text.lower() in message.text.lower()
    is_reply = bool(
        message.reply_to_message
        and message.reply_to_message.from_user
        and bot_id is not None
        and message.reply_to_message.from_user.id == bot_id
    )

    if not is_mention and not is_reply:
        if randint(1, probability) != seed:
            return

    user_text = message.text
    if is_mention:
        user_text = re.sub(re.escape(mention_text), "", user_text, flags=re.IGNORECASE).strip()

    if not user_text:
        await message.reply("no prompt 😮")
        return

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    messages = append_user_message(user_text)
    text = await generate_response(messages)

    if not text:
        await message.reply("no response 😮")
        return

    append_assistant_message(text)
    for chunk in split_long_text(text):
        await message.reply(chunk)


async def main():
    global bot_username, bot_id
    me = await bot.get_me()
    bot_username = me.username or ""
    bot_id = me.id
    await dp.start_polling(bot)


if __name__ == "__main__":
    run(main())
