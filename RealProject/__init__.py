import os
from RealProject.settings import BASE_DIR
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 数据库
db = SQLAlchemy()
# 数据库迁移
migrate = Migrate()


# test_config测试配置，默认为空
def create_app(test_config=None):
    # Flask应用程序是Flask类的一个实例
    app = Flask(__name__, instance_relative_config=True)  # instance_relative_config 表示允许从文件中加载配置，也就是settings.py

    # 如果没有提供测试配置，则尝试从 settings.py 文件中加载配置
    if test_config is None:
        CONFIG_PATH = BASE_DIR / 'RealProject/settings.py'      # 绝对路径
        app.config.from_pyfile(CONFIG_PATH, silent=True)  # silent=True告诉 Flask 在加载配置文件时忽略可能发生的错误，而不会抛出异常
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    # 引入blog的视图文件
    from app.blog import views as blog
    app.register_blueprint(blog.bp)
    from app.auth import views as auth
    app.register_blueprint(auth.bp)
    from app.admin import views as admin
    app.register_blueprint(admin.bp)

    app.add_url_rule('/', endpoint='index', view_func=blog.index)

    # 注册数据库模型，并没有被调用
    from app.blog import models
    from app.auth import models
    from app.admin import models

    # 引入上下文
    app.context_processor(inject_category)

    # 注册自定义命令，可以在命令行使用
    from app.admin.utils import init_script
    init_script(app)
    return app


def inject_category():
    # 上下文处理器回调函数
    from app.blog.models import Category
    categorys = Category.query.limit(6).all()
    return dict(categorys=categorys)
