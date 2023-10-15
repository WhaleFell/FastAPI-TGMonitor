#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   func.py
@Time    :   2023/10/12 11:01:28
@Author  :   WhaleFall
@License :   (C)Copyright 2020-2023, WhaleFall
@Desc    :   数据库的一些小函数
"""

from datetime import datetime, timedelta
from sqlalchemy import event


def getBeijingTime() -> datetime:
    """获取北京时间"""
    utc_now = datetime.utcnow()  # 获取当前UTC时间
    beijing_offset = timedelta(hours=8)  # 北京时间比UTC时间早8小时
    beijing_now = utc_now + beijing_offset  # 将偏移量加到当前时间上
    return beijing_now
