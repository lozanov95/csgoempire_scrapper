from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, SearchForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Item
from app.csgoempire_scrapper import CSGOEmpireScrapper
import json


@app.route('/')
@app.route('/index')
def index():
    items = Item.query.order_by(Item.timestamp.desc()).all()
    return render_template('index.html', items=items)


@login_required
@app.route('/scrape')
def scrape():
    scrapper = CSGOEmpireScrapper()
    data = json.loads(scrapper.scrape_items())
    priced_items = []
    try:
        for value in data['values']:
            existing = False
            try:
                for item in priced_items:
                    if item.get('weapon_name') == value['weapon_name'] and item.get('skin_name') == value['skin_name'] \
                            and item.get('skin_quality') == value['skin_quality']:
                        existing = True
                        if item['min_price'] > value['skin_price']:
                            item['min_price'] = value['skin_price']
                        if item['max_price'] < value['skin_price']:
                            item['max_price'] = value['skin_price']
                        break
                if not existing:
                    new_item = Item(skin_quality=value['skin_quality'],
                                    weapon_name=value['weapon_name'],
                                    min_price=value['skin_price'],
                                    max_price=value['skin_price'],
                                    timestamp=value['timestamp'],
                                    skin_name=value['skin_name'])
                    priced_items.append(new_item)
            except Exception as e:
                print(e)
    except Exception as e:
        print('exception on adding items')
        print(e)
    try:
        for item in priced_items:
            db.session.add(item)
        db.session.commit()
    except Exception as e:
        print('exception on adding items to db')
        print(e)
        db.session.rollback()
    finally:
        return redirect(url_for('index'))


@login_required
@app.route('/search', methods=['GET', 'POST'])
def search():
    if current_user.is_authenticated:
        form = SearchForm()
        if form.validate_on_submit():
            if form.skin_name.data != "" and form.weapon_name.data != "":
                print('has name and skin')
                print(form.weapon_name.data)
                items = Item.query.filter(Item.weapon_name.contains(form.weapon_name.data),
                                          Item.skin_name.contains(form.skin_name.data))
                return render_template('index.html', items=items, form=form)
            elif form.skin_name.data != "":
                print('has skin')
                items = Item.query.filter(Item.skin_name.contains(form.skin_name.data)).all()
                print(items)
                return render_template('index.html', items=items, form=form)
            elif form.weapon_name.data != "":
                print('has wep name')
                items = Item.query.filter(Item.weapon_name.contains(form.weapon_name.data))
                return render_template('index.html', items=items, form=form)
        return render_template('search.html', form=form)
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form, page_name='Login')


@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('login.html', title='Register', form=form, page_name='Register')
