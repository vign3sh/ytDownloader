from fastapi import APIRouter, Response , Depends
from pytubefix import YouTube, Playlist
from pytubefix import Buffer
from starlette.background import BackgroundTasks
from pytubefix.cli import on_progress
import redis
import json

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

buffer = Buffer()
buffer.clear()

router = APIRouter(prefix="/music")

@router.get("/single/{yt_link}")
async def getMusicSingle(bg_tasks: BackgroundTasks, yt_link: str ="fvUmrVnqLV0", save: bool = False):
    res = redis_client.lrange(f"music?id={yt_link}", 0, -1)
    #res = redis_client.get(f"music?id={yt_link}")
    if (len(res) > 0):
        cache = res[0]
        title = res[1]
        print("cached song")
    else:
        url = f"https://www.youtube.com/watch?v={yt_link}"
        yt = YouTube(url, on_progress_callback=on_progress)
        title = yt.title
        print(title)
        ys = yt.streams.get_audio_only()
        buffer.download_in_buffer(ys)
        cache = buffer.read()
        buffer.clear()
        #encoded_song = json.dumps(cache)
        redis_client.rpush(f"music?id={yt_link}", cache, title)
        #redis_client.set(f"music?id={yt_link}", cache)
    file_name = f"{title}.m4a"
    headers = {'Content-Disposition': f'inline; filename="{file_name}"'}
    return Response(content=cache, headers=headers, media_type="music/mp4")
    
@router.get("/playlist/{yt_link}")
async def getMusicPlaylist(yt_link: str="PLDCzG-mQi15JutPnxDALeYn3p6dlvzmIh", start: int = 1, end: int = 5):
    res = redis_client.get(f"pl?id={yt_link}")
    if (res != None):
        songs = json.loads(res)
        print("cached playlist")
    else:
        url = f"https://music.youtube.com/playlist?list={yt_link}"
        pl = Playlist(url)
        urls = pl.video_urls
        songs = []
        for i, video in enumerate(pl.videos):
            url = urls[i]
            url = f"http://127.0.0.1:8000/music/single/{url[url.find('v=') + 2:]}"
            song = {"title":video.title, "url": url}
            songs.append(song)
        encoded_song = json.dumps(songs)
        redis_client.set(f"pl?id={yt_link}", encoded_song)
    
    return {"SUCCESS":True, "songs":songs}