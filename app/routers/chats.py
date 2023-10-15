#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   chats.py
@Time    :   2023/10/13 01:41:59
@Author  :   WhaleFall
@License :   (C)Copyright 2020-2023, WhaleFall
@Desc    :   router/chats.py 录入系统的群聊详细
"""
from fastapi import APIRouter, Query, Depends
from app.schemas import BaseResp
from app.schemas.FromChat import FromChatModel

from app.database.connect import AsyncSession, get_session
from app.database.crud import getMonitingChat


from typing_extensions import Annotated
from typing import Optional, List

router = APIRouter()


# sqlalchemy pagination limit/offset
@router.get("/all/")
async def list_chats(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> List[FromChatModel]:
    fromchats = await getMonitingChat(session=db)

    return [FromChatModel.model_validate(fromchat) for fromchat in fromchats]
