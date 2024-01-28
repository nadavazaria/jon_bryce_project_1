markdown
Copy code
# Welcome to My Library

## Getting Started

To get started, clone this Git repository using the following command:

```cmd
git clone https://github.com/nadavazaria/jon_bryce_project_1.git
```
Create a virtual environment:

```cmd
py -m venv env
```
Activate the virtual environment:

```cmd
env\Scripts\activate
```
Install the required dependencies:

```cmd
pip install -r requirements.txt
```
## connecting your db
   in order to connect to the db please enter your mysql credentials into the test.py file inside of backend
   lines 19 -21
   after doing so run test.py to create the db and a few basic entrys to the bd 
   ```cmd
    py test.py
```
   and then run app.py to start the server  
   ```cmd
       py app.py
``` 
## Pages content
    There are four main web pages associated with my library:
    Index: Home page for customers
    Login: Login page
    Books: A place for an admin to view, add, and edit books
    Customers: A place for an admin to add new customers and manage existing ones

### List of Actions
    Books
        Add Book - a picture file is required to submit the book 
        Books in Stock
        Search Book
        Edit Book
        Delete Book
        Make Loan (restricted, requires login)
        Print Loans
        Delete Loan
    Customers
        Sign Up
        Login
        Print Customers
        Search Customer
        Edit Customer
        Delete Customer
    Index
        Login
        Show Books
        Search Book
        Make Loan (restricted)
        Delete Loan (restricted)
        Get Logged Customer (restricted, requires login)
        Show Logged Customer Loans (restricted, requires login)
    login
        submit login details
        back to index page after successful login
