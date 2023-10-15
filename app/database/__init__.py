#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   __init__.py
@Time    :   2023/10/12 10:33:16
@Author  :   WhaleFall
@License :   (C)Copyright 2020-2023, WhaleFall
@Desc    :   database lib
"""

from .connect import async_engine, AsyncSessionMaker
from app.utils import logger
from .models import Base


async def init_table(is_drop: bool = False):
    """创建 database 下的所有表"""
    if is_drop:
        await drop_table()
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("创建表成功!!!")
    except Exception as e:
        logger.error(f"创建表失败!!! -- 错误信息如下:\n{e}")


async def drop_table():
    """删除 database 下的所有表"""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("删除表成功!!!")
    except Exception as e:
        logger.error(f"删除表失败!!! -- 错误信息如下:\n{e}")
