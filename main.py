
from flask import Flask, request, jsonify
from game_recommender import generate_recommendation

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def home():
    if(request.method == 'GET'):
        data = "hello world"
        return jsonify({'data': data})
  
@app.route('/user/<int:id>', methods = ['GET'])
def query_games(id):
    res = generate_recommendation(20, id)
    return res

