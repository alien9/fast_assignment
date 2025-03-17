from .main import app
from .models import Road
from .config.index import get_index, index_search, index_store

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest,os
from fastapi import FastAPI, BackgroundTasks, status

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from geoalchemy2 import load_spatialite
from sqlalchemy.event import listen
from sqlalchemy import text
import shutil
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

if os.path.isfile("test.db"):
    os.remove("test.db")
if os.path.isdir("test_index"):
    shutil.rmtree("test_index")

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
os.environ['SPATIALITE_LIBRARY_PATH']= '/usr/lib/x86_64-linux-gnu/mod_spatialite.so'

def pytest_generate_tests(metafunc):
    os.environ['INDEX_PATH']="test_index"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True
)

listen(engine, "connect", load_spatialite)
conn = engine.connect()

client=TestClient(app)

Road.metadata.create_all(bind=engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_test_engine():
    return engine
  
def get_mock_session():
    return TestingSessionLocal()

def fromat_sqlite_geometry(t):
    return f"GEOMFROMTEXT('MULTILINESTRING({t})',4326)" 

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def get_test_index_path():
    return "test_index"

def setup(mocker):
    session = Session(engine)
    session.execute(text("delete from road"))
    session.commit()
    mocker.patch('src.config.db.get_engine', get_test_engine)
    mocker.patch('src.config.index.get_index_path', get_test_index_path)
    mocker.patch('src.main.get_session', get_mock_session)

def test_upload_file(mocker):
    with open("mexico_small.gpkg", "rb") as fu:
        datum=fu.read()
        fu.close()
    setup(mocker)
    r = client.post("/upload/", files={"file": ("mex.gpkg", datum, "application/octet-stream")})  
    session = Session(engine)
    roads = session.query(Road).all()
    session.commit()
    assert r.status_code == 200
    assert len(roads)==1312
    ix = open_dir("test_index")
    res=index_search(ix, "Playa")
    assert len([r for r in res])==30
    
def test_search_term(mocker):
    setup(mocker)
    ix=get_index()
    writer = ix.writer()
    writer.add_document(road_name="peganingas",road_id=1,content="peganingas")
    writer.add_document(road_name="pichorra",road_id=17,content="pichorra")
    writer.add_document(road_name="new data",road_id=771,content="new data")
    writer.add_document(road_name="new data",road_id=61, content="new data")
    writer.add_document(road_name="new data",road_id=14,content="new data")
    writer.add_document(road_name="new brew",road_id=12,content="new brew")
    writer.commit()
    r = client.get(f"/search/?t=new")
    assert r.status_code == 200
    assert len(r.json()["words"])==2

def test_draw_road(mocker):
    setup(mocker)
    with open("mexico_small.gpkg", "rb") as fu:
        datum=fu.read()
        fu.close()
    r = client.post("/upload/", files={"file": ("mex.gpkg", datum, "application/octet-stream")})
    r = client.get(f"/draw/Playa Caleta")
    assert r.status_code == 200

def test_draw_road_non_existant(mocker):
    setup(mocker)
    r = client.get(f"/draw/Inexistente")
    assert r.status_code == 404    
    
def test_search_term_param_missing(mocker):
    setup(mocker)
    r = client.get(f"/search/?term=new")
    assert r.status_code == 422
    assert r.json()["detail"][0]["msg"]=="Field required"
    
def test_search_post(mocker):
    setup(mocker)
    r = client.post(f"/search/?term=new")
    assert r.status_code == 405
