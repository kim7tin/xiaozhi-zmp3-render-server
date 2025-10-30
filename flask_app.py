from flask import Flask, request, jsonify
import requests
from zmp3 import search_song, get_stream, get_song, get_lyric

app = Flask(__name__)

@app.route("/stream_pcm")
def stream_pcm():
    song_name = request.args.get("song")
    artist_name = request.args.get("artist")

    if not song_name:
        return jsonify({"error": "Missing song parameter"}), 400

    query = song_name
    if artist_name:
        query += f" {artist_name}"

    # 1️⃣ Tìm bài hát
    search_result = search_song(query)
    if not search_result or search_result.get("err") != 0:
        return jsonify({"error": "Search failed", "query": query})

    items = search_result["data"].get("items", [])
    if not items:
        return jsonify({"error": "No result found", "query": query})

    song_info = items[0]
    encode_id = song_info["encodeId"]
    title = song_info["title"]
    artist = song_info["artistsNames"]
    duration = song_info["duration"]
    cover_url = song_info.get("thumbnailM")

    # 2️⃣ Lấy link stream
    stream_result = get_stream(encode_id)
    if not stream_result or stream_result.get("err") != 0:
        return jsonify({"error": "Get stream failed", "song_id": encode_id})

    stream_data = stream_result["data"]
    audio_url = stream_data.get("128")

    if not audio_url or audio_url == "VIP":
        return jsonify({"error": "Audio requires VIP"}), 403

    # 3️⃣ Theo dõi redirect để lấy link cuối cùng
    try:
        final_resp = requests.get(audio_url, allow_redirects=True, timeout=10)
        final_url = final_resp.url.replace("https://", "http://")

    except Exception as e:
        final_url = audio_url  # fallback nếu bị chặn proxy

    # 4️⃣ Lấy lyric (tùy chọn)
    lyric_info = get_lyric(encode_id)
    if lyric_info and lyric_info.get("err") == 0:
        lyric_url = f"/music_cache/{encode_id}.lrc"
    else:
        lyric_url = None

    # 5️⃣ Kết quả dạng chuẩn
    return jsonify({
        "artist": artist,
        "audio_url": final_url,
        "cover_url": cover_url,
        "duration": duration,
        "from_cache": False,
        "lyric_url": lyric_url,
        "title": title
    })


@app.route("/test")
def test():
    return jsonify({"message": "Flask is running!"})


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
