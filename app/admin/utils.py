import os
import uuid
import click
from flask import Flask

from RealProject.settings import BASE_DIR
# secure_filename,文如其名，用来处理可能出错的文件名，比如如果有中文在名字里，类似“Bron鸭.png”，会被替代成"Bron.jpg"，是不是很大胆？
from RealProject import db
from werkzeug.utils import secure_filename
from app.auth.models import User
from werkzeug.security import generate_password_hash


def _file_path(directory_name):
    # 判断文件路径是否存在
    file_path = BASE_DIR / f'app/admin/static/{directory_name}'
    if os.path.exists(file_path) is False:
        os.makedirs(file_path)
    return file_path


def update_filename(f):
    # 分割成列表先,names列表的长度只有2，请注意这一点
    names = list(os.path.splitext(secure_filename(f.filename)))
    # 只取得名称,UUID 是一种能够保证全球范围内唯一性的标识符
    # 假设 uuid.uuid4() 生成的 UUID 是 8ff43f30-5864-4bfb-a06c-5a9869d9078d，那么处理后的文件名将是：
    # 8ff43f3058644bfba06c5a9869d9078d.png
    names[0] = ''.join(str(uuid.uuid4()).split('-'))
    return ''.join(names)


def upload_file_path(directory_name, f):
    file_path = _file_path(directory_name)
    filename = update_filename(f)
    return file_path / filename, filename


def init_script(app: Flask):
    @app.cli.command()
    # click库的prompt=True会在flask createsuperuser被执行时进行提示，还有个confirmation_prompt，作用就是让你确认密码
    @click.option('--username', prompt=True, help="请输入用户名")
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help="请输入用户密码")
    def createsuperuser(username, password):
        user = User(username=username, password=generate_password_hash(password), is_super_user=True)
        db.session.add(user)
        db.session.commit()
        click.echo(f'超级管理员{username}创建成功!')


