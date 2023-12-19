from flask import Flask, render_template, request, jsonify
import subprocess
import webbrowser
from youtubesearchpython import Search

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_youtube', methods=['POST'])
def search_youtube():
    search_query = request.form['search_query']
    allSearch = Search(search_query, limit=10)
    results = allSearch.result()['result']
    video_list = [f"{i}. {result['title']}" for i, result in enumerate(results, start=1)]
    return jsonify(video_list)

@app.route('/download_audio', methods=['POST'])
def download_audio():
    video_url = request.form['video_url']
    download_command = f"youtube-dl --extract-audio --audio-format mp3 {video_url}"
    subprocess.Popen(download_command, shell=True)
    return jsonify({'status': 'success'})

@app.route('/play_video', methods=['POST'])
def play_video():
    video_url = request.form['video_url']
    webbrowser.open(video_url)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
