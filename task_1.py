from flask import Flask
from flask_restful import Api, Resource, reqparse, request, output_json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from icecream import ic


class UnicodeApi(Api):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app.config['RESTFUL_JSON'] = {
            'ensure_ascii': False,
        }


app = Flask(__name__)
api = UnicodeApi(app)

result = dict()


class Solve(Resource):
    def get(self):
        """
        Описание функции
        :return:
        """
        return result

    def post(self):
        """
        Описание функции
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument("A")
        parser.add_argument("B")
        parser.add_argument("C")
        params = parser.parse_args()
        print("params = ", params)
        A = params['A']
        B = params['B']
        C = params['C']
        result = self.solve(A, B, C)
        return params, 201


    def solve(self, A, B, C):
        """
        Описание функции
        :param A:
        :param B:
        :param C:
        :return:
        """
        A = int(A)
        B = int(B)
        C = int(C)
        D = B ** 2 - 4 * A * C
        if B == 0 and C == 0:
            Nroots = 1
        elif C == 0:
            Nroots = 2
        elif B == 0:
            if C > 0:
                Nroots = 0
            else:
                Nroots = 2
        elif D > 0:
            Nroots = 2
        elif D == 0:
            Nroots = 1
        else:
            Nroots = 0
        result['A'] = A
        result['B'] = B
        result['C'] = C
        result['Nroots'] = Nroots
        print(result)
        return result


api.add_resource(Solve, "/grab", "/solve")


if __name__ == '__main__':
    app.run(debug=True)