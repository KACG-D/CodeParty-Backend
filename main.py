
from fastapi import Depends, FastAPI ,  File, UploadFile,Form
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
    thumb = dt_now.strftime('%Y%m%d%H%M%S')
    contest = models.Contest.create(name=name,discription=discription,thumb = "http://35.75.64.1:8000/static/thumb/")

    with open("./static/thumb/"+str(contest.id)+".py", "wb") as buffer:
        shutil.copyfileobj(file, buffer)

    return contest.__data__ 

@app.get("/contests/{contest_id}/codes")
def read_contest_codes(contest_id: int):
    ret = models.Code.select().where(models.Code.contest_id==contest_id)
    return [r.__data__ for r in ret]

@app.get("/contests/{contest_id}/rooms")
def read_contest_rooms(contest_id: int):
    ret =  models.Room.select().where(models.Room.contest_id==contest_id)
    return [r.__data__ for r in ret]

@app.get("/contests/{contest_id}/submitted")
def read_contest_submitted(contest_id: int,current_user:User = Depends(get_current_user)):
    ret =  models.Code.select().where(models.Code.contest_id==contest_id and models.Code.user_id==current_user.id)
    return [r.__data__ for r in ret]

#User 
@app.get("/users/{user_id}")
def read_user(user_id: int):
    return models.User.get_by_id(user_id).__data__ 

@app.post("/users/")
async def create_user(user_up: UserIn):
    user = models.User.create(name=user_up.name,password= user_up.password,is_admin = False,email = user_up.email)
    auth = authenticate(user.name, user.password)
    ret_dict = {}
    ret_dict["name"] = user.name
    ret_dict["tokens"] = create_tokens(user.id)
    return ret_dict

@app.get("/users/")
def read_users():
    ret = models.User.select()
    return [r.__data__ for r in ret]


# Code 
@app.post("/codes/")
async def create_codes(contest_id:int= Form(...),name:str= Form(...), file: bytes = File(...),current_user:User = Depends(get_current_user)):
    print(current_user,contest_id,file)
    code = models.Code.create(user_id=current_user.id,contest_id= contest_id,time = datetime.datetime.now(),name=name)

    with open("./static/submit/"+str(code.id)+".py", "wb") as buffer:
        shutil.copyfileobj(file, buffer)

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
async def create_room(contest_id:int,current_user:User = Depends(get_current_user)):
    room = models.Room.create(contest_id =contest_id)


    return room.__data__ 

@app.get("/rooms/{room_id}")
async def read_room(room_id: int):
    return models.Room.get_by_id(room_id).__data__ 

@app.get("/rooms/")
async def read_rooms():
    ret = models.Room.select()
    return [r.__data__ for r in ret]


@app.get("/rooms/{room_id}/run")
async def run_room(room_id: int):
    json = execute(["codeparty_simulator.players.sample2"]*4,room_id)
    return json

##Entry 
@app.post("/entries/", status_code=201)
async def create_entry(room_id:int,code_id:int):
    room = models.Entry.create(room_id = room_id)
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

    with open("./static/submit/"+str(code.id)+".py", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return code.__data__ 

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)