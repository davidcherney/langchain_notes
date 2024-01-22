import sqlite3 
# from pydantic.v1 import BaseModel # I recall this being required.. but I'll try
from pydantic import BaseModel
from typing import List
from langchain.tools import Tool

conn = sqlite3.connect("db.sqlite")

def list_tables():
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE  type='table';")
    rows = c.fetchall() # Each item in this list is a 2-tuple with first item the table name, second item blank
    rows = [row[0] for row in rows if row[0] is not None]
    return "\n".join(rows)

def run_sqlite_query(query):
    c =  conn.cursor() #Cursor is the object that allows us to get access to the db.
    try:
        c.execute(query)
        return c.fetchall() 
    except sqlite3.OperationalError as err:
        return f"The following error occuerd: {str(err)}"

# create a child class to support the tool run_query_tool with... 
class RunQueryArgsSchema(BaseModel):
    query: str


run_query_tool = Tool.from_function(
    name="run_sqlite_query",
    description="Run a sqlite query.",
    func=run_sqlite_query,
    args_schema=RunQueryArgsSchema # provides specific 
)

def describe_tables(table_names):
    c = conn.cursor()
    "'users','orders','products'"
    tables = ', '.join("'"+ table + "'" for table in table_names) 
    rows = c.execute(f"SELECT sql FROM sqlite_master WHERE type='table' and name IN ({tables});")
    rows = [row[0] for row in rows if row[0] is not None]
    return '\n'.join(row[0] for row in rows if row[0] is not None)

class DescribeTablesArgsSchema(BaseModel):
    tables_names: List[str]

describe_tables_tool = Tool.from_function(
    name="describe_tables",
    description="Gven a list of table names, returns the schema of those tables.",
    func=describe_tables,
    args_schema=DescribeTablesArgsSchema 
)