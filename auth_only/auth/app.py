
from flask import Flask

from auth.auth import Authorizer
from auth.routes import add_routes


def main():
    app.run(debug=True)


app = server = Flask(__name__)
authorizer = Authorizer(secret='change_me_for_token_encryption')
add_routes(app, authorizer)

if __name__ == '__main__':
    main()
