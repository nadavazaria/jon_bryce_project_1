from datetime import datetime, timedelta
from icecream import ic
import bcrypt
def main():

  def hash_password(password):
      password = str(password)
      
      hashed_password = bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt())
      ic (hashed_password)
      return hashed_password

  ic(hash_password(1234))
  
if __name__ == "__main__":
    main()