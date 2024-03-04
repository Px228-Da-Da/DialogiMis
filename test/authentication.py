# import pyrebase

config = {
    'apiKey': "AIzaSyBJVECLZ5_7BOrBRjl8yVk1lz7AP1Q3Ot4",
    'authDomain': "dialogimis.firebaseapp.com",
    'projectId': "dialogimis",
    'storageBucket': "dialogimis.appspot.com",
    'messagingSenderId': "561942559385",
    'appId': "1:561942559385:web:a44b7192b9deb8ab899608",
    'measurementId': "G-P26HK6H3WP",
    'databaseURL': 'https://dialogimis-default-rtdb.firebaseio.com/'
}

# firebase = pyrebase.initialize_app(config)
# auth = firebase.auth()

# email = 'leka55mapket@gmail.com'
# password = '1q2w3e4r5t6y7uJjd373'  # password > 6

# # user = auth.create_user_with_email_and_password(email, password)
# # print(user)

# user = auth.sign_in_with_email_and_password(email, password)

# # Send a password reset email
# # auth.send_password_reset_email(email)
# auth.send_email_verification(user['idToken'])
import pyrebase
import time


firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

# Function to handle user signup and verification
def signup_and_verify_email():
    email = input("Enter your email: ")
    password = input("Enter your password (must be at least 6 characters long): ")
    username = input("Enter your username: ")
    additional_password = input("Enter an additional password for login: ")

    if len(password) < 6:
        print("Password must be at least 6 characters long.")
        return

    try:
        # Create the user with email and password
        user = auth.create_user_with_email_and_password(email, password)
        print("User created successfully.")

        # Send a verification email
        auth.send_email_verification(user['idToken'])
        print("Verification email sent. Please check your inbox and verify your email address.")

        # Store additional user information in the database
        user_data = {
            'email': email,
            'username': username,
            'password': password,
            'additional_password': additional_password
        }
        db.child('users').child(user['localId']).set(user_data)

        # Wait for email verification
        while True:
            time.sleep(5)  # Check every 5 seconds
            try:
                user_info = auth.get_account_info(user['idToken'])
                email_verified = user_info['users'][0]['emailVerified']
                if email_verified:
                    print("Email verified successfully.")
                    break
                else:
                    print("Email not yet verified. Waiting...")
            except Exception as e:
                print("Error:", e)
                break

    except Exception as e:
        if "EMAIL_EXISTS" in str(e):
            print("The email address is already in use. Please use a different email address.")
        else:
            print("Error:", e)

# Sign up and verify email
signup_and_verify_email()
