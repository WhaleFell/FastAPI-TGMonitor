# curd/model.py
# 数据库模型

"""
参考文档:
    [1]: https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#declarative-mapping
    [2]: https://docs.sqlalchemy.org/en/20/orm/declarative_config.html#mapper-configuration-options-with-declarative
    [3]: https://docs.sqlalchemy.org/en/20/orm/declarative_mixins.html#composing-mapped-hierarchies-with-mixins
    [4]: https://docs.sqlalchemy.org/en/20/orm/declarative_config.html#other-declarative-mapping-directives
"""
import asyncio
from typing import List, Dict, Optional, Mapping, Type, TypeVar, Tuple
from typing_extensions import Annotated
from datetime import datetime, timedelta

# sqlalchemy type
import sqlalchemy.orm
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
)

from sqlalchemy.dialects.mysql import LONGTEXT

# sqlalchemy asynchronous support
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
)

# sqlalchemy ORM
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

from .func import getBeijingTime

# 主键 ID
# https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#mapping-whole-column-declarations-to-python-types
# 将整个列声明映射到 Python 类型
# 但目前尝试使用 Annotated 来指示 relationship() 的进一步参数以及类似的操作将在运行时引发 NotImplementedError 异常，但是可能会在未来的版本中实现。
IDPK = Annotated[
    int,
    mapped_column(primary_key=True, autoincrement=True, comment="ID主键"),
]

# 处理 async session 时的 relationship 查询存在隐性同步的 IO
# https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession


class Base(AsyncAttrs, DeclarativeBase):
    """ORM 基类 | 详见[1]、[3]"""

    __table_args__ = {
        "mysql_engine": "InnoDB",  # MySQL引擎
        "mysql_charset": "utf8mb4",  # 设置表的字符集
        "mysql_collate": "utf8mb4_general_ci",  # 设置表的校对集
    }


class Msg(Base):
    __tablename__ = "msgs"
    __table_args__ = {"comment": "消息表"}

    # 数据库主键
    id: Mapped[IDPK]

    # 来源信息的 ID 群/频道
    from_chat_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("fromchats.from_chat_id"),
        nullable=False,
        comment="来源信息的ID 群/频道",
    )

    # 信息内容
    content: Mapped[str] = mapped_column(
        LONGTEXT, nullable=False, comment="信息内容"
    )

    # 信息时间
    msg_time: Mapped[datetime] = mapped_column(
        nullable=False,
        default=getBeijingTime,
        comment="信息时间",
    )

    # 来源用户ID
    tg_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("users.tg_id"),
        nullable=False,
        comment="来源信息的ID 群/频道",
    )
    # 来源 chat 的信息
    from_chat: Mapped["Fromchat"] = relationship(
        "Fromchat", back_populates="msgs"
    )

    from_user: Mapped["User"] = relationship("User", back_populates="msgs")


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "用户表"}

    # 用户唯一 TG ID
    tg_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        nullable=False,
        comment="用户唯一 TG ID",
    )
    # 用户名 可选
    username: Mapped[str] = mapped_column(
        String(255), nullable=True, comment="用户名"
    )

    msgs: Mapped[List[Msg]] = relationship("Msg", back_populates="from_user")


class Fromchat(Base):
    __tablename__ = "fromchats"
    __table_args__ = {"comment": "监控的群组详细信息"}

    msgs: Mapped[List[Msg]] = relationship("Msg", back_populates="from_chat")

    # 来源信息的ID 群/频道
    from_chat_id: Mapped[str] = mapped_column(
        String(100), primary_key=True, comment="来源信息的 ID 群/频道"
    )

    # 群名字
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="群名字"
    )

    # 群类型
    chat_type: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="群名字"
    )

    # 群/频道描述
    description: Mapped[str] = mapped_column(
        String(255), nullable=True, comment="群/频道描述"
    )

    # 创建时间
    create_time: Mapped[datetime] = mapped_column(
        nullable=False,
        default=getBeijingTime,
        comment="创建时间",
    )

    # 最后信息时间 (可选)
    last_msg_time: Mapped[datetime] = mapped_column(
        nullable=True,
        onupdate=getBeijingTime,
        comment="最后信息时间",
    )
