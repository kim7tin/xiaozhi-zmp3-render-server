
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, jsonify
from zmp3 import chart_home, search_song, get_song, get_stream, get_lyric
import requests

app = Flask(__name__)

@app.route("/test")
def test():
    try:
        # Gửi request đơn giản tới một API công khai
        r = requests.get("https://api.ipify.org?format=json", timeout=5)
        data = r.json()
        return jsonify({
            "message": "Request thành công!",
            "your_public_ip": data["ip"]
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/stream_pcm")
def stream_pcm():
    song = request.args.get("song")
    artist = request.args.get("artist")

    if not song or not artist:
        return jsonify({"error": "Missing 'song' or 'artist' parameter"}), 400

    try:
        # Tìm kiếm bài hát
        query = f"{song} - {artist}"
        results = search_song(query, count=3)

        if not results or "data" not in results or len(results["data"]) == 0:
            return jsonify({"error": "No song found"}), 404

        # Lấy song_id đầu tiên
        song_id = results["data"][0]["id"]

        # Lấy link stream
        stream_info = get_stream(song_id)

        return jsonify({
            "query": query,
            "song_id": song_id,
            "stream": stream_info
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

