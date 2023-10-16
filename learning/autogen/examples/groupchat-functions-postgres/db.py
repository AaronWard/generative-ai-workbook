"""
This script is a manager object for function calls
with a postgresql database

"""
import psycopg2
from psycopg2.sql import SQL, Identifier


class PostgresManager:
    def __init__(self):
        self.conn = None
        self.cur = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def connect_with_url(self, url):
        self.conn = psycopg2.connect(url)
        self.cur = self.conn.cursor()

    def upsert(self, table_name, _dict):
        columns = _dict.keys()
        values = [SQL("%s")] * len(columns)
        upsert_stmt = SQL(
            "INSERT INTO {} ({}) VALUES ({}) ON CONFLICT (id) DO UPDATE SET {}"
        ).format(
            Identifier(table_name),
            SQL(", ").join(map(Identifier, columns)),
            SQL(", ").join(values),
            SQL(", ").join(
                [SQL("{} = EXCLUDED.{}").format(Identifier(k), Identifier(k)) for k in columns]
            )
        )
        self.cur.execute(upsert_stmt, list(_dict.values()))
        self.conn.commit()

    def delete(self, table_name, _id):
        delete_stmt = SQL("DELETE FROM {} WHERE id = %s").format(Identifier(table_name))
        self.cur.execute(delete_stmt, (_id,))
        self.conn.commit()

    def get(self, table_name, _id):
        select_stmt = SQL("SELECT * FROM {} WHERE id = %s").format(Identifier(table_name))
        self.cur.execute(select_stmt, (_id,))
        return self.cur.fetchone()

    def get_all(self, table_name):
        select_all_stmt = SQL("SELECT * FROM {}").format(Identifier(table_name))
        self.cur.execute(select_all_stmt)
        return self.cur.fetchall()

    def run_sql(self, sql):
        self.cur.execute(sql)
        return self.cur.fetchall()

    def get_table_definition(self, table_name):
        get_def_stmt = """
        SELECT pg_class.relname as tablename, pg_attribute.attnum, pg_attribute.attname,
        format_type(atttypid, atttypmod)
        FROM pg_class
        JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
        JOIN pg_attribute ON pg_attribute.attrelid = pg_class.oid
        WHERE pg_attribute.attnum > 0
        AND pg_class.relname = %s
        AND pg_namespace.nspname = 'public'
        """
        
        self.cur.execute(get_def_stmt, (table_name, ))
        rows = self.cur.fetchall()
        
        create_table_stmt = "CREATE TABLE {} (\n".format(table_name)
        for row in rows:
            create_table_stmt += "{} {} , \n".format(row[2], row[3])
        
        create_table_stmt = create_table_stmt.rstrip(", \n") + ");"
        
        return create_table_stmt
