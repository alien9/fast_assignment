from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from .models import Road
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, File, UploadFile
import logging,fiona
import sqlite3, re
from sqlalchemy.orm import Session
from shapely import MultiLineString
from geoalchemy2.shape import from_shape
from sqlmodel import Field, Session, SQLModel, create_engine, select
from src.config.db import get_engine
from .config.index import *
from whoosh.qparser import QueryParser
from fastapi import FastAPI, BackgroundTasks, status
from sqlalchemy import select
from geoalchemy2.shape import to_shape
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()
LOG = logging.getLogger(__name__)
app = FastAPI()
engine=get_engine()
conn=engine.connect()
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_session():
    return Session(engine)

LOG.info("API is starting up")

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    Road.metadata.create_all(bind=engine)

def geometry_format(points):
    return f"SRID=4326;MULTILINESTRING({points})"

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/upload/")
async def create_upload_file(file: UploadFile):
    ix=get_index()
    session = get_session()
    out_file_path=f"gpkg/{uuid4()}.gpkg"
    with open(out_file_path, 'wb') as out_file:
        content = await file.read()  # async read
        out_file.write(content)  # async write
    n=0
    writer = ix.writer()
    with fiona.open(out_file_path) as layer:
        for feature in layer:
            n+=1
            r=Road(name=feature["properties"]["nomvial"])
            ewkt="("+"),(".join(list(map(lambda ring:", ".join(list(map(lambda p:f"{p[0]} {p[1]}", ring))), feature.geometry.coordinates)))+")"
            r.geom=geometry_format(ewkt)
            k=session.add(r)
            terms=re.split("\W+", r.name)
            for t in terms:
                writer.add_document(road_name=r.name, road_id=r.id, content=t)
    writer.commit()
    session.commit()
    result = {"status":"ok", "message": f"{n} roads inserted"}
    return {"filename": file.filename, "result":result}

@app.get("/search/")
async def search_term(t: str):
    ix=get_index()
    result=[]
    if len(t)>2:
        query = QueryParser("content", ix.schema).parse(f"{t}*")
        result=ix.searcher().search(query, limit=30)
    return {"status":"ok", "words":list(set([r["road_name"] for r in result]))}

@app.get("/draw/{road_name}")
async def draw_road(road_name: str):
    session = get_session()
    r=session.execute(select(Road).where(Road.name == road_name))
    roads=[to_shape(road[0].geom).wkt for road in r]
    if not len(roads):
        raise HTTPException(status_code=404, detail="Item not found")
    return {"result":"ok", "roads":roads}
    
@app.on_event("startup")
def on_startup():
    create_db_and_tables()