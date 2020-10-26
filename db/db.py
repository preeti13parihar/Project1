import os
import pymysql
from config import config 

env = config.GetEnvObj()

DBHOST = env("PBOX_DBHOST") if env("PBOX_DBHOST") else os.getenv("PBOX_DBHOST", None)
DBNAME = env("PBOX_DBNAME") if env("PBOX_DBNAME") else os.getenv("PBOX_DBNAME", None)
USERNAME = env("PBOX_DB_USERNAME") if env("PBOX_DB_USERNAME") else os.getenv("PBOX_DB_USERNAME", None)
PASSWORD = env("PBOX_DB_PASSWORD") if env("PBOX_DB_PASSWORD") else os.getenv("PBOX_DB_PASSWORD", None)


class Database():
    def validate_db_init(self, ):
        print(DBHOST, USERNAME, PASSWORD)
        return (DBHOST and USERNAME and PASSWORD)

    def connect(self,):
        return pymysql.connect(host=DBHOST, database=DBNAME, user=USERNAME, password=PASSWORD)

    def read(self, id, username=None):
        try:
            con = Database.connect(self)
            cursor = con.cursor()
        except Exception as e:
            return str(e), 500

        try:

            if id == None and username==None:
                cursor.execute("SELECT * FROM fileuploads order by username asc")
            elif username:
                cursor.execute("SELECT * FROM fileuploads where username = %s order by createdAt asc", (username,))
            else:
                cursor.execute("SELECT * FROM fileuploads where id = %s order by username asc", (id,))

            return cursor.fetchall(), 200
        except Exception as e:
            print(e)
            return str(e), 500
        finally:
            con.close()

    def insert(self, data):
        try:
            con = Database.connect(self)
            cursor = con.cursor()
        except Exception as e:
            return str(e), 500

        try:
            res = cursor.execute("INSERT INTO fileuploads(username,firstname,lastname,uploadTime,description,filekey) \
                VALUES(%s, %s, %s, %s, %s, %s)", (data['username'],data['firstname'],data['lastname'], \
                    data['uploadTime'], data['description'], data['filekey']))

            con.commit()

            return res, 200
        except Exception as e:
            con.rollback()
            return str(e), 500

        finally:
            con.close()

    def update(self, id, data):
        try:
            con = Database.connect(self)
            cursor = con.cursor()
        except Exception as e:
            return str(e), 500

        try:
            res = cursor.execute("UPDATE fileuploads set username = %s, firstname = %s, lastname = %s \
                uploadTime = %s, updatedAt = %s, description = %s \
                where id = %s", ((data['username'],data['firstname'],data['lastname'], \
                    data['uploadTime'],data['updatedAt'],data['description'],id,)))

            con.commit()

            return res, 201
        except Exception as e:
            con.rollback()
            return str(e), 500

        finally:
            con.close()

    def delete(self, id):
        try:
            con = Database.connect(self)
            cursor = con.cursor()
        except Exception as e:
            return str(e), 500

        try:
            res = cursor.execute("DELETE FROM fileuploads where id = %s", (id,))
            con.commit()

            return res, 204
        except Exception as e:
            con.rollback()
            return str(e), 500
            
        finally:
            con.close()