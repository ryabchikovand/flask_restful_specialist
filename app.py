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
path = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(path, 'test_rel.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class AuthorModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return d


class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
    quote = db.Column(db.String(255), unique=False)

    def __init__(self, author, quote):
        self.author_id = author.id
        self.quote = quote

    def to_dict(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return d


class Author(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, id=None):
        if id is None:
            authors = AuthorModel.query.all()
        else:
            author = AuthorModel.query.get(id)
            ic(author)
            if author is None:
                return {}, 404
            authors = [author]
        ic(authors)
        return [author.to_dict() for author in authors], 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name")
        author_data = parser.parse_args()
        author = AuthorModel(author_data["name"])
        db.session.add(author)
        db.session.commit()
        return author.to_dict(), 201

    def put(self, id):
        if id is None:
            return {}, 404
        parser = reqparse.RequestParser()
        parser.add_argument("name")
        author_data = parser.parse_args()
        author = AuthorModel.query.get(id)
        if author is None:
            return {}, 404
        author.name = author_data['name']
        db.session.add(author)
        db.session.commit()
        return author.to_dict(), 201

    def delete(self, id):
        if id is None:
            return {}, 404
        author = AuthorModel.query.get(id)
        if author is None:
            return {}, 404
        db.session.delete(author)
        db.session.commit()
        return [author.to_dict()], 200


class Quote(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, author_id, id=None):
        """
        ToDo Сделать обработку запроса put для /authors/<int:author_id>/quotes/<int:id>
        :param author_id:
        :param id:
        :return:
        """
        if id is None:
            quotes = QuoteModel.query.all()
        else:
            quote = QuoteModel.query.get(id)
            if quote is None:
                return {}, 404
            quotes = [quote]
        return [quote.to_dict() for quote in quotes], 200

    def put(self, author_id, id):
        """
        ToDo Обработать адрес вида /authors/quotes (без id)
        :param author_id:
        :param id:
        :return:
        """
        if author_id is None:
            return {}, 404
        if id is None:
            return {}, 404
        parser = reqparse.RequestParser()
        parser.add_argument("quote")
        quote_data = parser.parse_args()
        author = AuthorModel.query.get(author_id)
        quote = QuoteModel.query.get(id)
        if author is None:
            return {}, 404
        if quote is None:
            return {}, 404
        quote.quote = quote_data['quote']
        db.session.add(quote)
        db.session.commit()
        return quote.to_dict(), 201

    def post(self, author_id):
        parser = reqparse.RequestParser()
        parser.add_argument("quote")
        quote_data = parser.parse_args()
        author = AuthorModel.query.get(author_id)
        quote = QuoteModel(author, quote_data["quote"])
        db.session.add(quote)
        db.session.commit()
        return quote.to_dict(), 201

    def delete(self, author_id, id):
        if author_id is None:
            return {}, 404
        if id is None:
            return {}, 404
        author = AuthorModel.query.get(author_id)
        quote = QuoteModel.query.get(id)
        if author is None:
            return {}, 404
        if quote is None:
            return {}, 404
        db.session.delete(quote)
        db.session.commit()
        return [quote.to_dict()], 200


# Route(Маршрут)

api.add_resource(Author, "/authors", "/authors/<int:id>")
api.add_resource(Quote, "/quotes", "/quotes/<int:id>", "/authors/<int:author_id>/quotes",  "/authors/<int:author_id>/quotes/<int:id>")

if __name__ == '__main__':
    app.run(debug=True)
