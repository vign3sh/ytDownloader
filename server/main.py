import os
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from pytubefix import YouTube, Playlist
from pytubefix import Buffer
from pytubefix.cli import on_progress
import uvicorn
from starlette.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

buffer = Buffer()
buffer.clear()
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World1"}


@app.get("/music/single/{yt_link}")
async def getMusicSingle(bg_tasks: BackgroundTasks, yt_link: str ="fvUmrVnqLV0", save: bool = False):
    current_dir = os.getcwd()
    LOCAL_PATH = os.path.join(current_dir, "downloads")
    #LOCAL_PATH = "./downloads"
    
    url = f"https://www.youtube.com/watch?v={yt_link}"
    
    yt = YouTube(url, on_progress_callback=on_progress)
    print(yt.title)
    ys = yt.streams.get_audio_only()
    if(save):
        ys.download(output_path=LOCAL_PATH)
        file_name = f"{yt.title}.m4a"
        file_path = os.path.join(LOCAL_PATH, file_name)
        bg_tasks.add_task(os.remove, file_path)
        return FileResponse(file_path, background=bg_tasks)
    else:
        buffer.download_in_buffer(ys)
        cache = buffer.read()
        buffer.clear()
        file_name = f"{yt.title}.m4a"
        headers = {'Content-Disposition': f'inline; filename="{file_name}"'}
        return Response(content=cache, headers=headers, media_type="music/mp4")
    
    #import pdb; pdb.set_trace();
    

@app.get("/music/playlist/{yt_link}")
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

if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)
