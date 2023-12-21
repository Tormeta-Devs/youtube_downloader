import os
import subprocess
import tempfile
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_youtube():
    search_query = request.form['search_query']
    # Tu lógica de búsqueda aquí...
    return render_template('index.html', results=results)

@app.route('/download/<video_id>', methods=['GET'])
def download_audio(video_id):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)

    download_command = f"youtube-dl --ffmpeg-location C://FFmpeg//bin -o {temp_file.name} --extract-audio --audio-format mp3 {video_url}"
    subprocess.run(download_command, shell=True)

    return send_file(temp_file.name, as_attachment=True, download_name='audio.mp3')

if __name__ == '__main__':
    app.run(debug=True)
