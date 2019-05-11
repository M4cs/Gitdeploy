from flask import Flask, request, render_template, jsonify
from flask_restful import Api, Resource, reqparse
from git.cmd import Git
import subprocess
import requests, validators

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({ 'status': 404,
                     'message': 'No endpoint here.'})
    
@app.route('/deploy')
def get():
    parser = reqparse.RequestParser()
    parser.add_argument('repo', location='args', required=True)
    parser.add_argument('port', location='args', required=True)
    data = parser.parse_args()
    repo = data['repo']
    port = data['port']
    try:
        response = requests.get(repo)
        if response.status_code != 200:
            return jsonify({ 'status': 401, 'error': '{} is not a valid URL'.format(repo) })
    except:
        return jsonify({ 'status': 401, 'error': '{} is not a valid URL'.format(repo) })
    gitcmd = Git('.')
    gitcmd.init()
    name = repo.split('/')
    repo_name = name[-1]
    repo_name = repo_name.replace('.git', '')
    gitcmd.clone(repo, 'repos/' + repo_name)
    subprocess.Popen('.flaskapp/bin/uwsgi --http :%s --file repos/{}/wsgi.py --callable app'.format(port, repo_name))
    return jsonify({ 'status': 200, 'message': 'Deployed to Raspberry Pi! {} is now running!'.format(repo_name) })
        
    
if __name__ == "__main__":
    app.run('0.0.0.0', port=5000)