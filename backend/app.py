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

# # connect to the mysql workbench  
# con = mysql.connector.connect(
#     host = "localhost",
#     user = "root",
#     password = "1234"
# )
# cur = con.cursor()
# # make a new schema called library using basic SQL 
# new_schema = 'library'
# schema_query = f"CREATE DATABASE IF NOT EXISTS {new_schema}"
# cur.execute(schema_query)
# con.commit()


# connecting my app to flask and to the mysql database that we just created 
app = Flask(__name__)
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///yourdatabase.db'
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
    db.create_all()
    return "this will be nice eventualy"




@app.route('/add_book', methods=['POST'])
def add_book():
    # Get form data
    book_name = request.form.get('name')
    author = request.form.get('author')
    year_published = request.form.get('year_published')
    book_type = request.form.get('type')
    existing_book = Book.query.filter_by(name=book_name).first()

    if existing_book:
        # check for overlaping book names (no there are no two similarly named books...)
        return {"message": "this book is already registered"}
    
    if 'book_cover' not in request.files:
    # Check if the POST request has the file part
        return jsonify({"error":"there is no uploaded file"}),400
    file = request.files['book_cover']
 
    if file.filename == '':
    # If the user does not select a file, the browser might submit an empty file
        return jsonify({'error': 'No selected file'}), 400

        

    # Generate a unique  identifier for the file (book name is a unique field)
    unique_filename = f"{book_name}_cover_pic.jpg"

    # Save the file to the upload folder with the unique filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
    new_book = Book(name = book_name,author = author,year_published = year_published,type = book_type,book_cover = unique_filename)
    db.session.add(new_book)
    db.session.commit()
    # Additional logic for saving book details to a database or performing other actions
    # ...
    return jsonify({'message': 'Book added successfully', 'filename': unique_filename}), 200
     
    



@app.route("/signup", methods = ["GET","POST"])
def signup():
    if request.method == "POST":
        customer_name = request.json["name"]
        email = request.json["email"]
        salt,password = hash_password(request.json["password"])
        city = request.json["city"]    
        age = request.json["age"]
        
        if Customer.query.filter_by(email = email).count() > 0:
            return{"message":"email already in use"}
        new_customer = Customer(name = customer_name,email = email,password = password,salt = salt,city = city,age = age,role = request.json["role"])
        db.session.add(new_customer)
        db.session.commit()
        return {"message": "customer added successfuly" }
    return {"message: whould you like to register to our library?"}


@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "POST":
        # i made the login with the email field because it is unique
        email = request.json["email"]
        password = request.json["password"]

        customer = Customer.query.filter_by(email = email).first()
        if customer:
            pwd = customer.password
            salt = customer.salt
            # cheking the password given using the customers unique salt and comparing to the saved password
            trash,hashed_password = hash_password(password,salt) 
            hashed_password_str = hashed_password.decode("utf-8")
            if pwd == hashed_password_str:
                # providing an access token and some basic credentials to the client for use 
                access_token = create_access_token(identity=email)
                output = {"access_token":access_token,"message":f"logged in successfully hello {customer.name}","customer_name":customer.name}
                return jsonify(output)

        return {"message": "email or password not correct" }

        
    return {"message": "whould you like to register to our library?"}



@app.route("/make_loan", methods = ["POST"])
@jwt_required()
def make_loan():
    book_name = request.json["book_name"]
    # checking if the customer is logged in so that i can loan on his name 
    email = ic(get_jwt_identity())
    customer = Customer.query.filter_by(email = email).first()
    book_to_loan = Book.query.filter_by(name = book_name).first()

    if book_to_loan and customer:
        new_loan = Loan(custID =customer.id,bookID = book_to_loan.id)
        db.session.add(new_loan)
        db.session.commit()
        return {"message": f"you have made a loan on {book_to_loan.name} please return the book by {new_loan.return_date}" }
    else:
        return{"message":"we are sorry we can not make that loan"}


@app.route("/books_in_stock")
def all_books():
    listed_books = Book.query.all()
    list = []
    # for each book in the db i add its info to a list and then return it to client 
    for book in listed_books:
        list.append({"book_name":book.name,
                     "author":book.author,
                     "type":book.type,
                     "book_id":book.id,
                     "book_cover":book.book_cover})
    return jsonify(list)


@app.route("/loans")
def all_laons():
    # getting all the loans to temp 
    temp = Loan.query.all()
    #  macking different lists for late and not late loans
    list_of_loans = []
    late_loans = []
    # looping on all the loans 
    for loan in temp:
        # extracting the needed info 
        customer = Customer.query.get(loan.custID)
        loaned_book = Book.query.get(loan.bookID)
        loan.return_date  = datetime.combine(loan.return_date, datetime.min.time())
        difference = datetime.now() - loan.return_date
        time_left = floor(difference.total_seconds()/(60*60*24))
        # adding the logic to divide to two lists 
        if loan.return_date > datetime.now():
            list_of_loans.append({"loan_id":loan.id,"customer_name":customer.name,"book_name":loaned_book.name,"time_left":f"{-time_left} days"})
        else:
            late_loans.append({"loan_id":loan.id,"customer_name":customer.name,"book_name":loaned_book.name,"time_left":f"{time_left} days"})
        
    result = {
        "list_of_loans":list_of_loans,
        "late_loans": late_loans
    }
    # returning the  divided list
    return jsonify(result)



@app.route("/customers")
def show_customers():
    temp = Customer.query.all()
    customers = []
    for customer in temp:
        # creating an enry for each customer 
        customers.append({"id":customer.id,
                          "customer_name":customer.name,
                          "email":customer.email,
                          "city":customer.city,
                          "age":customer.age})
    
    return jsonify(customers)


# this method is irrelevent but im too afraid to delete it 
# plus im a little sentimental cause i wrote it from scratch and its obseleat now ...
@app.route("/return_book",methods = ["DELETE","POST"])
def book_update():
    # extracting info
    book_to_return = Book.query.filter_by(name = request.json["book_name"]).first()
    returning_customer = Customer.query.filter_by(email = request.json["email"]).first()
    loan = Loan.query.filter_by(bookID = book_to_return.id,custID = returning_customer.id).first()
    # macking sure they actually exist in the db 
    if book_to_return and returning_customer and loan:    
        number_of_loans = Loan.query.filter_by(bookID = book_to_return.id,custID = returning_customer.id).count()

        # find out what to do with that list tho...
        if number_of_loans > 1:
            ic("more then one loan")
            list_of_loans = Loan.query.filter_by(bookID = book_to_return.id,custID = returning_customer.id).all() 
            loans = [] 
            for loan in list_of_loans:
                book_to_return = Book.query.get(loan.bookID)
                returning_customer = Customer.query.get(loan.custID)
                # db.session.delete(loan)
                # db.session.commit()
                loans.append({"book_name":book_to_return.name,"returning_customer":returning_customer.name,"return_date":loan.return_date,"loan_id":loan.id})
                
            return jsonify(loans)

        else:
            loan = Loan.query.filter_by(bookID = book_to_return.id,custID = returning_customer.id).first()
            ic(loan)
            db.session.delete(loan)
            db.session.commit()
            return {"message":f"{book_to_return.name} returned by {returning_customer.name} successfuly"}
    else:
        return {"message":"there is no such loan here" }
    

    # /delete_loan_by_id
@app.route("/delete_loan_by_id/<int:loan_id>",methods = ["DELETE"])
def delete_loan_by_id(loan_id):
    ic(loan_id)
    loan_to_del = Loan.query.get(loan_id)
    ic(loan_to_del)
    msg = f"the loan by {loan_to_del.customer.name} on the book {loan_to_del.book.name} has been resolved"
    db.session.delete(loan_to_del)
    db.session.commit()
    return {"message":msg}


@app.route("/find_book",methods = ["POST","GET"])
def find_book():
    if request.method == "POST":    
        book_name = request.json["book_name"]
        books_to_find = Book.query.filter_by(name = book_name).all()
        # macking sure the book exists
        if len(books_to_find) == 0:
            return  {"message":"book not found"}
        output = []
        # making a list and adding relevent books to it  
        for book in books_to_find: 
            # ic(book)
            output.append({"book_name":book.name,"author":book.author,"year_published":book.year_published,"book_id":book.id,"book_cover":book.book_cover})
            ic(output)
        # return the list
        return jsonify(output)
    # returm the user back to home page
    return render_template("index.html")

@app.route("/edit_customer",methods = ["PUT","GET"])
def edit_customer():
    if request.method == "PUT":
        customer_to_edit = request.json["customer_id"]
        edited_customer = Customer.query.get(customer_to_edit)
        # finding the custoemr in the db
        if edited_customer:
            new_email = request.json["new_email"]
            # making sure the input value of email is not taken
            invalid_email = Customer.query.filter_by(email = new_email).first()
            if invalid_email:
                if invalid_email.id != customer_to_edit:
                    return {"message":"this email is already in use"}   
            # editing the relevent fields if there is no input the field should remain the same 
            new_name = request.json["new_name"]
            new_city =request.json["new_city"]
            new_age =request.json["new_age"]
            new_password = request.json["new_password"]
            if new_name !="":
                edited_customer.name = new_name
            if new_city !="":
                edited_customer.city = new_city
            if new_age !="":            
                edited_customer.age = new_age
            if new_email != "":
                edited_customer.email = new_email
            if new_password != "":
                edited_customer.email = new_email
            db.session.commit()
            return {"message":"customer edited successfuly"}
        return {"message":"no such customer here"}
    # gives instructions when first called 
    return {"message":"to edit a customer, input his new information in the relevent fields and press submit"}


@app.route("/edit_book",methods = ["PUT"])
def edit_book():
    ic("in edit")
    book_id = request.json["book_id"]
    exiting_name = Book.query.filter_by(name = request.json["new_name"]).first()
    # checking if the name that they are trying to input is not taken by a different book
    if exiting_name:    
        # making sure not to raise an error if they just dont want to change the name of the edited book 
        if exiting_name.id != book_id:
            return{"message":"the book name your trying to input is already taken"}
    edited_book = Book.query.get(book_id)
    
    new_name = request.form.get["new_name"]
    new_author = request.form.get["new_author"]
    new_year_published = request.form.get["new_year_published"]
    new_type = request.form.get["new_type"]

    ic(new_type,new_year_published,new_author,new_name)
        
    if 'book_cover' not in request.files:
    # Check if the POST request has the file part
        return jsonify({"error":"there is no uploaded file"}),400
    if file.filename == '':
    # If the user does not select a file, the browser might submit an empty file
        return jsonify({'error': 'No selected file'}), 400
    file = request.files['book_cover']
    # Generate a unique  identifier for the file (book name is a unique field)
    unique_filename = f"{new_name}_cover_pic.jpg"
    # Save the file to the upload folder with the unique filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

            # editing the relevent fields if there is no input the field should remain the same 
    if new_name != "":
        edited_book.name = new_name
    if new_author != "":
        edited_book.author = new_author
    if new_year_published != "":
        edited_book.year_published = new_year_published
    if new_type != "":
        edited_book.type = new_type

    db.session.commit()
    return {"message":"book edited successfuly"}
    

# self explanitory
@app.route("/find_customer_by_id",methods = ["POST","GET"])
def find_customer_by_id():
    customer = request.json["customer_id"]
    customer = Customer.query.get(customer)
    
    if not customer:
        return {"message":"no such customer here "}
    output ={"customer_id":customer.id,
            "customer_name":customer.name,
            "city":customer.city,
            "age":customer.age ,
            "email":customer.email}
    ic(output)
    return jsonify(output)


@app.route("/get_logged_customer", methods=["POST", "GET"])
@jwt_required()
def get_logged_customer():
    email = ic(get_jwt_identity())
    customer = Customer.query.filter_by(email=email).first()  # Use .first() to get the first result
    if not customer:
        return {"message": "no such customer here "}
    output = {
        "customer_id": customer.id,
        "customer_name": customer.name,
        "city": customer.city,
        "age": customer.age,
        "email": customer.email
    }
    ic(output)
    return jsonify(output)

@app.route("/find_customer",methods = ["POST","GET"])
def find_customer():
    customer = request.json["customer_name"]
    customer = Customer.query.filter_by(name = customer).all()
    customers_searched = []
    for customer in customer:
        customers_searched.append({"customer_id":customer.id,
                                   "customer_name":customer.name,
                                   "city":customer.city,
                                   "age":customer.age ,
                                   "email":customer.email})
    ic(customers_searched)
    if len(customers_searched )== 0:
        return {"message":"no such customer here "}
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
            return {"message":"there are active loans on this book are you sure you whold like to remove it ?"}
            # pop up a message to the client with yes or no options if no cancel the removal  
            # add option to delete the loans if user chooses to 
        db.session.delete(book_to_remove)
        db.session.commit()
        return {"message":"book removed successfully"}
    else:
        return{"message":"no such book here"}


# i need to make a query to the client that indicates if he whants to delete all associated loans as well
@app.route("/remove_customer",methods = ["DELETE"])
def remove_customer():
    customer_to_remove = request.json["customer_name"]
    customer_to_remove = Customer.query.filter_by(name = customer_to_remove).first()
    if customer_to_remove:
        existing_loans = Loan.query.filter_by(custID = customer_to_remove.id).all()
        if len(existing_loans)>0:
            return {"message":"there are ongoing loans for this customer whold you like to resolve them all ? "}
            # pop up a message to the client with yes or no options if no cancel the removal  
            # if yes delete all loans on the users name and then remove him 
        db.session.delete(customer_to_remove)
        db.session.commit()
        return {"message":"customer removed successfully"}
    else:
        return{"message":"no such customer here"}



@app.route("/delete_book_by_id/<int:book_id>",methods = ["DELETE","GET"])
def delete_book_by_id(book_id):
    ic(book_id)
    book_to_del = Book.query.get(book_id)
    list_of_loans = Loan.query.filter_by(bookID = book_to_del.id).all()
    if book_to_del and len(list_of_loans )> 0 and request.method == "GET":
        ic("i found loans on the book")
        message = {
            "message": "There are active loans on this book. Do you want to remove it and delete the associated loans?",
            "options": [
                {"label": "Yes", "value": "delete_loans"},
                {"label": "No", "value": "cancel_removal"}
            ]
        }
        return message
    
    if book_to_del and request.method == "DELETE":
        for loan in list_of_loans:
            db.session.delete(loan)            
        db.session.delete(book_to_del)
        db.session.commit()
    
        return {"message":"book removed successfully asotiated loans were resolved"}    
    else:
        ic("i didn't found loans on the book")
        return{"message":"no such book here"}
    

@app.route(f"/delete_customer_by_id/<int:customer_id>",methods = ["DELETE","GET"])
def delete_customer_by_id(customer_id):
    customer_to_del = Customer.query.get(customer_id)
    list_of_loans = Loan.query.filter_by(custID = customer_to_del.id).all()
    if request.method == "GET" and customer_to_del:
        if len(list_of_loans)> 0:
            
            message = {
                "message": "There are active loans on this customer. Do you want to remove it and delete the associated loans?",
                "options": [
                    {"label": "Yes", "value": "delete_loans"},
                    {"label": "No", "value": "cancel_removal"}
                ]
            }
            return message


    if customer_to_del and request.method == "DELETE":
        for loan in list_of_loans:
            db.session.delete(loan)            
        db.session.delete(customer_to_del)
        db.session.commit()
    
        return {"message":"customer removed successfully asotiated loans were resolved"}    
    else:
        return{"message":"no such customer here"}
    


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
    os.system('cls')