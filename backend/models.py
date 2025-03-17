from typing import Annotated
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base
class Base(DeclarativeBase):
    pass

class Road(Base):
    __tablename__ = "road"
    id = Column(Integer, primary_key=True)
    name=Column(String(100), index=True)
    geom = Column(Geometry(geometry_type="MULTILINESTRING", srid=4326), index=True)
