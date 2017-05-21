from __future__ import print_function

# Import Flask code.
from flask import Flask, Response, request

# Import SQLAlchemy code.
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.orm

# This import isn't actually referenced directly below but is included to
# clearly indicate whether the CockroachDB dialect is missing.
import cockroachdb

from models import db, Customer, Order, Product

import argparse
from decimal import Decimal
import json
import logging
import os

# Flask WTF forms
from flask import (Flask, session, redirect, url_for, abort,
                   render_template, flash)
from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, ValidationError

# Configuration
DEFAULT_URL = "cockroachdb://root@localhost:26257/company?sslmode=disable"
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# Setup and return Flask app.
def setup_app():
    # Setup Flask app.
    app = Flask(__name__)
    app.config.from_pyfile('server.cfg')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("ADDR", DEFAULT_URL)
    app.debug = False

    # Disable log messages, which are outputted to stderr and treated as errors
    # by the test driver.
    if not app.debug:
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

    # Initialize flask-sqlachemy.
    db.init_app(app)
    with app.test_request_context():
        db.create_all()

    return app

app = setup_app()

## Setting Up the Form
class EntryForm(FlaskForm):

    title = TextField("Title")
    text = TextAreaField("Text")
    submit = SubmitField("Share")

@app.route('/')
def product_form():
    return render_template('form.html')


@app.route('/ping')
def ping():
    return 'The beginnings of Alt-blockchain App'


# The following functions respond to various HTTP routes, as described in the
# top-level README.md.

@app.route('/customer', methods=['GET'])
def get_customers():
    customers = [c.as_dict() for c in Customer.query.all()]
    return Response(json.dumps(customers), 200,
                    mimetype="application/json; charset=UTF-8")


@app.route('/customer', methods=['POST'])
def create_customer():
    try:
        body = request.stream.read().decode('utf-8')
        data = json.loads(body)
        customer = Customer(id=data.get('id'), name=data['name'])
        db.session.add(customer)
        db.session.commit()
    except (ValueError, KeyError) as e:
        return Response(str(e), 400)
    return body


@app.route('/customer/<id>', methods=['GET'])
def get_customer(id=None):
    if id is None:
        return Response('no ID specified', 400)
    customer = db.session.query(Customer).get(int(id))
    return Response(json.dumps(customer.as_dict()), 200,
                    mimetype="application/json; charset=UTF-8")


@app.route('/order', methods=['GET'])
def get_orders():
    orders = [o.as_dict() for o in Order.query.all()]
    return Response(json.dumps(orders), 200,
                    mimetype="application/json; charset=UTF-8")


@app.route('/order', methods=['POST'])
def create_order():
    try:
        body = request.stream.read().decode('utf-8')
        data = json.loads(body)
        order = Order(
            id=data.get('id'),
            subtotal=Decimal(data['subtotal']),
            customer_id=data['customer']['id'])
        db.session.add(order)
        db.session.commit()
    except (ValueError, KeyError) as e:
        return Response(str(e), 400)
    return body


@app.route('/order/<id>', methods=['GET'])
def get_order(id=None):
    if id is None:
        return Response('no ID specified', 400)
    order = db.session.query(Order).get(int(id))
    return Response(json.dumps(order.as_dict()), 200,
                    mimetype="application/json; charset=UTF-8")


@app.route('/product', methods=['GET'])
def get_products():
    products = [p.as_dict() for p in Product.query.all()]
    return Response(json.dumps(products), 200,
                    mimetype="application/json; charset=UTF-8")


@app.route('/product', methods=['POST'])
def create_product():
    try:
        body = request.stream.read().decode('utf-8')
        data = json.loads(body)
        product = Product(id=data.get('id'), name=data['name'], price=Decimal(data['price']))
        db.session.add(product)
        db.session.commit()
    except (ValueError, KeyError) as e:
        return Response(str(e), 400)
    return body


@app.route('/product/<id>', methods=['GET'])
def get_product(id=None):
    if id is None:
        return Response('no ID specified', 400)
    product = db.session.query(Product).get(int(id))
    return Response(json.dumps(product.as_dict()), 200,
                    mimetype="application/json; charset=UTF-8")


def main():
    parser = argparse.ArgumentParser(
        description='Test SQLAlchemy compatibility with CockroachDB.')
    parser.add_argument('--port', dest='port', type=int,
                        help='server listen port', default=6543)
    args = parser.parse_args()
    print('listening on port %d' % args.port)
    app.run(host='localhost', port=args.port)


if __name__ == '__main__':
    main()