import os
from flask import Flask, jsonify, request, session
from flask_cors import CORS

import mysql.connector
from mysql.connector import Error
import atexit  # para fechar a conn com o banco sempre que a api fechar

from functools import wraps
import jwt
# import datetime
from datetime import datetime, timedelta

# Flask
app = Flask(__name__)

HOST_DB = 'us-cdbr-east-03.cleardb.com'
NAME_DB = 'heroku_22222dd8dc7c8d4'
USER_DB = 'b99517f5d775e7'
PASS_DB = '633fdcec'

# Conexão com o SQL
conn = mysql.connector.connect(host=HOST_DB, database=NAME_DB, user=USER_DB, password=PASS_DB)


def abrirDB(self):
    self.conn = mysql.connector.connect(host=HOST_DB, database=NAME_DB, user=USER_DB, password=PASS_DB)


def fecharDB():
    if not conn == None:
        conn.close()

atexit.register(fecharDB)  # sempre que detectar que o terminal foi fechado, ele executa


#######################   GET  #########################

@app.route('/adjetivos/all', methods=['GET'])
def getAllAdjetivos():
    abrirDB(conn)
    if conn.is_connected():
        adjetivos = []
        cursor = conn.cursor()
        cursor.execute('SELECT id_adjetivo, negativo,descricao FROM sw_adjetivo')
        row = cursor.fetchone()
        while row is not None:
            data = {'id_adjetivo': row[0], 'negativo': row[1], 'descricao': row[2]}
            adjetivos.append(data)
            row = cursor.fetchone()
        conn.close()
        return jsonify(adjetivos), 200

########### INIT E TESTE ##########

@app.route('/teste', methods=['GET'])
def testeSQL():
    conn = mysql.connector.connect(host=HOST_DB, database=NAME_DB, user=USER_DB, password=PASS_DB)
    if conn.is_connected():
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        row = cursor.fetchone()
        conn.close()
        return jsonify("Database version : %s " % row), 200


def main():
    abrirDB(conn)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
