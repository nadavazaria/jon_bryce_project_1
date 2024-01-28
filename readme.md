markdown
Copy code
# Welcome to My Library

## Getting Started

To get started, clone this Git repository using the following command:

```bash
git clone [git_url]
Create a virtual environment:

bash
Copy code
py -m venv env
Activate the virtual environment:

bash
Copy code
env\Scripts\activate
Install the required dependencies:

bash
Copy code
pip install -r requirements.txt

```
## connecting your db
    to connect a mysql db pleas remove the notaition mark 
    from lines 14 - 25
    in lines 16 17 18 submit your mtsql credentials
    same for line 32

## Pages
    There are four main web pages associated with my library:

    Index: Home page for customers
    Login: Login page
    Books: A place for an admin to view, add, and edit books
    Customers: A place for an admin to add new customers and manage existing ones
### Methods
    All the methods are listed as buttons on the web pages, designed to be intuitive and easy to use. I recommend exploring the web pages to familiarize yourself with the functionality. For testing purposes, there is a test.py file that you can run to create a few books and customers. To view their email addresses on the web page, navigate to "Customers" using the navbar at the top of the page (the dog picture links to index.html), and then display them on the screen using the button. The password for all of them is '123'.

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