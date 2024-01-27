from datetime import datetime, timedelta
from icecream import ic
import bcrypt
import os
def main():

  def hash_password(password):
      password = str(password)
      
      hashed_password = bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt())
      ic (hashed_password)
      return hashed_password

  ic(os.urandom(32))
from flask import Flask, request, jsonify
import os
import uuid  # Import the UUID library for generating unique identifiers

app = Flask(__name__)

# Define the upload folder
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route for adding a book with a picture
@app.route('/add_book', methods=['POST'])
def add_book():
    # Get form data
    book_name = request.form.get('name')
    author = request.form.get('author')
    year_published = request.form.get('year_published')
    book_type = request.form.get('type')
    
    
    if 'book_cover' not in request.files:
    # Check if the POST request has the file part
        return jsonify({"error":"there is no uploaded file"}),400
 
    if file.filename == '':
    # If the user does not select a file, the browser might submit an empty file
        return jsonify({'error': 'No selected file'}), 400

    file = request.files['book_cover']
        

    # Generate a unique  identifier for the file (book name is a unique field)
    unique_filename = f"{book_name}_cover_pic"

    # Save the file to the upload folder with the unique filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
    new_book = Book(name = book_name,author = author,year_published = year_published,book_type = book_type,book_cover = book_cover)
    db.session.add(new_book)
    # Additional logic for saving book details to a database or performing other actions
    # ...
    return jsonify({'message': 'Book added successfully', 'filename': unique_filename}), 200

    # Return a success response

if __name__ == '__main__':
    app.run(debug=True)



if __name__ == "__main__":
    main()