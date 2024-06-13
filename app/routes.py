from flask import render_template, flash, redirect, url_for, request, jsonify, abort
from flask_login import current_user, login_user, logout_user, login_required
from app import db, bcrypt
from app.models import User, Post
from app.forms import LoginForm, RegistrationForm, PostForm
from flask import Blueprint
from functools import wraps

bp = Blueprint('main', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'Admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    posts = Post.query.all()
    return render_template('index.html', title='Home', posts=posts)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))
    return render_template('create_post.html', title='Create Post', form=form)


@bp.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', title=post.title, post=post)


@bp.route('/admin')
@admin_required
def admin():
    return render_template('admin.html')


# RESTful API routes
@bp.route('/api/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    return jsonify([post.to_dict() for post in posts])


@bp.route('/api/posts/<int:id>', methods=['GET'])
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_dict())


@bp.route('/api/posts', methods=['POST'])
@login_required
def create_post_api():
    if not request.json or not 'title' in request.json:
        return jsonify({'error': 'Bad request'}), 400
    post = Post(
        title=request.json['title'],
        body=request.json.get('body', ''),
        author=current_user
    )
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_dict()), 201


@bp.route('/api/posts/<int:id>', methods=['PUT'])
@login_required
def update_post(id):
    post = Post.query.get_or_404(id)
    if not request.json:
        return jsonify({'error': 'Bad request'}), 400
    post.title = request.json.get('title', post.title)
    post.body = request.json.get('body', post.body)
    db.session.commit()
    return jsonify(post.to_dict())


@bp.route('/api/posts/<int:id>', methods=['DELETE'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'result': True})


@bp.route('/api/posts/<int:id>/like', methods=['POST'])
@login_required
def like_post(id):
    post = Post.query.get_or_404(id)
    post.likes += 1
    db.session.commit()
    return jsonify({'likes': post.likes})