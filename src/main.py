"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Todo
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


######## End points para el todo ################

@app.route('/todos', methods=['GET'])
def get_todos():
    # get all the todos
    todos = Todo.query.all()

    # map the results and your list of todos  inside of the all_todos variable
    results = list(map(lambda x: x.serialize(), todos))

    return jsonify(results), 200


@app.route('/add_todo', methods=['POST'])
def add_todo():

    # recibir info del request
    request_body = request.get_json()
    print(request_body)

    new_todo = Todo(done=request_body["done"], label=request_body["label"])
    db.session.add(new_todo)
    db.session.commit()

    return jsonify("All good, added"), 200

@app.route('/todos/<int:id>', methods=['DELETE'])
def del_todo(id):

    # recibir info del request
    todo = Todo.query.get(id)
    if todo is None:
        raise APIException('Todo not found', status_code=404)

    db.session.delete(todo)

    db.session.commit()

    return jsonify("All good, delete"), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
