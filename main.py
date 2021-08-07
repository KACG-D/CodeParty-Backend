
from fastapi import Depends, FastAPI ,  File, UploadFile,Form,Query
from typing import List,Optional
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from auth import get_current_user, get_current_user_with_refresh_token, create_tokens, authenticate
from starlette.middleware.cors import CORSMiddleware
from codeparty_simulator.exec import execute
import models
import uvicorn
import datetime
import shutil
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   #
    allow_methods=["*"],      # 
    allow_headers=["*"]       # 
)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

    class Config:
        orm_mode = True

class User(BaseModel):
    name: str
    class Config:
        orm_mode = True

class Submit(BaseModel):
    code_ids:List[int]
    contest_id:int
    class Config:
        orm_mode = True

class Contest(BaseModel):
    id: int
    class Config:
        orm_mode = True

class UserIn(BaseModel):
    name: str
    password: str


class UserUp(BaseModel):
    name: str
    password: str
    email:str

def return_data(ret):
    return ret

@app.post("/token")
async def login(user_in: UserIn):
    user = authenticate(user_in.name, user_in.password)
    ret_dict = {}
    ret_dict["name"] = user.name
    ret_dict["tokens"] = create_tokens(user.id)
    return ret_dict


@app.get("/refresh_token/", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user_with_refresh_token)):
    return create_tokens(current_user.id)


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


#Contest 

@app.get("/contests/{contest_id}")
def read_contests(contest_id: int):
    return models.Contest.get_by_id(contest_id).__data__ 

@app.get("/contests/")
async def read_contests():
    ret = models.Contest.select()
    return [r.__data__ for r in ret]


@app.post("/contests/")
async def create_contests(name:str,description:str,file:UploadFile =File(...)):
    thumb = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    contest = models.Contest.create(name=name,description=description,thumb = "http://35.75.64.1:8000/static/thumb/")
    with open("./static/thumb/"+str(contest.id)+".png", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    contest.thumb = "http://35.75.64.1:8000/static/thumb/"+str(contest.id)+".png"
    contest.save()
    return contest.__data__ 

@app.get("/contests/{contest_id}/codes")
def read_contest_codes(contest_id: int):
    ret = models.Code.select().where(models.Code.contest_id==contest_id)
    return [r.__data__ for r in ret]

@app.get("/contests/{contest_id}/rooms")
def read_contest_rooms(contest_id: int):
    rooms =  models.Room.select().where(models.Room.contest_id==contest_id)
    return [room_json(room.id) for room in rooms]

@app.get("/contests/{contest_id}/submitted")
def read_contest_submitted(contest_id: int,current_user:User = Depends(get_current_user)):
    ret =  models.Code.select().where(models.Code.contest_id==contest_id and models.Code.user_id==current_user.id)
    return [r.__data__ for r in ret]

#User 
@app.get("/users/{user_id}")
def read_user(user_id: int):
    return models.User.get_by_id(user_id).__data__ 

@app.post("/users/update")
async def update_user(name:str= Form(None),password:str= Form(None),email:str= Form(None),current_user:User = Depends(get_current_user) ,icon: UploadFile = File(None)):
    file = icon
    user = models.User.get_by_id(current_user.id)
    if(name is not None):
        user.name = name
    if(password is not None):
        user.password = password
    if(email is not None):
        user.email = email

    if(file != None):
        path =  "http://35.75.64.1:8000/static/usericon/s"+str(current_user.id)+".png"
        user.icon = path
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    user.save()
    ret_dict = {}
    ret_dict["name"] = user.name
    ret_dict["tokens"] = create_tokens(user.id)

    return ret_dict

@app.post("/users/")
async def create_user(user_up: UserUp):
    user = models.User.create(name=user_up.name,password= user_up.password,is_admin = False,email = user_up.email)
    auth = authenticate(user.name, user.password)
    ret_dict = {}
    ret_dict["name"] = user.name
    ret_dict["tokens"] = crseate_tokens(user.id)
    return ret_dict
    

@app.post("/users/icon")
async def create_user_icon(file: UploadFile = File(...),current_user:User = Depends(get_current_user)):
    user = models.User.get_by_id(current_user.id)
    path =  "http://35.75.64.1:8000/static/usericon/s"+str(current_user.id)+".png"
    user.icon = path
    user.save()
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return user

@app.get("/users/")
def read_users():
    ret = models.User.select()
    return [r.__data__ for r in ret]


# Code 
@app.post("/codes/")
async def create_codes(contest_id:int= Form(...),name:str= Form(...), file: UploadFile = File(...),current_user:User = Depends(get_current_user)):
    print(current_user,contest_id,file)
    code = models.Code.create(user_id=current_user.id,contest_id= contest_id,time = datetime.datetime.now(),name=name)

    with open("./static/submit/a"+str(code.id)+".py", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        #buffer.write(file)
    return code.__data__ 

@app.get("/codes/{code_id}")
async def read_code(code_id: int):
    return models.Code.get_by_id(code_id).__data__ 


@app.get("/codes/{code_id}/user")
async def read_code_user(code_id: int):
    code = models.Code.get_by_id(code_id)
    user = models.User.get_by_id(code.user_id)
    return user.__data__
@app.get("/codes/")
async def read_codes():
    ret = models.Code.select()
    return [r.__data__ for r in ret]

##Room 
@app.post("/rooms/", status_code=201)
async def create_room(contest_id:int):
    room = models.Room.create(contest_id =contest_id)
    return room.__data__ 


def room_json(room_id:int):
    room = models.Room.get_by_id(room_id)
    entries = models.Entry.select().where(models.Entry.room_id ==room_id)
    codes = [models.Code.get_by_id(entry.code_id) for entry in entries]
    return {"id": room.id,"time": room.time,"contest_id":room.contest_id,"json_path":room.json_path,"codes": [c.__data__ for c in codes]}


@app.get("/rooms/{room_id}")
async def read_room(room_id: int):
    return room_json(room_id)

@app.get("/rooms/")
async def read_rooms():
    rooms = models.Room.select()
    ret = []
    for room in rooms:
        ret += [room_json(room.id)]
    return ret


@app.get("/rooms/{room_id}/run")
async def run_room_id(room_id: int):
    return {"json_path":run_room(room_id)}

#https://qiita.com/tdrk/items/9b23ad6a58ac4032bb3b

def run_room(room_id:int):
    entries = models.Entry.select().where(models.Entry.room_id ==room_id)
    json = execute(["static.submit.a"+str(entry.code_id) for entry in entries],room_id)
    return "http://35.75.64.1:8000"+json

@app.post("/rooms/submit")
async def room_submit(submit :Submit):
    contest_id = submit.contest_id
    code_ids = submit.code_ids
    room = models.Room.create(contest_id =contest_id)
    for cid in code_ids:
        models.Entry.create(room_id = room.id,code_id=cid)
    try:
        room.json_path = run_room(room_id = room.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
    room.save()
    return room.__data__

##Entry 
@app.post("/entries/", status_code=201)
async def create_entry(room_id:int,code_id:int):
    room = models.Entry.create(room_id = room_id,code_id=code_id)
    return room.__data__ 

@app.get("/entries/{entry_id}")
async def read_entry(entry_id: int):
    return models.Entry.get_by_id(entry_id).__data__ 

@app.get("/entries/")
async def read_entry():
    ret = models.Entry.select()
    return [r.__data__ for r in ret]

# Debug 
@app.post("/debug/codes/")
async def create_codes(contest_id:int= Form(...),name:str= Form(...),user_id:int= Form(...), file: UploadFile = File(...)):
    code = models.Code.create(user_id=user_id,contest_id= contest_id,time = datetime.datetime.now(),name=name)
    
    with open("./static/submit/a"+str(code.id)+".py", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return code.__data__ 

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)