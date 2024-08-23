import functools
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, g
from ..models import User
# 密文保存密码相关包werkzeug.security  ,check_password_hash,generate_password_hash
from werkzeug.security import check_password_hash, generate_password_hash
from RealProject import db
from ..forms import LoginForm, RegisterForm     # 代码解耦，在LoginForm和RegisterForm中单独进行逻辑验证，在auth.py中只进行简单的操作

# 访问的时候就通过/blog进入博客页面
bp = Blueprint('auth', __name__, url_prefix='/auth',
               static_folder='../static', template_folder='../templates')


# 所谓before_app_request是注册了一个在视图函数之前运行的函数，无论请求什么URL，都会先检查用户ID是否存储在会话中，同时从数据库获取用户数据，将其存储在g.usr上
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user.id')
    # 使用g对象,g对象是一个全局对象，可以模板或者视图函数直接调用
    urls = ['/auth/']

    if user_id is None:
        print("Get in the function:load_logged_in_user")
        g.user = None
    else:
        g.user = User.query.get(int(user_id))  # 给g对象新增属性

        # 权限判断
        if g.user.is_super_user and g.user.is_active:
            g.user.has_perm = 1
        elif not g.user.is_super_user and g.user.is_active and not g.user.is_staff and request.path in urls:
            g.user.has_perm = 1
        else:
            g.user.has_perm = 0


def login_required(view):
    # 限制必须登录才能访问的页面装饰器
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            # 如果g.user为空，说明没有登录，这时候redirect_to就会记录下你的请求，以便在你登录后重定向回去ss
            redirect_to = f"{url_for('auth.login')}?redirect_to={request.path}"
            return redirect(redirect_to)
        if g.user.has_perm:
            pass
        else:
            return '<h1>无权限查看此页面~</h1>'
        return view(**kwargs)
    return wrapped_view


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # 登录逻辑，代码解耦（登录验证全部放在form中了）
    redirect_to = request.args.get('redirect_to')
    form = LoginForm()      # 一个表单实例化
    if form.validate_on_submit():       # 自动判断请求是post还是get，同时验证数据
        user = User.query.filter_by(username=form.username.data).first()
        session.clear()
        session['user.id'] = user.id    # 登录成功后对use.id属性赋值
        if redirect_to is not None:
            return redirect(redirect_to)
        return redirect('/')
    return render_template('login.html', form=form)  # 渲染


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()   # 实例化表单对象
    if form.validate_on_submit():       # 表单提交时验证
        user = User(username=form.username.data, password=generate_password_hash(form.password.data))
        db.session.add(user)
        db.session.commit()
        session.clear()
        session['user_id'] = user.id
        return redirect('userinfo.html')
    return render_template('register.html', form=form)


@bp.route('/logout')
def logout():
    # 注销
    session.clear()
    return redirect('/')


@bp.route('/')
def userinfo():
    return render_template('userinfo.html')



