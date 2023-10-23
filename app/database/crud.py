#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   crud.py
@Time    :   2023/10/12 14:56:14
@Author  :   WhaleFall
@License :   (C)Copyright 2020-2023, WhaleFall
@Desc    :   database/crud.py 数据库增删改查
"""

from sqlalchemy.ext.asyncio import AsyncSession

from pyrogram.types import Message as TGMessage
from pyrogram.types import Chat as TGChat
from pyrogram.types import User as TGUser

from .models import Msg, Fromchat, User
from app.schemas.Message import MessageModel
from app.utils import logger

from typing import Optional, List, Sequence, Tuple, Any

from sqlalchemy import (
    ForeignKey,
    func,
    select,
    update,
    String,
    DateTime,
    Integer,
    Float,
    Boolean,
    desc,
    Select,
    text,
)


def handleUserName(tgchat: TGUser) -> str:
    """处理User 对象名字"""
    last_name = ""
    first_name = ""
    username = ""

    if tgchat.last_name:
        last_name = tgchat.last_name
    if tgchat.first_name:
        first_name = tgchat.first_name
    if tgchat.username:
        username = tgchat.username

    return f"@{username}({first_name}{last_name})"


def handleMsgContent(tgmsg: TGMessage) -> str:
    """处理 messgae 的内容"""
    if tgmsg.text:
        return tgmsg.text
    else:
        return f"[{str(tgmsg.media)}]"


async def newChat(session: AsyncSession, tgchat: TGChat) -> Fromchat:
    """新建一个聊天信息"""
    result = await session.get(Fromchat, str(tgchat.id))
    if result:
        return result

    chat = Fromchat(
        from_chat_id=str(tgchat.id),
        name=tgchat.title,
        chat_type=f"{str(tgchat.type)}",
        description=f"{str(tgchat.description)}",
    )

    session.add(chat)
    await session.commit()
    await session.refresh(chat)

    return chat


async def checkChatExist(
    session: AsyncSession, TGmsg: TGMessage
) -> Optional[Fromchat]:
    """检查对应的群聊信息是否存在 并更新最新信息"""
    result = await session.execute(
        select(Fromchat).where(Fromchat.from_chat_id == str(TGmsg.chat.id))
    )
    chat = result.scalar_one_or_none()
    if not chat:
        return

    # update last_msg_time
    await session.execute(
        update(Fromchat).where(Fromchat.from_chat_id == TGmsg.chat.id)
    )
    await session.commit()
    await session.refresh(chat)

    return chat


async def searchUser(session: AsyncSession, tg_id: str) -> Optional[User]:
    """搜索用户是否存在"""
    result = await session.execute(select(User).where(User.tg_id == tg_id))

    return result.scalar_one_or_none()


async def newUser(session: AsyncSession, TGmsg: TGMessage) -> User:
    search = await searchUser(session, tg_id=str(TGmsg.from_user.id))
    if search:
        # TODO: update exist user username
        await session.execute(
            update(User)
            .where(User.tg_id == TGmsg.from_user.id)
            .values(username=handleUserName(TGmsg.from_user))
        )
        await session.commit()
        await session.refresh(search)
        return search

    user = User(
        tg_id=str(TGmsg.from_user.id), username=handleUserName(TGmsg.from_user)
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def newMsg(session: AsyncSession, TGmsg: TGMessage) -> Optional[Msg]:
    """新增的一条信息"""
    chat = await checkChatExist(session, TGmsg=TGmsg)
    if not chat:
        logger.error(f"chat id {TGmsg.chat.id} not found!")
        return

    user = await newUser(session, TGmsg=TGmsg)
    msg = Msg(
        from_chat_id=str(chat.from_chat_id),
        content=handleMsgContent(TGmsg),
        tg_id=user.tg_id,
    )
    session.add(msg)
    await session.commit()
    await session.refresh(msg)

    return msg


async def queryMsg(
    session: AsyncSession,
    from_chat_id: str,
    offset: int,
    limit: int,
    tg_id: Optional[str] = None,
    keyword: Optional[str] = None,
) -> Tuple[int, Sequence[Msg]]:
    """分页查询 msg 信息
    sqlalchemy pagination limit/offset
    Require:
        - from_chat_id: 来源的群聊 ID
        - offset: 偏移量
        - limit: 查询数
    Optional:
        - tg_id: 搜索指定用户
        - keyword: 模糊搜索指定内容
    """

    def gen_execute_count() -> str:
        sql = (
            f"SELECT COUNT(*) FROM msgs WHERE from_chat_id = '{from_chat_id}' "
        )
        if tg_id:
            sql += f"AND tg_id = '{tg_id}' "
        if keyword:
            sql += f"AND content LIKE '%{keyword}%';"
        return sql

    execute = (
        select(Msg)
        .where(Msg.from_chat_id == from_chat_id)
        .offset(offset)
        .order_by(desc(Msg.msg_time))
        .limit(limit)
    )
    if tg_id:
        execute = execute.where(Msg.tg_id == tg_id)
    if keyword:
        execute = execute.where(Msg.content.like(f"%{keyword}%"))

    count_result = await session.execute(text(gen_execute_count()))
    count = count_result.all()[0][0]

    result = await session.scalars(execute)

    return int(count), result.all()


async def getMsgCount(session: AsyncSession) -> int:
    """获取 msgs 表的信息数"""
    statement = select(func.count()).select_from(Msg)
    result = await session.execute(statement)

    return result.scalar()


async def getMonitingChat(session: AsyncSession) -> List[Fromchat]:
    """获取数据库中监听的群组"""
    result = await session.execute(select(Fromchat))

    return list(result.scalars().all())
