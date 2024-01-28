import json
from math import floor
from MySQLdb import IntegrityError
from flask import Flask, jsonify, redirect, render_template, request,session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from icecream import ic
from datetime import datetime,timedelta
import bcrypt
import mysql.connector
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os

from sqlalchemy import null
from app import hash_password

# create the db
con = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "1234"
)
cur = con.cursor()
# make a new schema called library using basic SQL 
new_schema = 'library'
schema_query = f"CREATE DATABASE IF NOT EXISTS {new_schema}"
cur.execute(schema_query)
con.commit()


# config the app 
app = Flask(__name__)
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:1234@localhost/library"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "FUCKthatSHIT"
CORS(app)
secret_key = app.config["JWT_SECRET_KEY"]
db = SQLAlchemy(app)

# create models
class Book(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(50),nullable = False,unique = True)
    author = db.Column(db.String(50),nullable = False)
    year_published = db.Column(db.Integer,nullable = False)
    type = db.Column(db.Integer,nullable = False)
    book_cover = db.Column(db.String(200),default = "url_for_placeholder")
    # i made a connection/relationship between the book and the loan table 
    loans = db.relationship("Loan",backref = "book")
    # this helps view the book when we call on it 
     

# create model customer 
class Customer(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(50),nullable = False)
    email =db.Column(db.String(100),nullable = False,unique = True) 
    password = db.Column(db.String(500),nullable = False)
    salt = db.Column(db.LargeBinary,nullable = False)
    city  = db.Column(db.String(50),nullable = False)
    age = db.Column(db.Integer,nullable = False)
    role = db.Column(db.Integer,nullable = False)
    #connect to loans and enable the loan object created to reach the corresponding customer's data 
    loans = db.relationship("Loan",backref = "customer")
   
# create a model loan that uses the id columns of book and customer to connect the schema
class Loan(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    custID = db.Column(db.Integer,db.ForeignKey('customer.id'),nullable = False)
    bookID = db.Column(db.Integer,db.ForeignKey('book.id'),nullable = False)
    loan_date = db.Column(db.Date, default =datetime.now(),nullable = False)
    return_date = db.Column(db.Date) 

    def __init__(self,custID,bookID):
        loaned_book = Book.query.get(bookID)
        book_type = loaned_book.type
        if book_type == 1:
            self.return_date= datetime.now() + timedelta(days = 10) 
        if book_type == 2:
            self.return_date= datetime.now() + timedelta(days = 5)
        if book_type == 3:
            self.return_date= datetime.now() + timedelta(days = 2)
        super().__init__(custID =custID,bookID = bookID)
        ic(self.id, self.return_date)

 

def main():
    msg = """have fun /('u')/   \('u')/  /('u')/"""
    
    ic(msg)
    


def create_db_entrys():
    book1 = Book(name = "name of the wind",author = "Patrick Rothfuss",year_published = "2007",type = 1,book_cover = "https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcRi04lvVxkzBg5gQMcefq5DPusDxvJWCS1v4NCqw6nWLhKNw7Ah")
    book2 = Book(name = "wise mans fear",author = "Patrick Rothfuss",year_published = "2011",type = 2,book_cover = "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcT5x2Z02xkKLn-c4Nlgag46lHXn1nbwR9_aN3aMfqO2vjxM3LEi")
    book3 = Book(name = "silent things",author = "Patrick Rothfuss",year_published = "2014",type = 3,book_cover = "https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcS0nfkSNGgmJf4m2fb_b0XUpdS4wW-otyv3kgd2V5XvbMUlsoYb")
    salt1,pwd1 = hash_password("123")
    salt2,pwd2 = hash_password("123")
    salt3,pwd3 = hash_password("123")
    new_customer1 = Customer(name = "avi",email = "mail1",password = pwd1,salt = salt1,city = "Reashon Lezion",age = 25,role = 1)
    new_customer2 = Customer(name = "aviel",email = "mail2",password = pwd2,salt = salt2,city = "Tel Aviv",age = 12,role = 1)
    new_customer3 = Customer(name = "avigail",email = "mail3",password = pwd3,salt = salt3,city = "Yavne",age = 32,role = 1)
    db.session.add(book1)
    db.session.add(book2)
    db.session.add(book3)
    db.session.add(new_customer1)
    db.session.add(new_customer2)
    db.session.add(new_customer3)
    db.session.commit()
    new_loan1 = Loan(custID =new_customer1.id,bookID = book1.id)
    new_loan2 = Loan(custID =new_customer1.id,bookID = book2.id)
    new_loan3 = Loan(custID =new_customer1.id,bookID = book3.id)
    new_loan4 = Loan(custID =new_customer2.id,bookID = book2.id)
    new_loan5 = Loan(custID =new_customer2.id,bookID = book2.id)
    new_loan6 = Loan(custID =new_customer2.id,bookID = book3.id)
    new_loan7 = Loan(custID =new_customer3.id,bookID = book3.id)
    db.session.add(new_loan1)
    db.session.add(new_loan2)
    db.session.add(new_loan3)
    db.session.add(new_loan4)
    db.session.add(new_loan5)
    db.session.add(new_loan6)
    db.session.add(new_loan7)
    db.session.commit()
    # making some loans late 
    loan1 = Loan.query.get(1)
    loan2 = Loan.query.get(2)
    loan3 = Loan.query.get(3)
    ic(loan1.id)
    ic(loan2.return_date)
    ic(loan3)
    loan1.return_date = datetime.now()
    loan2.return_date = datetime.now()
    loan3.return_date = datetime.now()
    ic(loan1.return_date)
    ic(loan2.id)
    ic(loan3)
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
            db.create_all()
            create_db_entrys()
    main()