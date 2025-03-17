from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
import os

def get_index_path():
    return "index"

def get_index(path=None):
    if path is None:
        index_path=get_index_path()
    else:
        index_path=path
    schema = Schema(road_name=TEXT(stored=True), road_id=NUMERIC(stored=True), content=TEXT)
    if not os.path.exists(index_path):
        os.mkdir(index_path)
        ix = create_in(index_path, schema)
    else:
        ix = open_dir(index_path)
    return ix

def index_store(ix, word, id):
    writer = ix.writer()
    writer.add_document(road_name=word, road_id=id, content=word)
    writer.commit()

def index_search(ix, term):
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(term)
        results = searcher.search(query, limit=30)
    return results

