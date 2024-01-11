import json
from math import floor
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from icecream import ic
from datetime import datetime,timedelta
import bcrypt
import mysql.connector
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
# your mysql database credentials here 
host = '127.0.0.1'
user = 'root'
password = '1234'

# connect to the mysql workbench  
con = mysql.connector.connect(
    host = host,
    user = user,
    password = password
)
cur = con.cursor()
# make a new schema called library using basic SQL 
new_schema = 'library'
schema_query = f"CREATE DATABASE IF NOT EXISTS {new_schema}"
cur.execute(schema_query)
con.commit()


# connecting my app to flask and to the mysql database that we just created 
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:1234@localhost/library"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "FUCKthatSHIT"
CORS(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)
# create model book 
secret_key = app.config["JWT_SECRET_KEY"]




class Book(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(50),nullable = False,unique = True)
    author = db.Column(db.String(50),nullable = False)
    year_published = db.Column(db.Integer,nullable = False)
    type = db.Column(db.Integer,nullable = False)
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
          
        ic(book_type)
        if book_type == 1:
            self.return_date= datetime.now() + timedelta(days = 10) 
        if book_type == 2:
            self.return_date= datetime.now() + timedelta(days = 5)
        if book_type == 3:
            self.return_date= datetime.now() + timedelta(days = 2)
        super().__init__(custID =custID,bookID = bookID)



def hash_password(password,salt = None):
    # password = str(password)
    if salt == None:
        salt = bcrypt.gensalt()
    encrypted_pwd =password.encode("utf-8")
    hashed_password = bcrypt.hashpw(encrypted_pwd,salt)
    return salt,hashed_password

# macking the crud
@app.route("/")
def home_page():
    return "this will be nice eventualy"




@app.route("/add_book", methods = ["GET","POST"])
def add_book():
    if request.method == "POST":
        book_name = request.json["name"]
        author = request.json["author"]    
        year_published = request.json["year_published"]
        type = request.json["type"]
        new_book = Book(name = book_name,author = author,year_published = year_published,type = type)
        ic(new_book)
        db.session.add(new_book)
        db.session.commit()
        
        return {"messege": "book added successfuly" }
    return {"messege: please add a book"}



@app.route("/signup", methods = ["GET","POST"])
def signup():
    if request.method == "POST":
        customer_name = request.json["name"]
        email = request.json["email"]
        salt,password = hash_password(request.json["password"])
        city = request.json["city"]    
        age = request.json["age"]
        
        if Customer.query.filter_by(email = email).count() > 0:
            return{"messege":"email already in use"}
        new_customer = Customer(name = customer_name,email = email,password = password,salt = salt,city = city,age = age)
        db.session.add(new_customer)
        db.session.commit()
        return {"messege": "customer added successfuly" }
    return {"messege: whould you like to register to our library?"}

@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "POST":
        email = request.json["email"]
        password = request.json["password"]
        customer = Customer.query.filter_by(email = email).first()
        if customer:
            pwd = customer.password
            salt = customer.salt
            trash,hashed_password = hash_password(password,salt) 
            ic(hashed_password)
            ic(pwd)
            hashed_password_str = hashed_password.decode("utf-8")
            if pwd == hashed_password_str:
                access_token = create_access_token(identity=email)
                return jsonify({"access_token":access_token})

        return {"messege": "email or password not correct" }

        
    return {"messege": "whould you like to register to our library?"}



@app.route("/make_loan", methods = ["GET","POST"])
def make_loan():
    if request.method == "POST":
        book_name = request.json["book_name"]
        customer_name = request.json["customer_name"]
        customer = Customer.query.filter_by(name = customer_name ).first()
        book_to_loan = Book.query.filter_by(name = book_name ).first()
        if book_to_loan and customer:
            new_loan = Loan(custID =customer.id,bookID = book_to_loan.id)
            db.session.add(new_loan)
            db.session.commit()
            return {"messege": f"you have made a loan please return the book by {new_loan.return_date}" }
        else:
            return{"messege":"we are sorry we can not make that loan"}
    return {"messege: what book whould you like to loan? "}

@app.route("/books_in_stock")
def all_books():
    listed_books = Book.query.all()
    list = []
    for book in listed_books:
        list.append({"book_name":book.name,
                     "author":book.author,
                     "type":book.type})
    return jsonify(list)


@app.route("/loans")
def all_laons():
    temp = Loan.query.all()
    list_of_loans = []
    late_loans = []
    for loan in temp:
        customer = Customer.query.get(loan.custID)
        loaned_book = Book.query.get(loan.bookID)
        loan.return_date  = datetime.combine(loan.return_date, datetime.min.time())
        difference = datetime.now() - loan.return_date
        time_left = floor(difference.total_seconds()/(60*60*24))
        if loan.return_date > datetime.now():
            list_of_loans.append({"customer_name":customer.name,"book_name":loaned_book.name,"time_left":f"{-time_left} days"})
        else:
            late_loans.append({"customer_name":customer.name,"book_name":loaned_book.name,"late_by":f"{time_left} days"})
        
        result = {
            "list_of_loans":list_of_loans,
            "late_loans": late_loans
        }
    ic(result)
    return jsonify(result)



@app.route("/customers")
def show_customers():
    temp = Customer.query.all()
    customers = []
    for customer in temp:
        customers.append({"id":customer.id,
                          "customer_name":customer.name,
                          "email":customer.email,
                          "city":customer.city,
                          "age":customer.age})
    
    return jsonify(customers)



@app.route("/return_book",methods = ["DELETE"])
def book_update():
    book_to_return = Book.query.filter_by(name = request.json["book_name"]).first()
    returning_customer = Customer.query.filter_by(name = request.json["customer_name"]).first()
    loan = Loan.query.filter_by(bookID = book_to_return.id,custID = returning_customer.id).first()
    if book_to_return and returning_customer and loan:    
        number_of_loans = Loan.query.filter_by(bookID = book_to_return.id,custID = returning_customer.id).count()

        # find out what to do with that list tho...
        if number_of_loans > 1:
            list_of_loans = Loan.query.filter_by(bookID = book_to_return.id,custID = returning_customer.id).all() 
            loans = [] 
            for loan in list_of_loans:
                book_to_return = Book.query.get(loan.bookID)
                returning_customer = Customer.query.get(loan.custID)
                db.session.delete(loan)
                db.session.commit()
                loans.append({"book_name":book_to_return.name,"returning_customer":returning_customer.name,"return_date":loan.return_date})
                
            return jsonify(loans)

        else:
            loan = Loan.query.filter_by(bookID = book_to_return.id,custID = returning_customer.id).first()
            ic(loan)
            db.session.delete(loan)
            db.session.commit()
            return {"messege":f"{book_to_return.name} returned by {returning_customer.name} successfuly"}
    else:
        return {"messege":"there is no such loan here" }
    


@app.route("/find_book",methods = ["POST","GET"])
def find_book():
    book_to_find = request.json["book_name"]
    book_to_find = Book.query.filter_by(name = book_to_find).all()
    ic(book_to_find)
    books_to_find = []
    for book in book_to_find:
        book_name = book.name
        author = book.author
        year_published = book.year_published
        books_to_find.append({"book_name":book_name,"author":author,"year_published":year_published})
    if len(books_to_find) == 0:
        return {"messege":"no such books here"}
    return jsonify(books_to_find)

@app.route("/edit_customer",methods = ["PUT"])
def edit_customer():
    customer_to_edit = request.json["customer_name"]
    edited_customer = Customer.query.filter_by(name = customer_to_edit).first()
    if edited_customer:
        new_name = request.json["new_name"]
        new_city =request.json["new_city"]         
        new_age =request.json["new_age"]
        if new_name !="":
            edited_customer.name = new_name
        if new_city !="":
            edited_customer.city = new_city
        if new_age !="":            
            edited_customer.age = new_age
        db.session.commit()
        return {"messege":"customer edited successfuly"}
    return {"messege":"no such customer here"}

@app.route("/edit_book",methods = ["PUT"])
def edit_book():
    book_to_edit = request.json["book_name"]
    edited_book = Book.query.filter_by(name = book_to_edit).first()
    if edited_book:
        new_name = request.json["new_name"]
        new_author = request.json["new_author"]
        new_year_published = request.json["new_year_published"]
        new_type = request.json["new_type"]
        ic(new_type,new_year_published,new_author,new_name)
        if new_name != "":
            edited_book.name = new_name
        if new_author != "":
            edited_book.author = new_author
        if new_year_published != "":
            edited_book.year_published = new_year_published
        if new_type != "":
            edited_book.type = new_type
        db.session.commit()
        return {"messege":"book edited successfuly"}
    return{"messege":"no such book here"}


@app.route("/find_customer",methods = ["POST","GET"])
def find_customer():
    customer = request.json["customer_name"]
    customer = Customer.query.filter_by(name = customer).all()
    customers_searched = []
    for customer in customer:
        customer_id = customer.id
        customer_name = customer.name
        city = customer.city
        age = customer.age 
        customers_searched.append({"customer_id":customer_id,"customer_name":customer_name,"city":city,"age":age})
    ic(customers_searched)
    if len(customers_searched )== 0:
        return {"messege":"no such customer here "}
    return jsonify(customers_searched)


# i need to make a query to the client that indicates if he whants to delete all associatef loans ass well
@app.route("/remove_book",methods = ["DELETE"])
def remove_book():
    book_to_remove = request.json["book_name"]
    book_to_remove = Book.query.filter_by(name = book_to_remove).first()
    if book_to_remove:
        list_of_loans = Loan.query.filter_by(bookID = book_to_remove.id).all()
        ic(list_of_loans)
        if len(list_of_loans )> 0:
            return {"messege":"there are active loans on this book are you sure you whold like to remove it ?"}
            # pop up a messege to the client with yes or no options if no cancel the removal  
            # add option to delete the loans if user chooses to 
        db.session.delete(book_to_remove)
        db.session.commit()
        return {"messege":"book removed successfully"}
    else:
        return{"messege":"no such book here"}


# i need to make a query to the client that indicates if he whants to delete all associatef loans ass well
@app.route("/remove_customer",methods = ["DELETE"])
def remove_customer():
    customer_to_remove = request.json["customer_name"]
    customer_to_remove = Customer.query.filter_by(name = customer_to_remove).first()
    if customer_to_remove:
        existing_loans = Loan.query.filter_by(custID = customer_to_remove.id).all()
        if len(existing_loans)>0:
            return {"messege":"there are ongoing loans for this customer whold you like to resolve them all ? "}
            # pop up a messege to the client with yes or no options if no cancel the removal  
            # if yes delete all loans on the users name and then remove him 
        db.session.delete(customer_to_remove)
        db.session.commit()
        return {"messege":"customer removed successfully"}
    else:
        return{"messege":"no such customer here"}



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    os.system('cls')