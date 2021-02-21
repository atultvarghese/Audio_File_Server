from typing import Optional
from enum import Enum
from fastapi import FastAPI, Request, File, UploadFile, status,Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
from mutagen.mp3 import MP3
import time



if not os.path.exists("media"):
    os.mkdir("media")
if not os.path.exists("media/song"):
    os.mkdir("media/song")
if not os.path.exists("media/podcast"):
    os.mkdir("media/podcast")
if not os.path.exists("media/audiobook"):
    os.mkdir("media/audiobook")



#Data base connection
import pymongo
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["audio-server"]

coll_song = db.song
coll_podcast = db.podcast
coll_audiobook = db.audiobook

song_len = coll_song.find_one({},sort=[( '_id', pymongo.DESCENDING )])["_id"] if coll_song.find_one({},sort=[( '_id', pymongo.DESCENDING )]) else 0
podcast_len = coll_podcast.find_one({},sort=[( '_id', pymongo.DESCENDING )])["_id"] if coll_podcast.find_one({},sort=[( '_id', pymongo.DESCENDING )]) else 0
audiobook_len = coll_audiobook.find_one({},sort=[( '_id', pymongo.DESCENDING )])["_id"] if coll_audiobook.find_one({},sort=[( '_id', pymongo.DESCENDING )]) else 0
print(song_len,podcast_len,audiobook_len)

def song_upload(data):
    print(data)
    coll_song.insert_one(data)
def podcast_upload(data):
    print(data)
    coll_podcast.insert_one(data)
def audiobook_upload(data):
    print(data)
    coll_audiobook.insert_one(data)

def song_update(data):
    coll_song.update_one({"_id":data['_id']},{"$set":data},upsert=True)
def podcast_update(data):
    coll_podcast.update_one({"_id":data['_id']},{"$set":data},upsert=True)
def audiobook_update(data):
    coll_audiobook.update_one({"_id":data['_id']},{"$set":data},upsert=True)

def song_delete(id):
    coll_song.delete_one({"_id":id})
def podcast_delete(id):
    coll_podcast.delete_one({"_id":id})
def audiobook_delete(id):
    coll_audiobook.delete_one({"_id":id})

app = FastAPI()

app.mount("/media", StaticFiles(directory="media"), name="media")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    songs = list(coll_song.find())
    podcasts = list(coll_podcast.find())
    audiobooks = list(coll_audiobook.find())
    return templates.TemplateResponse("index.html", {"request": request,"songs":songs,"podcasts":podcasts,"audiobooks":audiobooks})

@app.get("/{audio_type}", response_class=HTMLResponse)
async def read_item(audio_type:str,request: Request,id: Optional[int] = None):
    if audio_type =="song":
        if id:
            songs = list(coll_song.find({"_id":id}))
            return templates.TemplateResponse("index.html", {"request": request,"songs":songs})
        else:
            songs = list(coll_song.find())
            return templates.TemplateResponse("index.html", {"request": request,"songs":songs})
    if audio_type =="podcast":
        if id:
            podcasts = list(coll_podcast.find({"_id":id}))
            return templates.TemplateResponse("index.html", {"request": request,"podcasts":podcasts})
        else:
            podcasts = list(coll_podcast.find())
            return templates.TemplateResponse("index.html", {"request": request,"podcasts":podcasts})
    if audio_type =="audiobook":
        if id:
            audiobooks = list(coll_audiobook.find({"_id":id}))
            return templates.TemplateResponse("index.html", {"request": request,"audiobooks":audiobooks})
        else:
            audiobooks = list(coll_audiobook.find())
            return templates.TemplateResponse("index.html", {"request": request,"audiobooks":audiobooks})

@app.post("/create/{typeof}",status_code=status.HTTP_201_CREATED)
async def create(
    typeof:str,form_data = Form(...),file: UploadFile = File(...)
):
    form_data = eval(form_data)
    global song_len
    global podcast_len
    global audiobook_len
    # curl -X POST "http://localhost:8000/create/song" -H  "accept: application/json" -H  "Content-Type: multipart/form-data" -F "form_data={"name":"Name of the song",}" -F "file=@test.mp3;type=audio/mpeg"
    if typeof == "song":
        song_len += 1
        with open("media/song/"+str(song_len)+".mp3", "wb") as audio:
            shutil.copyfileobj(file.file, audio)
            url = str(song_len)+".mp3"
            audio = MP3("media/song/"+url)
            # duration = str(int(audio.info.length // 60))+"."+ str(int(audio.info.length % 60 ))
            duration = int(audio.info.length)
        date = time.ctime()
        data ={"_id":song_len,"url":url,"name":form_data["name"],"duration":duration,"date":date} 
        song_upload(data)
        return "success"
    # curl -X POST "http://localhost:8000/create/podcast" -H  "accept: application/json" -H  "Content-Type: multipart/form-data" -F "form_data={"name":"test","host":"test","participants":["test1","test2"]}" -F "file=@test.mp3;type=audio/mpeg"
    if typeof == "podcast":
        podcast_len +=1
        with open("media/podcast/"+str(podcast_len)+".mp3", "wb") as audio:
            shutil.copyfileobj(file.file, audio)
            url = str(podcast_len)+".mp3"
            audio = MP3("media/podcast/"+url)
            duration = int(audio.info.length)
        date = time.ctime()
        data ={"_id":podcast_len,"url":url,"name":form_data["name"],"host":form_data["host"],"participants":form_data["participants"],"duration":duration,"date":date} 
        podcast_upload(data)
        return "success"
    # curl -X POST "http://localhost:8000/create/audiobook" -H  "accept: application/json" -H  "Content-Type: multipart/form-data" -F "form_data={"title":"test","narrator":"test","author":"test"}" -F "file=@test.mp3;type=audio/mpeg"
    if typeof == "audiobook":
        audiobook_len +=1
        with open("media/audiobook/"+str(audiobook_len)+".mp3", "wb") as audio:
            shutil.copyfileobj(file.file, audio)
            url = str(audiobook_len)+".mp3"
            audio = MP3("media/audiobook/"+url)
            duration = int(audio.info.length)
        date = time.ctime()
        data ={"_id":audiobook_len,"url":url,"title":form_data["title"],"author":form_data["author"],"narrator":form_data["narrator"],"duration":duration,"date":date} 
        audiobook_upload(data)
        return "success"


@app.post("/update/{typeof}/{id}",status_code=status.HTTP_201_CREATED)
async def create(
    typeof:str,id:int,form_data = Form(...),file: UploadFile = File(...)
):
    form_data = eval(form_data)
    # curl -X POST "http://localhost:8000/update/song/id" -H  "accept: application/json" -H  "Content-Type: multipart/form-data" -F "form_data={"name":"Name of the song",}" -F "file=@test.mp3;type=audio/mpeg"
    if typeof == "song":
        with open("media/song/"+str(id)+".mp3", "wb") as audio:
            shutil.copyfileobj(file.file, audio)
            url = str(id)+".mp3"
            audio = MP3("media/song/"+url)
            # duration = str(int(audio.info.length // 60))+"."+ str(int(audio.info.length % 60 ))
            duration = int(audio.info.length)
        date = time.ctime()
        data ={"_id":id,"url":url,"name":form_data["name"],"duration":duration,"date":date} 
        song_update(data)
        return "success"
    # curl -X POST "http://localhost:8000/update/podcast/id" -H  "accept: application/json" -H  "Content-Type: multipart/form-data" -F "form_data={"name":"test","host":"test","participants":["test1","test2"]}" -F "file=@test.mp3;type=audio/mpeg"
    if typeof == "podcast":
        with open("media/podcast/"+str(id)+".mp3", "wb") as audio:
            shutil.copyfileobj(file.file, audio)
            url = str(id)+".mp3"
            audio = MP3("media/podcast/"+url)
            duration = int(audio.info.length)
        date = time.ctime()
        data ={"_id":id,"url":url,"name":form_data["name"],"host":form_data["host"],"participants":form_data["participants"],"duration":duration,"date":date} 
        podcast_update(data)
        return "success"
    # curl -X POST "http://localhost:8000/update/audiobook/id" -H  "accept: application/json" -H  "Content-Type: multipart/form-data" -F "form_data={"title":"test","narrator":"test","author":"test"}" -F "file=@test.mp3;type=audio/mpeg"
    if typeof == "audiobook":
        with open("media/audiobook/"+str(id)+".mp3", "wb") as audio:
            shutil.copyfileobj(file.file, audio)
            url = str(id)+".mp3"
            audio = MP3("media/audiobook/"+url)
            duration = int(audio.info.length)
        date = time.ctime()
        data ={"_id":id,"url":url,"title":form_data["title"],"author":form_data["author"],"narrator":form_data["narrator"],"duration":duration,"date":date} 
        audiobook_upload(data)
        return "success"

@app.post("/delete/{typeof}/{id}",status_code=status.HTTP_201_CREATED)
async def create(
    typeof:str,id:int
):
    # curl -X POST "http://localhost:8000/delete/song/id" -H  "accept: application/json" -H  "Content-Type: multipart/form-data" -F "form_data={"name":"Name of the song",}" -F "file=@test.mp3;type=audio/mpeg"
    if typeof == "song":
        os.remove("media/song/"+str(id)+".mp3")
        song_delete(id)
        return "success"
    # curl -X POST "http://localhost:8000/podcast/podcast/id" -H  "accept: application/json" -H  "Content-Type: multipart/form-data" -F "form_data={"name":"test","host":"test","participants":["test1","test2"]}" -F "file=@test.mp3;type=audio/mpeg"
    elif typeof == "podcast":
        os.remove("media/podcast/"+str(id)+".mp3")
        podcast_delete(id)
        return "success"
    # curl -X POST "http://localhost:8000/audiobook/audiobook/id" -H  "accept: application/json" -H  "Content-Type: multipart/form-data" -F "form_data={"title":"test","narrator":"test","author":"test"}" -F "file=@test.mp3;type=audio/mpeg"
    elif typeof == "audiobook":
        os.remove("media/audiobook/"+str(id)+".mp3")
        audiobook_delete(id)
        return "success"
    else:
        return "Can't delete"
