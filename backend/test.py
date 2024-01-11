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
if __name__ == "__main__":
    main()