from flask_wtf import FlaskForm     # 表单
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from werkzeug.security import check_password_hash
from .models import User


class LoginForm(FlaskForm):
    # 登录表单
    def qs_username(username):
        # 对该字段进行在传递之前处理
        u = f'{username}'
        print(u)
        return username

    username = StringField('username', validators=[     # validators 是 WTForms 中用于定义字段验证规则的部分
        DataRequired(message="不能为空"),           # DataRequired是WTForms提供的专门处理空字段的验证器，为空则会提示message的信息（string）
        Length(max=32, message="不符合字数要求！")   # Length也差不多，是长度验证器，很容易理解参数意义
    ], filters=(qs_username,))
    password = PasswordField('password', validators=[
        DataRequired(message="不能为空"),
        Length(max=32, message="不符合字数要求！")
    ])

    # 定义验证器，这个写法是固定的，指validate_username,form是表单本身，field是字段本身。
    def validate_username(form, field):
        user = User.query.filter_by(username=field.data).first()
        if user is None:
            error = '该用户不存在！'
            raise ValidationError(error)
        elif not check_password_hash(user.password, form.password.data):
            raise ValidationError('密码不正确')


class RegisterForm(FlaskForm):
    # 注册表单
    username = StringField('username', validators=[
        DataRequired(message="不能为空"),
        Length(min=2, max=32, message="超过限制字数！")
        ])
    password = PasswordField('password', validators=[
        DataRequired(message="不能为空"),
        Length(min=2, max=32, message="超过限制字数！"),
        EqualTo('password1', message='两次密码输入不一致！')  #
        ])
    password1 = PasswordField('password1')

    def validate_username(form, field):
        user = User.query.filter_by(username=field.data).first()
        if user is not None:
            error = '该用户名称已存在！'
            raise ValidationError(error)