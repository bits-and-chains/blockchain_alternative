from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()


# Customer maps to the "customers" table.
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Order maps to the "orders" table.
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    subtotal = db.Column(db.DECIMAL(18, 2))

    #customer = db.relationship('customer', backref=db.backref('posts', lazy='dynamic'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))

    def as_dict(self):
        return {
            'id': self.id,
            'subtotal': str(self.subtotal),
            'customer_id': self.customer_id,
        }


# Product maps to the "products" table.
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    price = db.Column(db.DECIMAL(18, 2))

    def as_dict(self):
        return {'id': self.id, 'name': self.name, 'price': str(self.price)}


# order_products_table is a many-to-many table mapping Orders to Products.
order_products_table = db.Table(
    'order_products', db.metadata,
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id')))
