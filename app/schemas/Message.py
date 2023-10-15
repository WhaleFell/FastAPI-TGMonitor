#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   Message.py
@Time    :   2023/10/12 11:21:19
@Author  :   WhaleFall
@License :   (C)Copyright 2020-2023, WhaleFall
@Desc    :   schemas/Message.py 消息 BaseModel 模型
"""


from pydantic import BaseModel, Field
from typing import Optional, Any, List
from pydantic import ConfigDict
from datetime import datetime


class MessageModel(BaseModel):
    tg_id: str = Field(description="tg唯一ID")
    username: Optional[str] = Field(description="用户名可选")
    from_chat_id: str = Field(description="来源信息 ID")
    content: str = Field(description="信息内容")
    msg_time: datetime = Field(description="信息时间")

    model_config = ConfigDict(from_attributes=True)


class MessagePagination(BaseModel):
    """信息分页查询"""

    total: int  # 总条数
    page: int  # 当前页数
    size: int  # 当前条数
    pages: int  # 总页数

    data: List[MessageModel]
