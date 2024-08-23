from flask_wtf import FlaskForm
from wtforms import (StringField, RadioField, SelectField,
                     TextAreaField, SelectMultipleField,
                     PasswordField, BooleanField, URLField)
from wtforms.validators import DataRequired, Length, URL
from app.blog.models import PostPublishType
from flask_wtf.file import FileField, FileRequired, FileSize, FileAllowed


# Form用来完成数据库的查询以及后续操作（增删查改）
class CategoryForm(FlaskForm):
    name = StringField('分类名称', validators=[
        DataRequired(message="不能为空"),
        Length(max=128, message="不符合字数要求！")
    ])
    icon = StringField('分类图标', validators=[
        Length(max=256, message="不符合字数要求！")
    ])


class ArticleForm(FlaskForm):
    title = StringField('标题', validators=[
        DataRequired(message="不能为空"),
        Length(max=128, message="不符合字数要求")
    ])
    desc = StringField('描述', validators=[
        DataRequired(message="不能为空"),
    ])
    has_type = RadioField('发布状态',
                          choices=(PostPublishType.draft.name, PostPublishType.show.name),
                          default=PostPublishType.show.name)
    # WTForms提供的HTML下拉框
    category_id = SelectField(
        '分类',
        choices=None,
        coerce=int,
        validators=[
            DataRequired(message="不能为空"),
        ]
    )
    # 长文本
    content = TextAreaField('文章详情',
                            validators=[DataRequired(message="不能为空")]
                            )
    tags = SelectMultipleField('文章标签', choices=None, coerce=int)


class TagForm(FlaskForm):
    name = StringField('标签', validators=[
        DataRequired(message="不能为空"),
        Length(max=128, message="不符合字数要求")
    ])


class CreateUserForm(FlaskForm):
    username = StringField('username', validators=[
        DataRequired(message="不能为空哦"),
        Length(max=32, message="不能为空哦")
    ])
    password = PasswordField('password', validators=[
        Length(max=32, message="不符合字数要求~")
    ], description="修改用户信息时，留空代表不修改")
    avatar = FileField("avatar", validators=[
        FileAllowed(['jpg', 'png', 'gif'], message="支持的格式只有jpg/png/gif后缀哦"),
        FileSize(max_size=20480000, message="20Mb都可以，不要不识抬举>")],
        description="20Mb的头像还有啥不满足:<<，目前仅支持jpg/png/gif后缀文件，不选择就代表不修改")
    is_super_user = BooleanField("是否为管理员")
    is_active = BooleanField("是否活跃", default=True)
    is_staff = BooleanField("是否锁定")


class BannerForm(FlaskForm):
    # banner表单
    img = FileField("Banner图", validators=[
        # FileRequired(),
        FileAllowed(['jpg', 'png', 'gif'], message="仅支持jpg/png/gif格式"),
        FileSize(max_size=3 * 1024 * 1000, message="不能大于3M")],
        description="大小不超过3M，仅支持jpg/png/gif格式，不选择则代表不修改, 尺寸比例：3:1")

    desc = StringField('描述', validators=[
        # DataRequired(message="不能为空"),
        Length(max=200, message="不符合字数要求！")
        ])

    url = URLField("Url", validators=[
        URL(require_tld=False, message="请输入正确的url"),
        Length(max=300, message="不符合字数要求！")])


'''
URL(require_tld=False, message="请输入正确的url")：

require_tld=False 表示不要求 URL 中必须包含顶级域名 (Top-Level Domain, TLD)，这意味着 http://example.com 和 http://example 都将被视为有效的 URL。
message="请输入正确的url" 是在验证失败时显示的自定义消息，提示用户输入正确的 URL。
Length(max=300, message="不符合字数要求！")：

max=300 指定了 URL 的最大长度为 300 个字符。如果输入的 URL 超过了这个长度，验证将失败。
message="不符合字数要求！" 是在验证失败时显示的自定义消息，指示用户输入的 URL 不符合长度要求。
因此，这段代码限制了 URL 的两个方面：要求 URL 格式正确（不需要顶级域名），并且限制 URL 的最大长度为 300 个字符。
'''