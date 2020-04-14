from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('email', required=True)
parser.add_argument('surname', required=True)
parser.add_argument('name', required=True)
parser.add_argument('age', required=True)
parser.add_argument('gender', required=True)
parser.add_argument('password', required=True)
parser.add_argument('vk_url', required=True)