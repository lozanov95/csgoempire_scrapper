from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, SearchForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Item, PricedItems
from app.csgoempire_scrapper import CSGOEmpireScrapper
import json


@app.route('/')
@app.route('/index')
def index():
    items = PricedItems.query.order_by(PricedItems.weapon_name, PricedItems.max_price.desc())
    return render_template('index.html', items=items)


@login_required
@app.route('/scrape')
def scrape():
    scrapper = CSGOEmpireScrapper(initial_pause_seconds=5)
    data = json.loads(scrapper.scrape_items())
    priced_items = []
    try:
        for value in data['values']:
            existing = False
            try:
                for item in priced_items:
                    if item.weapon_name == value['weapon_name'] and item.skin_name == value['skin_name'] \
                            and item.skin_quality == value['skin_quality']:
                        existing = True
                        if item.min_price > value['skin_price']:
                            item.min_price = value['skin_price']
                        if item.max_price < value['skin_price']:
                            item.max_price = value['skin_price']
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
        print(e)
    try:
        for item in priced_items:
            db.session.add(item)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
    for priced_item in priced_items:
        existing = False
        new_items = PricedItems.query.all()
        for new_item in new_items:
            if new_item.weapon_name == priced_item.weapon_name and\
                    new_item.skin_name == priced_item.skin_name and\
                    new_item.skin_quality == priced_item.skin_quality:
                existing = True
                if new_item.max_price < priced_item.max_price:
                    new_item.max_price = priced_item.max_price
                if new_item.min_price > priced_item.min_price:
                    new_item.min_price = priced_item.min_price
                db.session.commit()
                break
        if not existing:
            new_priced_item = PricedItems(weapon_name=priced_item.weapon_name,
                                          skin_quality=priced_item.skin_quality,
                                          skin_name=priced_item.skin_name,
                                          min_price=priced_item.min_price,
                                          max_price=priced_item.max_price)
            try:
                db.session.add(new_priced_item)
                db.session.commit()
            except Exception as e:
                print(e)
                db.session.rollback()
    return redirect(url_for('index'))


@login_required
@app.route('/search', methods=['GET', 'POST'])
def search():
    if current_user.is_authenticated:
        form = SearchForm()
        if form.validate_on_submit():
            if form.skin_name.data != "" and form.weapon_name.data != "":
                print(form.weapon_name.data)
                items = Item.query.filter(Item.weapon_name.contains(form.weapon_name.data),
                                          Item.skin_name.contains(form.skin_name.data))
                return render_template('index.html', items=items, form=form)
            elif form.skin_name.data != "":
                items = Item.query.filter(Item.skin_name.contains(form.skin_name.data)).all()
                print(items)
                return render_template('index.html', items=items, form=form)
            elif form.weapon_name.data != "":
                items = Item.query.filter(Item.weapon_name.contains(form.weapon_name.data))
                return render_template('index.html', items=items, form=form)
        return render_template('search.html', form=form)
    return redirect(url_for('index'))


@login_required
@app.route('/details/<id>', methods=['GET', 'POST'])
def details(id):
    scanned_item = PricedItems.query.filter_by(id=id).first()
    items = Item.query.filter_by(weapon_name=scanned_item.weapon_name,
                                 skin_name=scanned_item.skin_name,
                                 skin_quality=scanned_item.skin_quality).order_by(Item.timestamp.desc())
    return render_template('details.html', items=items)


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
