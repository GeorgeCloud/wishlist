from flask import Flask, render_template, request, url_for, redirect, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sdlfms'

uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/Wishlist')
client = MongoClient(uri)
db = client.get_default_database()

users = db.users
products = db.products


def create_product_document(request_form):
    return {
        'owner_username': request_form['owner'],
        'name': request_form['name'],
        'description': request_form['description'],
        'rating': 0,
        'last_modified': datetime.now(),
    }

@app.route('/', methods=['GET'])
def home():
    # users.delete_many({})
    # products.delete_many({})
    return redirect(url_for('index_products'))

@app.route('/products', methods=['GET'])
def index_products():
    # products.insert_one(product)
    all_products = products.find({})  # fetch 12

    return render_template('index_products.html', products=all_products)

@app.route('/products/new', methods=['GET'])
def new_product():
    return render_template('new_product.html', product='', title="New Product")

@app.route('/products/create', methods=['POST'])
def submit_product():
    username = request.form['owner']
    user = users.find_one({'_id': username})

    if user:
        product_document = create_product_document(request.form)
        products.insert_one(product_document)
    else:
        flash(f'{username} does not exist')
        return redirect(url_for('new_product'))

    return redirect(url_for('show_user', username=username))

@app.route('/products/<product_id>', methods=['GET'])
def show_product(product_id):
    product = products.find_one({'_id': ObjectId(product_id)})

    return render_template('show_product.html', product=product)
#
@app.route('/products/<playlist_id>/edit', methods=['GET'])
def product_edit(product_id):
    product = products.find_one({'_id': ObjectId(product_id)})
    return render_template('playlists_edit.html', product=product, title="Edit Product")

@app.route('/products/<product_id>/delete')
def playlist_delete(product_id):
    products.delete_one({'_id': ObjectId(product_id)})
    return redirect(url_for('index_products'))

@app.route('/users', methods=['GET'])
def index_users():
    all_users = users.find({})  # fetch 12

    return render_template('index_users.html', users=all_users)

@app.route('/users/new', methods=['GET'])
def new_user():
    return render_template('new_user.html', user='', title="New user")

@app.route('/users/create', methods=['POST'])
def submit_user():
    username = users.insert_one({
        '_id': request.form['username'].lower()
    }).inserted_id

    return redirect(url_for('show_user', username=username))

@app.route('/users/<username>', methods=['GET'])
def show_user(username):
    user = users.find_one({'_id': username})
    user_products = products.find({'owner_username': username})

    return render_template('show_user.html', user=user, products=user_products)

@app.route('/users/<username>/edit', methods=['GET'])
def user_edit(username):
    user = users.find_one({'_id': username})
    return render_template('edit_user.html', user=user, title="Edit User")

@app.route('/users/<username>/delete')
def user_delete(username):
    users.delete_one({'_id': username})
    return redirect(url_for('index_users'))


if __name__ == '__main__':
    app.run(port=5001, debug=True)
