# ====== pyrogram =======

from pyrogram import Client, idle, filters  # type:ignore
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    BotCommand,
    CallbackQuery,
)
from pyrogram.handlers import MessageHandler  # type:ignore
from pyrogram.enums import ParseMode

# ====== pyrogram end =====

# ====== APP Import =====
from app.config import settings

# sqlalchemy
from app.database import init_table
from app.database.crud import *
from app.database.connect import AsyncSessionMaker

# ====== APP Import End =====


from contextlib import closing, suppress
from typing import List, Union, Any, Optional
from pathlib import Path
import asyncio
from loguru import logger
import sys
import re
from functools import wraps
import os
import sys
import glob

# ====== Config ========
ROOTPATH: Path = Path(__file__).parent.absolute()
DEBUG = True
NAME = os.environ.get("NAME") or "session"
API_ID = 21341224
API_HASH = "2d910cf3998019516d6d4bbb53713f20"
SESSION_PATH: Path = Path(ROOTPATH, "sessions", f"{NAME}.txt")
# 需要监控的 群 ID
MONITOR_CHAT_ID: List[Union[str, int]] = [-1001616666972]
__desc__ = """
信息监控机器人正在运行中.....
"""
# ====== Config End ======

# ===== logger ====
from app.utils import logger

# ===== logger end =====

# ===== error handle =====


# ====== error handle end =========

# ====== Client maker =======


def makeClient(path: Path) -> Client:
    session_string = path.read_text(encoding="utf8")
    return Client(
        name=path.stem,
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=session_string,
        in_memory=True,
    )


app = makeClient(SESSION_PATH)

# ====== Client maker end =======

# ====== helper function  ====


# ====== helper function end ====

# ===== Handle ======


@app.on_message(
    filters=filters.command("start") & filters.private & ~filters.me
)
async def start(client: Client, message: Message):
    await message.reply_text(__desc__)


@app.on_message(filters=filters.chat(MONITOR_CHAT_ID))
async def handleMessage(client: Client, message: Message):
    """监听信息并入库"""
    async with AsyncSessionMaker() as session:
        msg = await newMsg(session=session, TGmsg=message)
        if not msg:
            return
        logger.info(
            f"Group ID:{msg.from_chat_id} User:{msg.tg_id} Time:{msg.msg_time} content:{msg.content}"
        )
        await session.commit()


# ==== Handle end =====


async def main():
    global app
    await app.start()
    user = await app.get_me()

    # ===== Test Code =======
    # chat_id = await app.get_chat("@w2ww2w2w")
    # print(chat_id)

    # ======== Test Code end ==========

    logger.success(
        f"""
-------login success--------
username: {user.first_name}
type: {"Bot" if user.is_bot else "User"}
@{user.username}
----------------------------
"""
    )
    await init_table()
    logger.info(f"Initialize monitor group:{MONITOR_CHAT_ID}")
    for chat_id in MONITOR_CHAT_ID:
        try:
            chat = await app.get_chat(chat_id)
            async with AsyncSessionMaker() as session:
                fromchat = await newChat(
                    session=session, tgchat=chat  # type:ignore
                )
                logger.success(
                    f"add {fromchat.name} {fromchat.description} {fromchat.create_time} !"
                )
        except Exception as exc:
            logger.error(f"not get the chat infomation: id:{chat_id} exc:{exc}")

    await idle()
    await app.stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    with closing(loop):
        with suppress(asyncio.exceptions.CancelledError):
            loop.run_until_complete(main())
        loop.run_until_complete(asyncio.sleep(3.0))  # task cancel wait 等待任务结束
    # asyncio.run(makeSessionString())
