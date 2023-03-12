
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from game_recommender import generate_recommendation
from forms import NameForm
#from flask_cors import CORS
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.secret_key = "supersecretkey"
bootstrap = Bootstrap(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

'''
@app.route('/', methods = ['GET', 'POST'])
def home():
    
    form = NameForm(request.form)
    if request.method == 'POST':
        return query_games(form)
    
    return render_template('index.html', form=form)

@app.route('/results')
def query_games(form):
    userId = form.data['name']
    results = generate_recommendation(20, userId)
    print(results)
    if results.empty:
        flash('No results found!')
        return redirect(url_for('index'))
    else:
        return render_template('results.html', form=form, results=results)

'''
@app.route('/', methods = ['GET', 'POST'])
@cross_origin()
def home():
    if(request.method == 'GET'):
        data = "hello world"
        return jsonify({'data': data})

@app.route('/user/<int:id>', methods = ['GET'])
@cross_origin()
def query_games(id):
    res = generate_recommendation(20, id).to_json(orient="split")
    return res


