from flask import render_template, flash, session, request, redirect, url_for, jsonify
from flask_admin.contrib.sqla import ModelView
from app import app, db, models, admin
from .models import Users, Items, Basket
from .forms import loginForm


class UserAdmin(ModelView):
    column_list = ('id', 'username', 'password')

class ItemAdmin(ModelView):
    column_list = ('id', 'name', 'price', 'stock', 'category')

class BasketAdmin(ModelView):
    column_list = ('id', 'user_id', 'item_id', 'quantity', 'name', 'price')


admin.add_view(UserAdmin(Users, db.session))
admin.add_view(ItemAdmin(Items, db.session))
admin.add_view(BasketAdmin(Basket, db.session))

@app.route('/')
@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    return render_template('welcome.html',title='login')


@app.route('/login', methods=['GET', 'POST'])
def login():    
    form = loginForm()
    if form.validate_on_submit():
        user = models.Users.query.filter_by(username=form.username.data.lower()).first()
        if user:
            if  user.password == form.password.data:
                return redirect(url_for('home', user_id=user.id))
            else:
                flash("Incorrect Password")
        else:
            flash("Username does not exist")

    return render_template('login.html', title="login", form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = loginForm()
    is_num = False
    is_special = False
    if form.validate_on_submit():
        for i in range(len(form.password.data)):
            if form.password.data[i].isdigit():
                is_num = True
            elif not form.password.data[i].isalpha():
                is_special = True


        if models.Users.query.filter_by(username=form.username.data.lower()).first():
            flash('Username already exists')
        elif len(form.password.data) < 8:
            flash('Password must be at least 8 characters')
        elif is_num == False:
            flash('Password must contain a number')
        elif is_special == False:
            flash('Password must contain a special character')
        else:
            # Find the assesment in the database with highest ID and give the new assessment an ID of this value +1
            last_user = models.Users.query.order_by(models.Users.id.desc()).first()
            if last_user is not None:
                use_id = last_user.id + 1
            # No assessments in database
            else:
                use_id = 1
            p = Users(id=use_id, username=form.username.data.lower(), password=form.password.data)
            db.session.add(p)
            db.session.commit()
            return redirect(url_for('home', user_id=use_id))


    return render_template('signup.html', title="Sign Up", form=form)



@app.route('/home/<int:user_id>', methods=['GET', 'POST'])
def home(user_id):
    user = Users.query.get(user_id)
    
    basket_entries = Basket.query.all()
    
    items = {}

    for basket in basket_entries:
            if basket.item in items.keys():
                quantity = items.get(basket.item)
                items.update({basket.item: quantity + basket.quantity})
            else:
                items[basket.item] = basket.quantity

    most_popular = 0
    second_popular = 0
    third_popular = 0
    for q in items.values():
        if q > most_popular:
            m = most_popular
            most_popular = q
            q = second_popular
            second_popular = m
            third_popular = q
        elif q > second_popular:
            s = second_popular
            second_popular = q
            third_popular = s
        elif q > third_popular:
            third_popular = q
    
    popular = []
    for x, y in items.items():
        if y >= third_popular:
            popular.append(x)
    
    if Basket.query.filter_by(user_id=user_id).count() > 0:
        item_id = Basket.query.filter_by(user_id=user_id).first().item_id
        item = Items.query.get(item_id)
            
        split = item.name.split()
        results = Items.query.filter(Items.name.ilike(f"%{split[0]}%")).all()
        results = results + Items.query.filter(Items.name.ilike(f"%{split[1]}%")).all()
        results = list(dict.fromkeys(results))
    
    else:
        results=[]

    return render_template('home.html', title='home', user=user, popular=popular, results=results)

@app.route('/checkout/<int:user_id>', methods=['GET', 'POST'])
def checkout(user_id):
    user = Users.query.get(user_id)
    bag = Basket.query.filter_by(user_id=user_id).all()
    total = sum(item.price for item in bag)

    return render_template('checkout.html', title='Checkout', user=user, bag=bag, total=total)

@app.route('/category/<int:user_id><string:cat>', methods=['GET', 'POST'])
def category(user_id, cat):
    user = Users.query.get(user_id)
    
    if cat == 'All':
        items = Items.query.all()
    else:
        items = Items.query.filter_by(category=cat).all()
    
    for item in items:
        if item.stock <= 0:
            items.remove(item)

    return render_template('category.html', title='category', user=user, cat=cat, items=items)

@app.route('/add_to_basket', methods=['GET', 'POST'])
def add_to_basket():
    if request.method == 'POST':
        cat = request.form.get('cat')
        user_id = request.form.get('user_id')
        item_id = request.form.get('item_id')
        quantity = int(request.form.get('quantity'))
        item = Items.query.get(item_id)
        user = Users.query.get(user_id)
        
        # Stop people ordering to many of one item
        if Basket.query.filter_by(user_id=user_id, item_id=item_id).first():
            if quantity > 50 or Basket.query.filter_by(user_id=user_id, item_id=item_id).first().quantity + quantity > 50:
                flash('No more than 50 of one item is allowed per purchase, sorry for any inconveniance')
                return redirect(url_for('category', user_id=user_id, cat=cat))
        else:
            if quantity > 50:
                flash('No more than 50 of one item is allowed per purchase, sorry for any inconveniance')
                return redirect(url_for('category', user_id=user_id, cat=cat))
        
        if item.stock - quantity <= 0:
            flash('You have ordered too many of this item, please try ordering less')
            return redirect(url_for('category', user_id=user_id, cat=cat))

        if request.form['submit_button'] == 'Add to Basket':
            
            if item:
                if Basket.query.filter_by(user_id=user_id, item_id=item_id).all():
                    p = Basket.query.filter_by(user_id=user_id, item_id=item_id).first()
                    p.quantity += quantity
                    p.price += item.price * quantity
                else:
                    p = Basket(user_id=user_id, item_id=item_id, quantity=quantity, name=item.name, price=item.price*quantity)
                    db.session.add(p)
                item.stock -= quantity
                db.session.commit()

                flash('Succesfully added to basket')
                return redirect(url_for('category', user_id=user_id, cat=cat))


@app.route('/remove_from_basket', methods=['GET', 'POST'])
def remove_from_basket():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        bag_id = request.form.get('bag_id')

        p = Basket.query.get(bag_id)
        item = Items.query.get(p.item_id)
        item.stock += p.quantity
        db.session.delete(p)
        db.session.commit()

        bag = Basket.query.filter_by(user_id=user_id).all()
        total = sum(item.price * item.quantity for item in bag)
        return redirect(url_for('checkout', user_id=user_id, bag=bag, total=total))

@app.route('/add_to_basket_home', methods=['GET', 'POST'])
def add_to_basket_home():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        item_id = request.form.get('item_id')
        quantity = int(request.form.get('quantity'))
        item = Items.query.get(item_id)
     
        
        # Stop people ordering to many of one item
        if Basket.query.filter_by(user_id=user_id, item_id=item_id).first():
            if quantity > 50 or Basket.query.filter_by(user_id=user_id, item_id=item_id).first().quantity + quantity > 50:
                flash('No more than 50 of one item is allowed per purchase, sorry for any inconveniance')
                return redirect(url_for('home', user_id=user_id))
        else:
            if quantity > 50:
                flash('No more than 50 of one item is allowed per purchase, sorry for any inconveniance')
                return redirect(url_for('home', user_id=user_id))
        
        if item.stock - quantity <= 0:
            flash('You have ordered too many of this item, please try ordering less')
            return redirect(url_for('home', user_id=user_id))

        if request.form['submit_button'] == 'Add to Basket':
            
            if item:
                if Basket.query.filter_by(user_id=user_id, item_id=item_id).all():
                    p = Basket.query.filter_by(user_id=user_id, item_id=item_id).first()
                    p.quantity += quantity
                    p.price += item.price * quantity
                else:
                    p = Basket(user_id=user_id, item_id=item_id, quantity=quantity, name=item.name, price=item.price*quantity)
                    db.session.add(p)
                item.stock -= quantity
                db.session.commit()

                flash('Succesfully added to basket')
                return redirect(url_for('home', user_id=user_id))
            
@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query') 
    user_id = request.args.get('user_id')
    user = Users.query.get(user_id)
    if query:
        results = Items.query.filter(Items.name.ilike(f"%{query}%")).all()
    else:
        results = []

    return render_template('results.html', user=user, results=results, query=query)