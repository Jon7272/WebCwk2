from app import db

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(500), index=True, unique=True)
    password = db.Column(db.String(500))

    def __repr__(self):
            return '{}{}{}'.format(self.id, self.username, self.password)
 
class Items(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.String(500), unique=True)
      price = db.Column(db.Double)
      stock = db.Column(db.Integer)
      category = db.Column(db.String(500))

      def __repr__(self):
            return '{}{}{}{}'.format(self.id, self.name, self.price, self.stock)

class Basket(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
      item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
      quantity = db.Column(db.Integer, nullable=False, default=1)
      name = db.Column(db.String(500))
      price = db.Column(db.Double)

      user = db.relationship('Users', backref=db.backref('baskets', lazy='dynamic'))
      item = db.relationship('Items', backref=db.backref('baskets', lazy='dynamic'))

      def __repr__(self):
            return '{}{}{}{}{}{}'.format(self.id, self.user_id, self.item_id, self.quantity, self.name, self.price)

      

