from flask import Flask
from flask_script import Manager, Server
from flask_cors import CORS
from router import api

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fegesefdasfvef'

#跨域访问
CORS(app, supports_credentials=True, resource={r"*":{"origin":"*"}})

#flask restful init
api.init_app(app)

manager = Manager(app)

manager.add_command('runserver', Server(host='0.0.0.0', port=8000))



if __name__ == '__main__':
    manager.run()
