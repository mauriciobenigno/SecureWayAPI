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


# Limite GPS

LIMITE_GPS = 25

# Conexão com o SQL
conn = mysql.connector.connect(host=HOST_DB, database=NAME_DB, user=USER_DB, password=PASS_DB)


def abrirDB(self):
    self.conn = mysql.connector.connect(host=HOST_DB, database=NAME_DB, user=USER_DB, password=PASS_DB)


def fecharDB():
    if not conn == None:
        conn.close()

atexit.register(fecharDB)  # sempre que detectar que o terminal foi fechado, ele executa


#######################   ADJETIVOS  #########################

@app.route('/adjetivos/all', methods=['GET'])
def getAllAdjetivos():
    conn = mysql.connector.connect(host=HOST_DB, database=NAME_DB, user=USER_DB, password=PASS_DB)
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

#######################   ZONAS  #########################

@app.route('/zonas/all', methods=['GET'])
def getAllZonas():
    conn = mysql.connector.connect(host=HOST_DB, database=NAME_DB, user=USER_DB, password=PASS_DB)
    if conn.is_connected():
        adjetivos = []
        cursor = conn.cursor()
        cursor.execute('SELECT id_zona, coordenada_x, coordenada_y, densidade FROM sw_zona')
        row = cursor.fetchone()
        while row is not None:
            data = {'id_zona': row[0], 'coordenada_x': row[1], 'coordenada_y': row[2], 'densidade': row[3]}
            adjetivos.append(data)
            row = cursor.fetchone()
        conn.close()
        return jsonify(adjetivos), 200


@app.route('/zonas/regiao', methods=['POST'])
def getZonasByLocation():
    print(request.json)
    dataFromApp = request.json
    conn = mysql.connector.connect(host=HOST_DB, database=NAME_DB, user=USER_DB, password=PASS_DB)
    if conn.is_connected():
        zonas = []
        cursor = conn.cursor()

        queryInsert = """ 
        SELECT id_zona,coordenada_x,coordenada_y, densidade, 
            (6371 * acos( cos( radians({}) ) * cos( radians( coordenada_x ) ) * cos( radians( coordenada_y ) - radians({}) ) + sin( radians({}) ) * sin( radians(coordenada_x) ) ) ) distancia
        FROM sw_zona HAVING distancia < {} order by distancia
        """.format(dataFromApp['latitude'],dataFromApp['longitude'],dataFromApp['latitude'], LIMITE_GPS)
        cursor.execute(queryInsert)

        row = cursor.fetchone()
        while row is not None:
            data = {'id_zona': row[0], 'coordenada_x': row[1], 'coordenada_y': row[2], 'densidade': row[3]}
            zonas.append(data)
            row = cursor.fetchone()
        conn.close()
        return jsonify(zonas), 201

@app.route('/zonas/proxima', methods=['POST'])
def getZonaByLocation():
    print(request.json)
    dataFromApp = request.json
    conn = mysql.connector.connect(host=HOST_DB, database=NAME_DB, user=USER_DB, password=PASS_DB)
    if conn.is_connected():
        zonas = []
        cursor = conn.cursor()

        queryInsert = """ 
        SELECT id_zona,coordenada_x,coordenada_y, densidade, 
            (6371 * acos( cos( radians({}) ) * cos( radians( coordenada_x ) ) * cos( radians( coordenada_y ) - radians({}) ) + sin( radians({}) ) * sin( radians(coordenada_x) ) ) ) distancia
        FROM sw_zona HAVING distancia < {} order by distancia limit 1
        """.format(dataFromApp['latitude'],dataFromApp['longitude'],dataFromApp['latitude'], LIMITE_GPS)
        cursor.execute(queryInsert)

        row = cursor.fetchone()
        while row is not None:
            data = {'id_zona': row[0], 'coordenada_x': row[1], 'coordenada_y': row[2], 'densidade': row[3]}
            zonas.append(data)
            row = cursor.fetchone()

        if zonas[0] is None:
            cursor = conn.cursor()
            queryInsert = """ 
            INSERT INTO 
                sw_zona(coordenada_x, coordenada_y, densidade)
            VALUES 
                ({}, {}, {})
            """.format(dataFromApp['coordenada_x'], dataFromApp['coordenada_y'], 500)
            cursor.execute(queryInsert)
            idZona = cursor.lastrowid
            conn.commit()

            cursor = conn.cursor()
            queryInsert = """ 
            SELECT id_zona,coordenada_x,coordenada_y, densidade
            FROM sw_zona WHERE id_zona = {}
            """.format(idZona)
            cursor.execute(queryInsert)

            row = cursor.fetchone()
            while row is not None:
                data = {'id_zona': row[0], 'coordenada_x': row[1], 'coordenada_y': row[2], 'densidade': row[3]}
                zonas.append(data)
                row = cursor.fetchone()

        return jsonify(zonas), 201

@app.route('/zonas/newpost', methods=['POST'])
def addZona():
    print(request.json)
    dataFromApp = request.json
    conn = mysql.connector.connect(host=HOST_DB, database=NAME_DB, user=USER_DB, password=PASS_DB)
    if conn.is_connected():
        cursor = conn.cursor()
        queryInsert = """ 
        INSERT INTO 
            sw_zona(coordenada_x, coordenada_y, densidade)
        VALUES 
            ({}, {}, {})
        """.format(dataFromApp['coordenada_x'],dataFromApp['coordenada_y'],dataFromApp['densidade'])
        cursor.execute(queryInsert)
        dataFromApp['id_zona'] = cursor.lastrowid
        conn.commit()
        return jsonify(dataFromApp), 201

#######################   REPORT  #########################

@app.route('/report/all', methods=['GET'])
def getAllReports():
    conn = mysql.connector.connect(host=HOST_DB, database=NAME_DB, user=USER_DB, password=PASS_DB)
    if conn.is_connected():
        reports = []
        cursor = conn.cursor()
        cursor.execute('SELECT id_report, id_zona, numero, data_report, densidade, observacao FROM sw_report')
        row = cursor.fetchone()
        while row is not None:
            data = {'id_report': row[0], 'id_zona': row[1], 'numero': row[2], 'data_report': row[3], 'densidade': row[4], 'observacao': row[5]}
            reports.append(data)
            row = cursor.fetchone()
        conn.close()
        return jsonify(reports), 200

@app.route('/report/newreport', methods=['POST'])
def addReport():
    print(request.json)
    dataFromApp = request.json

    # montar objetos
    report = dataFromApp['first']
    local = dataFromApp['second']

    conn = mysql.connector.connect(host=HOST_DB, database=NAME_DB, user=USER_DB, password=PASS_DB)
    if conn.is_connected():
        # Validar a zona
        zonas = []
        cursor = conn.cursor()

        queryInsert = """ 
                SELECT id_zona,coordenada_x,coordenada_y, densidade, 
                    (6371 * acos( cos( radians({}) ) * cos( radians( coordenada_x ) ) * cos( radians( coordenada_y ) - radians({}) ) + sin( radians({}) ) * sin( radians(coordenada_x) ) ) ) distancia
                FROM sw_zona HAVING distancia < {} order by distancia limit 1
                """.format(local['latitude'], local['longitude'], local['latitude'], LIMITE_GPS)
        cursor.execute(queryInsert)

        row = cursor.fetchone()
        while row is not None:
            data = {'id_zona': row[0], 'coordenada_x': row[1], 'coordenada_y': row[2], 'densidade': row[3]}
            zonas.append(data)
            row = cursor.fetchone()

        if  len(zonas) <= 0:
            cursor = conn.cursor()
            queryInsert = """ 
            INSERT INTO 
                sw_zona(coordenada_x, coordenada_y, densidade)
            VALUES 
                ({}, {}, {})
            """.format(local['latitude'], local['longitude'], 500)
            cursor.execute(queryInsert)
            idZona = cursor.lastrowid
            conn.commit()
            report['id_zona'] = idZona
        else:
            print(len(zonas))
            print(zonas)
            zonaValida = zonas[0]
            report['id_zona'] = zonaValida['id_zona']

        # Registrar o report
        print(report)
        cursor = conn.cursor()
        queryInsert = """ 
                INSERT INTO 
                    sw_report(id_zona, numero, data_report, densidade)
                VALUES 
                    ({},{}, {}, {})
                """.format(report['id_zona'], report['numero'], report['data_report'], report['densidade'])
        cursor.execute(queryInsert)
        report['id_report'] = cursor.lastrowid
        conn.commit()

        # fecha conexão com o banco de dados
        conn.close()
    print(report)
    return jsonify(report), 201

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
