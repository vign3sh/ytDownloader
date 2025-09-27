from fastapi import APIRouter
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from pytubefix import YouTube, Playlist
from pytubefix import Buffer
from starlette.background import BackgroundTasks
from pytubefix.cli import on_progress

buffer = Buffer()
buffer.clear()

router = APIRouter(prefix="/music")

@router.get("/single/{yt_link}")
async def getMusicSingle(bg_tasks: BackgroundTasks, yt_link: str ="fvUmrVnqLV0", save: bool = False):
    url = f"https://www.youtube.com/watch?v={yt_link}"
    yt = YouTube(url, on_progress_callback=on_progress)
    print(yt.title)
    ys = yt.streams.get_audio_only()
    buffer.download_in_buffer(ys)
    cache = buffer.read()
    buffer.clear()
    file_name = f"{yt.title}.m4a"
    headers = {'Content-Disposition': f'inline; filename="{file_name}"'}
    return Response(content=cache, headers=headers, media_type="music/mp4")
    
@router.get("/playlist/{yt_link}")
async def getMusicPlaylist(yt_link: str="PLDCzG-mQi15JutPnxDALeYn3p6dlvzmIh", start: int = 1, end: int = 5):
    url = f"https://music.youtube.com/playlist?list={yt_link}"
    pl = Playlist(url)
    urls = pl.video_urls
    songs = []
    for i, video in enumerate(pl.videos):
        url = urls[i]
        url = f"http://127.0.0.1:8000/music/single/{url[url.find('v=') + 2:]}"
        song = {"title":video.title, "url": url}
        songs.append(song)
    """import pdb; pdb.set_trace();"""
    return {"SUCCESS":True, "songs":songs}