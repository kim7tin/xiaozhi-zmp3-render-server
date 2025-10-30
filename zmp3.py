# cre by TomDev211

import time, hashlib, hmac, requests, json
from urllib.parse import quote
URL = "https://zingmp3.vn"
cfg = json.load(open("config.json", encoding="utf-8"))
version, akey, skey = cfg["version"], cfg["r"], cfg["i"]
p = {"ctime", "id", "type", "page", "count", "version"}

session, _cookie = requests.Session(), None

# utils
def hash256(s): return hashlib.sha256(s.encode()).hexdigest()
def hmac512(s, key): return hmac.new(key.encode(), s.encode(), hashlib.sha512).hexdigest()

def str_params(params):
    return "".join(f"{quote(k)}={quote(str(v))}" for k, v in sorted(params.items()) if k in p and v not in [None, ""] and len(str(v)) <= 5000)

def get_sig(path, params): 
    return hmac512(path + hash256(str_params(params)), skey)

def get_cookie(force=False):
    global _cookie
    if _cookie and not force: return _cookie
    r = session.get(URL, timeout=5)
    _cookie = "; ".join(f"{k}={v}" for k, v in r.cookies.items()) or None
    return _cookie

def zingmp3(path, extra=None):
    now = str(int(time.time()))
    params = {"ctime": now, "version": version, "apiKey": akey, **(extra or {})}
    params["sig"] = get_sig(path, params)
    headers = {"Cookie": get_cookie()} if get_cookie() else {}
    return session.get(f"{URL}{path}", headers=headers, params=params, timeout=10).json()

# api
chart_home = lambda: zingmp3("/api/v2/page/get/chart-home")
search_song = lambda q, count=10: zingmp3("/api/v2/search", {"q": q, "type": "song", "count": count, "allowCorrect": 1})
get_song = lambda song_id: zingmp3("/api/v2/song/get/info", {"id": song_id})
get_stream = lambda song_id: zingmp3("/api/v2/song/get/streaming", {"id": song_id})
get_lyric = lambda song_id: zingmp3("/api/v2/lyric/get/lyric", {"id": song_id})
