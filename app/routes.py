import os
from flask import render_template, flash, redirect, url_for, request, send_file, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, SignupForm, ChangePasswordForm, NewOrderForm
from app.models import User, Order
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        if current_user.username == 'admin':
            return redirect('admin')
        else:
            return redirect(url_for('view_orders'))
    else:
        return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        if form.password.data == form.password2.data:
            user.set_password(form.password.data)
            user.full_name = form.full_name.data
            user.tutor_group = form.tutor_group.data
            db.session.add(user)
            db.session.commit()
            flash('You are now signed up.')
            return redirect(url_for('login'))
        flash('Invalid password')
    return render_template('signup.html', title='Signup', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password'.format(form.username.data, form.remember_me.data))
            return redirect(url_for('index'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = current_user
        if user.check_password(form.old_password.data) and form.new_password.data == form.new_password2.data:
            user.set_password(form.new_password.data)
            db.session.commit()
            logout_user()
            flash('Password changed')
            return redirect(url_for('login'))
        flash('Incorrect password')
    return render_template('change_password.html', title='Change Password', form=form)

@app.route('/view_orders')
@login_required
def view_orders():
    user = current_user
    orders = user.orders()
    orders_length = orders.count()
    return render_template('view_orders.html', title='New Order', user=user, orders=orders, orders_length=orders_length)

@app.route('/new_order', methods=['GET', 'POST'])
@login_required
def new_order():
    form = NewOrderForm()
    if form.validate_on_submit():
        user = current_user
        order = Order(user_id=user.id, name=form.name.data, status=0)
        db.session.add(order)
        db.session.flush()
        uploaded_file = form.uploaded_file.data
        filename = str(order.id) + '_' + secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        order.filename = filename
        db.session.commit()
        flash('Order submitted')
        return redirect(url_for('index'))
    return render_template('new_order.html', title='New Order', form=form)

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_file(os.path.join(os.path.abspath(''), app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(os.path.abspath(''), 'static'), 'favicon.ico')
