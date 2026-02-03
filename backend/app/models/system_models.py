# -*- coding: utf-8 -*-
# @author: rebort
import typing

from sqlalchemy import Column, String, Text, Integer, DateTime, select, update, Index, JSON
from sqlalchemy.orm import aliased

from app.models.base import Base


class User(Base):
    """用户表"""
    __tablename__ = 'user'

    username = Column(String(64), nullable=False, comment='用户名', index=True)
    password = Column(Text, nullable=False, comment='密码')
    email = Column(String(64), nullable=True, comment='邮箱')
    phone = Column(String(20), nullable=True, comment='手机号')
    roles = Column(JSON, nullable=False, comment='用户角色（JSON数组，逐步废弃，使用user_role表）')
    status = Column(Integer, nullable=False, comment='用户状态 0禁用 1启用', default=1)
    nickname = Column(String(255), nullable=False, comment='用户昵称')
    user_type = Column(Integer, nullable=False, comment='用户类型 10 管理人员, 20 测试人员', default=20)
    remarks = Column(String(255), nullable=False, comment='用户描述')
    avatar = Column(Text, nullable=True, default='', comment='头像')
    tags = Column(JSON, nullable=False, comment='标签')
    dept_id = Column(Integer, nullable=True, comment='部门ID')
    last_login_time = Column(DateTime, nullable=True, comment='最后登录时间')
    last_login_ip = Column(String(50), nullable=True, comment='最后登录IP')



    @classmethod
    async def get_user_by_roles(cls, roles_id: int) -> typing.Any:
        stmt = select(cls.id).where(cls.roles.like(f'%{roles_id}%'), cls.enabled_flag == 1)
        return await cls.get_result(stmt, True)

    @classmethod
    async def get_user_by_name(cls, username: str):
        stmt = select(*cls.get_table_columns()).where(cls.username == username, cls.enabled_flag == 1)
        return await cls.get_result(stmt, True)

    @classmethod
    async def get_user_by_nickname(cls, nickname: str):
        stmt = select(*cls.get_table_columns()).where(cls.nickname == nickname, cls.enabled_flag == 1)
        return await cls.get_result(stmt, True)


class Department(Base):
    """部门表"""
    __tablename__ = 'department'

    name = Column(String(100), nullable=False, comment='部门名称', index=True)
    dept_code = Column(String(64), nullable=True, comment='部门编码', index=True)
    parent_id = Column(Integer, nullable=True, comment='父部门ID', default=0)
    ancestors = Column(String(500), nullable=True, comment='祖级列表')
    leader_id = Column(Integer, nullable=True, comment='负责人ID')
    phone = Column(String(20), nullable=True, comment='联系电话')
    email = Column(String(100), nullable=True, comment='邮箱')
    sort = Column(Integer, nullable=True, comment='排序', default=0)
    status = Column(Integer, nullable=True, comment='状态 1启用 0禁用', default=1)
    description = Column(String(500), nullable=True, comment='部门描述')

    @classmethod
    async def get_list(cls):
        """获取所有部门列表"""
        q = [cls.enabled_flag == 1]
        u = aliased(User)
        stmt = select(
            *cls.get_table_columns(),
            u.nickname.label("created_by_name"),
            User.nickname.label("updated_by_name")
        ).where(*q) \
            .outerjoin(u, u.id == cls.created_by) \
            .outerjoin(User, User.id == cls.updated_by) \
            .order_by(cls.sort, cls.id)
        result = await cls.get_result(stmt)
        return result if result else []

    @classmethod
    async def get_by_name(cls, name: str, exclude_id: int = None):
        """根据名称查询部门"""
        q = [cls.name == name, cls.enabled_flag == 1]
        if exclude_id:
            q.append(cls.id != exclude_id)
        stmt = select(*cls.get_table_columns()).where(*q)
        return await cls.get_result(stmt, first=True)

    @classmethod
    async def get_children(cls, parent_id: int):
        """获取子部门"""
        stmt = select(*cls.get_table_columns()).where(
            cls.parent_id == parent_id,
            cls.enabled_flag == 1
        )
        return await cls.get_result(stmt)


class Menu(Base):
    """菜单表"""
    __tablename__ = 'menu'

    path = Column(String(255), nullable=False, comment='菜单路径')
    name = Column(String(255), nullable=False, comment='菜单名称', index=True)
    component = Column(String(255), nullable=True, comment='组件路径')
    title = Column(String(255), nullable=True, comment='title', index=True)
    isLink = Column(Integer, nullable=True,
                    comment='开启外链条件，`1、isLink: true 2、链接地址不为空（meta.isLink） 3、isIframe: false`')
    isHide = Column(Integer, nullable=True, default=False, comment='菜单是否隐藏（菜单不显示在界面，但可以进行跳转）')
    isKeepAlive = Column(Integer, nullable=True, default=True, comment='菜单是否缓存')
    isAffix = Column(Integer, nullable=True, default=False, comment='固定标签')
    isIframe = Column(Integer, nullable=True, default=False, comment='是否内嵌')
    roles = Column(String(64), nullable=True, default='', comment='权限（逐步废弃）')
    icon = Column(String(64), nullable=True, comment='icon', index=True)
    parent_id = Column(Integer, nullable=True, comment='父级菜单id')
    redirect = Column(String(255), nullable=True, comment='重定向路由')
    sort = Column(Integer, nullable=True, comment='排序')
    menu_type = Column(Integer, nullable=True, comment='菜单类型 1目录 2菜单 3按钮')
    permission = Column(String(100), nullable=True, comment='权限标识 如: user:add', index=True)
    visible = Column(Integer, nullable=True, default=1, comment='1显示 0隐藏')
    lookup_id = Column(Integer, nullable=True, comment='数据字典')
    active_menu = Column(String(255), nullable=True, comment='显示页签')
    views = Column(Integer, default=0, nullable=True, comment='访问数')

    @classmethod
    async def get_menu_by_ids(cls, ids: typing.List[int]):
        """获取菜单id（只返回目录和菜单，不包括按钮）- 用于用户菜单"""
        stmt = select(cls.get_table_columns()).where(
            cls.id.in_(ids), 
            cls.enabled_flag == 1,
            cls.menu_type.in_([1, 2])  # 1目录 2菜单，排除按钮(3)
        ).order_by(cls.sort)
        return await cls.get_result(stmt)

    @classmethod
    async def get_menus_and_buttons_by_ids(cls, ids: typing.List[int]):
        """获取菜单和按钮权限（包括所有类型）"""
        stmt = select(cls.get_table_columns()).where(
            cls.id.in_(ids), 
            cls.enabled_flag == 1
        ).order_by(cls.sort)
        return await cls.get_result(stmt)

    @classmethod
    async def get_menu_all(cls):
        """获取所有菜单（只返回目录和菜单，不包括按钮）- 用于用户菜单"""
        stmt = select(cls.get_table_columns()).where(
            cls.enabled_flag == 1,
            cls.menu_type.in_([1, 2])  # 1目录 2菜单，排除按钮(3)
        ).order_by(cls.sort)
        return await cls.get_result(stmt)

    @classmethod
    async def get_all_menus_with_buttons(cls):
        """获取所有菜单（包括按钮，用于管理界面）"""
        stmt = select(cls.get_table_columns()).where(
            cls.enabled_flag == 1
        ).order_by(cls.sort)
        return await cls.get_result(stmt)
        return await cls.get_result(stmt)

    @classmethod
    async def get_all_buttons(cls):
        """获取所有按钮权限"""
        stmt = select(cls.get_table_columns()).where(
            cls.enabled_flag == 1,
            cls.menu_type == 3  # 按钮类型
        ).order_by(cls.sort)
        return await cls.get_result(stmt)

    @classmethod
    async def get_buttons_by_ids(cls, ids: typing.List[int]):
        """根据ID获取按钮权限"""
        stmt = select(cls.get_table_columns()).where(
            cls.id.in_(ids),
            cls.enabled_flag == 1,
            cls.menu_type == 3  # 按钮类型
        ).order_by(cls.sort)
        return await cls.get_result(stmt)

    @classmethod
    async def get_parent_id_by_ids(cls, ids: typing.List[int]):
        """根据子菜单id获取父级菜单id"""
        stmt = select(cls.get_table_columns()).where(
            cls.id.in_(ids), 
            cls.enabled_flag == 1
        ).order_by(cls.sort)
        return await cls.get_result(stmt)

    @classmethod
    async def get_parent_id_all(cls):
        """根据子菜单id获取父级菜单id"""
        stmt = select(cls.get_table_columns()).where(cls.enabled_flag == 1).order_by(cls.sort)
        return await cls.get_result(stmt)

    @classmethod
    async def get_menu_by_title(cls, title: str):
        stmt = select(cls.get_table_columns()).where(cls.title == title, cls.enabled_flag == 1)
        return await cls.get_result(stmt, True)

    @classmethod
    async def get_menu_by_parent(cls, parent_id: int):
        stmt = select(cls.get_table_columns()) \
            .where(cls.parent_id == parent_id, cls.enabled_flag == 1) \
            .order_by(cls.sort)
        return await cls.get_result(stmt, True)

    @classmethod
    async def add_menu_views(cls, menu_id: int):
        stmt = update(cls.get_table_columns()).where(cls.id == menu_id, cls.enabled_flag == 1).values(
            **{"views": cls.views + 1})
        result = await cls.execute(stmt)
        return result.rowcount


class Roles(Base):
    """角色表"""
    __tablename__ = 'roles'

    name = Column(String(64), nullable=True, comment='角色名称', index=True)
    role_code = Column(String(64), nullable=True, comment='角色编码', index=True)
    role_type = Column(Integer, nullable=False, comment='权限类型，10菜单权限，20用户组权限', index=True, default=10)
    menus = Column(Text, nullable=True, comment='菜单列表（逐步废弃，使用role_menu表）', index=False)
    description = Column(String(500), nullable=True, comment='描述')
    status = Column(Integer, nullable=True, comment='状态 10 启用 20 禁用', default=10)
    dept_id = Column(Integer, nullable=True, comment='部门ID')
    data_scope = Column(Integer, nullable=True, default=1, comment='数据权限范围 1全部 2本部门 3本部门及下级 4仅本人')
    sort = Column(Integer, nullable=True, default=0, comment='排序')



    @classmethod
    async def get_roles_by_ids(cls, ids: typing.List, role_type=None):
        q = [cls.enabled_flag == 1, cls.id.in_(ids)]
        if role_type:
            q.append(cls.role_type == role_type)
        else:
            q.append(cls.role_type == 10)

        stmt = select(cls.get_table_columns()).where(*q)
        return await cls.get_result(stmt)

    @classmethod
    def get_all(cls, role_type=10):
        q = list()
        if role_type:
            q.append(cls.role_type == role_type)
        return cls.query.filter(*q, cls.enabled_flag == 1).order_by(cls.id.desc())

    @classmethod
    async def get_roles_by_name(cls, name, role_type=None):
        q = [cls.name == name, cls.enabled_flag == 1]
        if role_type:
            q.append(cls.role_type == role_type)
        else:
            q.append(cls.role_type == 10)
        stmt = select(cls.get_table_columns()).where(*q)
        return await cls.get_result(stmt, True)


class Lookup(Base):
    __tablename__ = 'lookup'

    code = Column(String(64), nullable=False, index=True, comment='编码')
    description = Column(String(256), comment='描述')



    @classmethod
    async def get_lookup_by_code(cls, code: str):
        stmt = select(cls).where(cls.code == code, cls.enabled_flag == 1)
        return await cls.get_result(stmt)


class LookupValue(Base):
    __tablename__ = 'lookup_value'

    id = Column(Integer, primary_key=True, comment='主键')
    lookup_id = Column(Integer, nullable=False, index=True, comment='所属类型')
    lookup_code = Column(String(32), nullable=False, index=True, comment='编码')
    lookup_value = Column(String(256), comment='值')
    ext = Column(String(256), comment='拓展1')
    display_sequence = Column(Integer, comment='显示顺序')



    @classmethod
    async def get_lookup_value_by_lookup_id(cls, lookup_id, lookup_code=None):
        q = [cls.lookup_id == lookup_id, cls.enabled_flag == 1]
        if lookup_code:
            q.append(cls.lookup_code == lookup_code)
        stmt = select(cls.get_table_columns()).where(*q) \
            .order_by(cls.id.desc())
        return await cls.get_result(stmt, True)


class RequestHistory(Base):
    __tablename__ = 'request_history'

    id = Column(Integer, primary_key=True, comment='主键')
    remote_addr = Column(String(255), nullable=False, comment='用户名称')
    real_ip = Column(String(255), nullable=False, comment='用户名称')
    request = Column(Text, nullable=False, comment='用户名称')
    method = Column(String(255), nullable=True, comment='操作')
    url = Column(String(255), nullable=True, comment='操作')
    args = Column(String(255), nullable=True, comment='操作')
    form = Column(String(255), nullable=True, comment='操作')
    json = Column(Text, nullable=True, comment='操作')
    response = Column(Text, nullable=True, comment='操作')
    endpoint = Column(Text, nullable=True, comment='操作')
    elapsed = Column(Text, nullable=True, comment='操作')
    request_time = Column(DateTime, nullable=True, comment='操作')
    env = Column(String(255), nullable=True, comment='操作')
    employee_code = Column(String(255), nullable=True, comment='操作')
    toekn = Column(String(255), nullable=True, comment='操作')


class MenuViewHistory(Base):
    """访问"""
    __tablename__ = 'menu_view_history'

    menu_id = Column(Integer(), nullable=True, comment='菜单id', index=True)
    remote_addr = Column(String(64), nullable=True, comment='访问ip', index=True)
    user_id = Column(Integer(), nullable=True, comment='访问人', index=True)


class Notify(Base):
    """消息"""
    __tablename__ = 'notify'

    user_id = Column(Integer(), nullable=True, comment='用户id', index=True)
    group = Column(String(64), nullable=True, comment='组')
    message = Column(String(500), nullable=True, comment='消息')
    send_status = Column(Integer(), nullable=True, comment='发送状态，10成功 20 失败')
    read_status = Column(Integer(), nullable=True, comment='消息状态，10未读 20 已读')


class UserLoginRecord(Base):
    __tablename__ = "user_login_record"
    __table_args__ = (
        Index('idx_login_record_code_logintime', 'code', 'login_time'),
    )

    token = Column(String(40), index=True, comment='登陆token')
    code = Column(String(64), index=True, comment='账号')
    user_id = Column(Integer, comment='用户id')
    user_name = Column(String(50), comment='用户名称')
    logout_type = Column(String(50), comment='退出类型')
    login_type = Column(String(50), index=True, comment='登陆方式   扫码  账号密码等')
    login_time = Column(DateTime, index=True, comment='登陆时间')
    logout_time = Column(DateTime, comment='退出时间')
    login_ip = Column(String(30), index=True, comment='登录IP')
    ret_msg = Column(String(255), comment='返回信息')
    ret_code = Column(String(9), index=True, comment='是否登陆成功  返回状态码  0成功')
    address = Column(String(255), comment='地址')
    source_type = Column(String(255), comment='来源')



    @classmethod
    async def get_by_token(cls, token: str):
        if not token:
            return None
        stmt = select(cls.get_table_columns()).where(cls.enabled_flag == 1, cls.token == token).order_by(cls.id.desc())
        return await cls.get_result(stmt, first=True)


class FileInfo(Base):
    """文件信息"""
    __tablename__ = 'file_info'
    id = Column(String(60), nullable=False, primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=True, comment='存储的文件名')
    file_path = Column(String(255), nullable=True, comment='文件路径')
    extend_name = Column(String(255), nullable=True, comment='扩展名称', index=True)
    original_name = Column(String(255), nullable=True, comment='原名称')
    content_type = Column(String(255), nullable=True, comment='文件类型')
    file_size = Column(String(255), nullable=True, comment='文件大小')
