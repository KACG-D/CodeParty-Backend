from peewee import SqliteDatabase, Model, AutoField, CharField, TextField,BooleanField,IntegerField ,DateTimeField
import datetime

db = SqliteDatabase('db.sqlite3')

class User(Model):
    id = AutoField(primary_key=True)
    name = CharField(100,unique = True)
    password = CharField(100)
    refresh_token = TextField(null=True)
    is_admin = BooleanField()
    icon = TextField(null=True)
    email = CharField(100,unique = True)
    class Meta:
        database = db

class Contest(Model):
    id = AutoField(primary_key=True)
    name = CharField(100)
    description = TextField(null=True)
    thumb = TextField(null=True)
    
    class Meta:
        database = db

class Code(Model):
    id = AutoField(primary_key=True)
    user_id = IntegerField()
    contest_id = IntegerField()
    time = DateTimeField
    name = CharField(100)
    class Meta:
        database = db

class Room(Model):
    id = AutoField(primary_key=True)
    contest_id = IntegerField()
    time = DateTimeField(default=datetime.datetime.now)
    json_path = CharField(100,null = True)
    class Meta:
        database = db

class Entry(Model):
    id = AutoField(primary_key=True)
    room_id = IntegerField()
    code_id = IntegerField()
    class Meta:
        database = db

db.create_tables([User])
db.create_tables([Contest])
db.create_tables([Code])
db.create_tables([Room])
db.create_tables([Entry])

# ユーザーデータ挿入
try:
    User.create(name='tanaka', password='secret_tanaka',is_admin=False,email = "hoge@hoge.com")
    User.create(name='kobayashi', password='secret_kobayashi',is_admin=True,email = "hoge1@hoge.com")
    Contest.create(name='Square Drop #1', description='デモ用のコンテストです',)
except:
    pass