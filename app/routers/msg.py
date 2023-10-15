#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   msg.py
@Time    :   2023/10/12 17:23:00
@Author  :   WhaleFall
@License :   (C)Copyright 2020-2023, WhaleFall
@Desc    :   routers/msg.py 信息路由
"""


from fastapi import APIRouter, Query, Depends
from app.schemas import BaseResp
from app.schemas.Message import MessagePagination, MessageModel

from app.database.connect import AsyncSession, get_session
from app.database.crud import getMsgCount, queryMsg


from typing_extensions import Annotated
from typing import Optional

import math

router = APIRouter()


# sqlalchemy pagination limit/offset
@router.get("/views/")
async def msg_views(
    from_chat_id: Annotated[str, Query(description="来源群的 ID")],
    db: Annotated[AsyncSession, Depends(get_session)],
    page: Annotated[int, Query(description="第几页")],
    size: Annotated[int, Query(description="一页的数据量")],
    tg_id: Annotated[Optional[str], Query(description="指定的用户ID")] = None,
    keyword: Annotated[Optional[str], Query(description="指定内容的关键词")] = None,
) -> MessagePagination:
    """信息分页查询"""
    offset = (page - 1) * size  # 偏移量

    msgs = await queryMsg(
        session=db,
        from_chat_id=from_chat_id,
        offset=offset,
        limit=size,
        tg_id=tg_id,
        keyword=keyword,
    )

    # 处理 async session 时的 relationship 查询存在隐性同步的 IO
    # https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession

    msgModels = []
    for msg in msgs[1]:
        from_user = await msg.awaitable_attrs.from_user
        msgModel = MessageModel(
            tg_id=msg.tg_id,
            username=from_user.username,
            from_chat_id=msg.from_chat_id,
            content=msg.content,
            msg_time=msg.msg_time,
        )
        msgModels.append(msgModel)

    total = msgs[0]
    pages = math.ceil(total / size)  # 总页数

    return MessagePagination(
        total=total, page=page, size=size, pages=pages, data=msgModels
    )
