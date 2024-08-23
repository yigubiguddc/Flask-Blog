from flask import Blueprint, render_template, request, g, flash, redirect, url_for
from .models import Post, Category, Tag, Comment
from .forms import CommentForm
from RealProject import db

# 这里是一个蓝图对象，与bp相关所有的url都有blog前缀，如果想要不是以blog为前缀的就需要其他区别于bp的蓝图对象，在
bp = Blueprint('blog', __name__, url_prefix='/blog', static_folder='static', template_folder='templates')


def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(-Post.add_date).paginate(page=page, per_page=9, error_out=False)
    post_list = pagination.items
    import random
    imgs = ["https://c.wallhere.com/photos/c0/9d/Bronya_Honkai_Star_Rail_Bronya_Zaychik_Honkai_Impact-2239266.jpg!d",
            "http://picture.gptkong.com/20240509/1914f694bf4e424b479d2f85fa0d9dd680.jpg",
            "http://picture.gptkong.com/20240509/19152a0934e6414430b9bb94afc52702fc.jpg",
            "http://picture.gptkong.com/20240509/1915d3325bbb7f4bf1b3052f847e40b182.jpg",
            "http://picture.gptkong.com/20240509/1916fed500cfcb435c84c688278bb64bdf.jpg",
            "http://picture.gptkong.com/20240509/19160db3f65d414256b56366bc27ccf480.png",
            "http://picture.gptkong.com/20240509/1917e05ebf4f68471998c33e1b9305c896.png",
            "http://picture.gptkong.com/20240509/191708fb9a25a24297b794028aededbe2b.jpg",
            "http://picture.gptkong.com/20240509/191870909b68234a6b892c12c8e42ac6c1.jpg",
            "http://picture.gptkong.com/20240509/191992f1c695a24ba68b8c1acbefee2bdc.png",
            "http://picture.gptkong.com/20240509/19209876c86ace4a22ab88a45154496528.jpg",
            "http://picture.gptkong.com/20240509/1921afa13553b74f0bb9ea9b49af849a21.jpg"
            ]

    for post in post_list:
       #  post.img = random.sample(imgs, 1)[0]
        post.img = random.choice(imgs)

    import json
    from app.admin.models import Banner
    banners = Banner.query.all()
    # for banner in banners:
    #     print(f"ID: {banner.id}, Image: {banner.img}, Description: {banner.desc}, URL: {banner.url}")    # 可以打印出来，说明没毛病

    # 列表推导式
    banners_list = [{'img':f'/admin/static/{banner.img}', 'url':banner.url} for banner in banners]
    banners_json = json.dumps(banners_list, ensure_ascii=False)

    return render_template('index.html', posts=post_list, pagination=pagination, banners=banners_json)


@bp.route('/category/<int:cate_id>')
def cates(cate_id):
    cate = Category.query.get(cate_id)
    page = request.args.get('page', default=1, type=int)
    pagination = Post.query.filter(Post.category_id == cate_id).paginate(page=page, per_page=10, error_out=False)
    post_list = pagination.items

    return render_template('cate_list.html', post_list=post_list, cate=cate, pagination=pagination, page=page)


@bp.route('/category/<int:cate_id>/<int:post_id>', methods=['GET', 'POST'])
def detail(cate_id, post_id):
    cate = Category.query.get(cate_id)
    post = Post.query.get_or_404(post_id)

    prev_page = Post.query.filter(Post.id < post_id).order_by(-Post.id).first()
    next_post = Post.query.filter(Post.id > post_id).order_by(Post.id).first()

    # 2024.05.05新增评论列表
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.filter(Comment.post_id == post.id).order_by(-Comment.add_date).paginate(page=page, per_page=10, error_out=False)
    comment_list = pagination.items

    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            post_id=post.id,
            user_id=g.user.id
        )
        db.session.add(comment)
        db.session.commit()
        flash(f'评论成功！')
        # 跳转回到当前详情页面
        return redirect(f"{url_for('blog.detail', cate_id=cate.id, post_id=post.id)}#comment")

    return render_template('detail.html', cate=cate, post=post,
                           prev_page=prev_page, next_post=next_post,
                           pagination=pagination, comment_list=comment_list, form=form)


@bp.context_processor
def inject_archive():
    # 文章归档日期注入上下文
    posts = Post.query.order_by(-Post.add_date)
    dates = set([post.add_date.strftime("%Y年%m月") for post in posts])

    # 标签
    tags = Tag.query.all()
    for tag in tags:
        # 颜色
        tag.style = ['is-success', 'is-danger', 'is-black', 'is-light', 'is-primary', 'is-link', 'is-info', 'is-warning']
    # 最新文章·
    new_posts = posts.limit(6)
    return dict(dates=dates, tags=tags, new_posts=new_posts)


@bp.route('/category/<string:date>')
def archive(date):
    # 归档页
    import re
    # 正则匹配年月
    regex = re.compile(r'\d{4}|\d{2}')
    dates = regex.findall(date)
    print(dates)

    from sqlalchemy import extract, and_, or_   # 引入了奇怪的东西
    page = request.args.get('page', 1, type=int)
    # 根据年月获取数据筛选依据，这里还是从文章（Post）中选择的
    archive_posts = Post.query.filter(and_(extract('year', Post.add_date) == int(dates[0]), extract('month', Post.add_date) == int(dates[1])))
    # 对数据进行分页
    pagination = archive_posts.paginate(page=page, per_page=10, error_out=False)
    return render_template('archive.html', post_list=pagination.items,  pagination=pagination, date=date)


@bp.route('/tags/<int:tag_id>')
def tags(tag_id):
    # 标签页
    tag = Tag.query.get(tag_id)
    return render_template('tags.html', post_list=tag.post, tag=tag)


@bp.route('/search')
def search():
    words=request.args.get('words')
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter(Post.title.like("%" + words + "%")).paginate(page=page, per_page=10, error_out=False)
    post_list = pagination.items
    return render_template('search.html', words=words, post_list=post_list, pagination=pagination)


@bp.route('/test',  methods=['GET'])
def test():
    return {
        'status', 'success',
        'message', 'test route success'
    }

