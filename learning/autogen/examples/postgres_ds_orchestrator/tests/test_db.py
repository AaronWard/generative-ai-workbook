"""
Unit tests for the PostgresManager class.

Written by: Aaron Ward - 2nd November 2023
"""
import pytest
import os
import sys
import dotenv
import psycopg2
sys.path.append('../')
from data.db import PostgresManager

dotenv.load_dotenv()
DB_URL = os.environ.get("POSTGRES_CONNECTION_URL")

@pytest.fixture
def db():
    with PostgresManager() as db_instance:
        db_instance.connect_with_url(DB_URL)
        yield db_instance

def test_connect_with_url(db):
    """Test if connection succeeded."""
    assert db.conn is not None
    assert db.cur is not None

def test_get_nonexistent(db):
    result = db.get("patients", 99999)  # Assuming ID 99999 doesn't exist
    assert result is None

def test_upsert(db):
    data = {
        "id": 100,
        "patient_id": "TESTID",
        "state": "TX",
        "fips": 99999,
        "diagnosed_covid": "f",
        "diagnoses_date": None,
        "current_age": 30,
        "age_at_diagnosis": None
    }
    db.upsert("patients", data)
    result = db.get("patients", 100)
    assert result is not None

def test_delete(db):
    db.delete("patients", 100)
    result = db.get("patients", 100)
    assert result is None

def test_get_all(db):
    results = db.get_all("patients")
    assert results is not None
    assert len(results) > 0

def test_run_sql(db):
    results = db.run_sql("SELECT * FROM patients LIMIT 5;")
    assert results is not None
    assert len(results) == 5

def test_get_table_definition(db):
    table_def = db.get_table_definition("patients")
    assert "CREATE TABLE patients" in table_def

def test_get_all_table_names(db):
    table_names = db.get_all_table_names()
    assert "patients" in table_names

def test_get_table_definitions_for_prompt(db):
    definitions = db.get_table_definitions_for_prompt()
    assert "CREATE TABLE patients" in definitions

def test_get_table_definition_structure(db):
    table_def = db.get_table_definition("patients")
    
    # Check for presence of certain keywords and structure
    assert table_def.startswith("CREATE TABLE patients (")
    assert "id" in table_def
    assert "patient_id" in table_def
    assert table_def.endswith(");")

def test_run_sql_invalid(db):
    with pytest.raises(psycopg2.errors.SyntaxError):
        db.run_sql("INVALID SQL STATEMENT")