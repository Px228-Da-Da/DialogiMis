# from flask import Flask, request, jsonify, url_for
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Путь к базе данных SQLite
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
# bcrypt = Bcrypt(app)

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(50), unique=True, nullable=False)
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String(100), nullable=False)

# @app.route('/api/register', methods=['POST'])
# def register():
#     data = request.json
#     username = data.get('username')
#     email = data.get('email')
#     password = data.get('password')

#     hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

#     new_user = User(username=username, email=email, password=hashed_password)
#     db.session.add(new_user)
#     db.session.commit()

#     user_id = new_user.id  # Получаем идентификатор только что созданного пользователя

#     # Создаем ссылку на пользователя с использованием его идентификатора
#     user_link = url_for('get_user', user_id=user_id, _external=True)

#     print("User ID:", user_id)  # Печатаем user_id после успешной регистрации

#     return jsonify({'message': 'User registered successfully', 'user_link': user_link})

# @app.route('/api/login', methods=['POST'])
# def login():
#     data = request.json
#     username = data.get('username')
#     password = data.get('password')

#     user = User.query.filter_by(username=username).first()

#     if user and bcrypt.check_password_hash(user.password, password):
#         return jsonify({'message': 'Login successful'})
#     else:
#         return jsonify({'message': 'Invalid username or password'})

# @app.route('/api/send_message', methods=['POST'])
# def send_message():
#     data = request.json
#     # Здесь можно добавить код для обработки отправленного сообщения
#     # Например, можно сохранить сообщение в базу данных
#     return jsonify({'status': 'success'})

# @app.route('/api/user/<int:user_id>')
# def get_user(user_id):
#     # Получаем информацию о пользователе по его идентификатору
#     user = User.query.get_or_404(user_id)
#     return jsonify({
#         'id': user.id,
#         'username': user.username,
#         'email': user.email
#     })

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()  # Создание таблицы пользователей при запуске приложения
#     app.run(debug=True)
from flask import Flask, request, jsonify, redirect, url_for
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow CORS for all routes

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)



@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Return a JSON response with user_link upon successful registration
        return jsonify({'message': 'User registered successfully', 'user_link': url_for('chat')})
    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error during registration: {str(e)}")
        return jsonify({'message': 'Error during registration'})



@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        return redirect(url_for('chat'))  # Перенаправляем на страницу чата после успешного входа
    else:
        return jsonify({'message': 'Invalid username or password'})

@app.route('/chat')
def chat():
    return render_template('chats.html')



@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.json
    # Здесь можно добавить код для обработки отправленного сообщения
    # Например, можно сохранить сообщение в базу данных
    return jsonify({'status': 'success'})

@app.route('/api/user/<int:user_id>')
def get_user(user_id):
    # Получаем информацию о пользователе по его идентификатору
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    })



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создание таблицы пользователей при запуске приложения
    app.run(debug=True)
