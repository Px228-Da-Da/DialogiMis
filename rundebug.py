from api.index import app, socketio, db

with app.app_context():
    db.create_all()

socketio.run(app, debug=True, port=5000)
