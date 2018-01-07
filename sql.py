from flaskext.mysql import MySQL
from flask import *


class Sql:

    def __init__(self, app):
        self.mysql = MySQL()

        # MySQL configurations
        app.config['MYSQL_DATABASE_USER'] = 'test'
        app.config['MYSQL_DATABASE_PASSWORD'] = 'test'
        app.config['MYSQL_DATABASE_DB'] = 'pa'
        app.config['MYSQL_DATABASE_HOST'] = '10.211.55.3'
        self.mysql.init_app(app)

    def run_query(self, sql):
        # print("db ok")
        conn = self.mysql.connect()
        # vprint ("connection ok")
        cursor = conn.cursor()
        cursor.execute(sql)
        print ("description")
        print (cursor.description)
        data = cursor.fetchall()
        print (data)
        cursor.close()
        conn.close()
        return data

    def run_query_json(self, sql, values):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, values)

        rows = [x for x in cursor]
        cols = [x[0] for x in cursor.description]

        results = []

        for row in rows:
            result = {}
            for prop, val in zip(cols, row):
                result[prop] = val
            results.append(result)

        # Create a string representation of your array of results.
        resultsJSON = json.dumps(results)
        resultsJSONdata = '{ "data": ' + resultsJSON + '}'
        cursor.close()
        conn.close()
        print resultsJSONdata
        return resultsJSONdata


    def execute(self, sql, values):
        conn = self.mysql.connect()
        cursor= conn.cursor()
        cursor.execute(sql, values)
        result = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        return result

