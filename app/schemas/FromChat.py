#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   FromChat.py
@Time    :   2023/10/13 01:35:56
@Author  :   WhaleFall
@License :   (C)Copyright 2020-2023, WhaleFall
@Desc    :   schemas/FromChat.py 群组模型文件
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, List
from pydantic import ConfigDict
from datetime import datetime


class FromChatModel(BaseModel):
    from_chat_id: str = Field(description="群组ID")
    name: Optional[str] = Field(description="群名字", default="NotFound")
    chat_type: str = Field(description="群类型")
    description: Optional[str] = Field(
        description="群描述", default="empty description"
    )
    create_time: datetime = Field(description="录入系统时间")
    last_msg_time: datetime = Field(description="最近消息时间")

    model_config = ConfigDict(from_attributes=True)
