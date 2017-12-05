#!/usr/bin/env python
#-*- coding: UTF-8 -*-

from flask import Flask
from flask import render_template
from flask import send_from_directory
from flask import request

import re
import requests
import datetime
import time
import MySQLdb
from beebotte import *

from pymongo import MongoClient
from Aleatorio import Aleatorio


app = Flask(__name__)


Apy_key = '2b5de53d53a1e964c6883503419f90b9'
Secret_Number = 'd63c899e291a7677c2f5281c27b59c95ca9d12db64d9724330a2db1b0148f089'
Channel_Token = '1510156441853_8sSc491F8yBRmF0u'
_hostname   = 'api.beebotte.com'

bbt = BBT( Apy_key, Secret_Number, hostname = _hostname)    # Concetar a beebotte

DB_HOST = '127.0.0.1'										# Datos para conectar a mySql
DB_USER = 'root'
DB_PASS = 'mysqlroot'
DB_NAME = 'Numeros_aleatorios'

def run_query(query=''): 		
	datos=[DB_HOST, DB_USER, DB_PASS, DB_NAME]  			
	conn = MySQLdb.connect(*datos) # Conectar a la base de datos 
	cursor = conn.cursor()         # Crear un cursor 
	cursor.execute(query)          # Ejecutar una consulta 

	if query.upper().startswith('SELECT'):
		data = cursor.fetchall()   # Traer los resultados de un select 
	else: 
		conn.commit()              # Hacer efectiva la escritura de datos  	  
		data = None 

	cursor.close()                 # Cerrar el cursor 
	conn.close()                   # Cerrar la conexión 
	return data
	

def obtener_dato():

	global umbral
	umbral = 50.00						#puesto de prueba
	url = 'http://www.numeroalazar.com.ar/'

	r = requests.get(url)

	patron1 = re.compile(r'\d{1,2}[.]\d{1,2}')
	fecha = time.strftime("%Y/%m/%d")
	hora = time.strftime("%X")

	valor = patron1.findall(r.text)[3]

	print valor + ' ' +fecha +' '+ hora
	print patron1

	###########################  MYSQL  ##########################

	query = "INSERT INTO N_aleatorio (valor, fecha , hora) VALUES ('%f','%s','%s')" %(float(valor), fecha, hora)

	run_query(query)

	###########################  BEEBOTTE  #####################

	bbt.write("n_aleatorios", "valor", float(valor))

	bbt.write("n_aleatorios", "fecha", str(fecha))

	bbt.write("n_aleatorios", "hora", str(hora))

	# ###########################  MONGO DB  ######################

	# muestra = Aleatorio(valor,fecha,hora);

	# mongoClient = MongoClient('localhost',27017) 	# conectar a mongo
	# db = mongoClient.Aleatorio
	# collection = db.Valores
	# collection.insert(muestra.toDBCollection())


	# cursor = collection.find()
	# for elemento in cursor:
	#     print "%s - %s - %s " \
	#           %(elemento['valor'], elemento['fecha'], elemento['hora'])

	# #collection.update({"edad":{"$gt":30}},{"$inc":{"edad":100}}, upsert = False, multi = True)
	# #collection.remove({"internacional":True})
	# mongoClient.close()




def mongo_db_prueba():
	###########################  MONGO DB  ######################
	global lista_superado_mongo
	global lista_no_superado_mongo

	url = 'http://www.numeroalazar.com.ar/'
	global cursor
	r = requests.get(url)

	patron1 = re.compile(r'\d{1,2}[.]\d{1,2}')
	fecha = time.strftime("%Y/%m/%d")
	hora = time.strftime("%X")

	valor = patron1.findall(r.text)[3]

	print valor + ' ' +fecha +' '+ hora
	

	muestra = Aleatorio(valor,fecha,hora);

	mongoClient = MongoClient('localhost',27017) 	# conectar a mongo
	db = mongoClient.Aleatorio
	collection = db.Valores

	#collection.insert(muestra.toDBCollection())
	#print collection

	cursor = collection.find()
	#print cursor
	# for nn in cursor:
	#     print "%s - %s - %s - " \
	#           %(nn['valor'], nn['fecha'], nn['hora'])

	for elemento in cursor:
		if elemento['valor']> umbral :
			lista_superado_mongo = elemento['valor'], elemento['fecha'], elemento['hora']
		else:
			lista_no_superado_mongo= elemento['valor'], elemento['fecha'], elemento['hora']

	#lista_no_superado = cursor
	print lista_superado_mongo
	# print lista_no_superado
	#collection.update({"edad":{"$gt":30}},{"$inc":{"edad":100}}, upsert = False, multi = True)
	#collection.remove({"internacional":True})
	mongoClient.close()

def obtener_limites_sql():
	global umbral
	global lista_superado_sql
	global lista_no_superado_sql
	global database_sql

	query_umbralsuperado = "SELECT * from N_aleatorio WHERE valor >= %f order by fecha desc LIMIT 30" %(float(umbral))
	run_query(query_umbralsuperado) 
	lista_superado_sql=run_query(query_umbralsuperado) 
	#print lista_superado


	query_umbral_no_superado = "SELECT * from N_aleatorio WHERE valor <= %f order by fecha desc LIMIT 30" %(float(umbral))
	run_query(query_umbral_no_superado)
	lista_no_superado_sql=run_query(query_umbral_no_superado)
	#print lista_no_superado

	query_database= "SELECT * from N_aleatorio"
	run_query(query_database)
	database_sql=run_query(query_database)


def calcular_media_sql():
	global media_sql
	global media_superior_sql
	global media_inferior_sql

	
	query_media = "select avg(valor) from N_aleatorio"
	run_query(query_media)
	media_sql = run_query(query_media)[0]
	

	query_media_superada = "select avg(valor) from N_aleatorio where valor >= %f" %(float(umbral))
	run_query(query_media_superada)
	media_superior_sql = run_query(query_media_superada)[0]

	query_media_no_superada = "select avg(valor) from N_aleatorio where valor <= %f" %(float(umbral))
	run_query(query_media_no_superada)
	media_inferior_sql = run_query(query_media_no_superada)[0]

def calcular_media_bbt():
	global media
	global lista
	global media_inferior
	global media_superior
	global a
	global b
	global c

	num_bbt = bbt.read("n_aleatorios", "valor", limit=30)
	#print num_bbt[ ]['data']
	media = 0.0
	media_superior = 0.0
	media_inferior = 0.0
	a = 0.0
	b= 0.0
	c= 0.0

	for i in range(0,30):
		 
	     media=num_bbt[i]['data'] + media
	     print num_bbt[i]['data']
	     lista=num_bbt[i]['data']
	     #c=c+1
	media = media/30
	print media

	for i in range(0,30):
		if num_bbt[i]['data'] > umbral:
			a=a+1
			media_superior= num_bbt[i]['data'] +media_superior
			
		else: 
			b=b+1
			media_inferior= num_bbt[i]['data'] + media_inferior
	
	media_superior=media_superior/a
	media_inferior=media_inferior/b

	print media_superior
	print media_inferior
		


@app.route('/', methods=['GET','POST'] )
def index():
	global umbral
	global media_acumulada
	global media_datos_superados
	global media_datos_no_superados
	global mensaje
	global lista

		
	if (request.method == 'GET'):
		print "Metodo GET"
		calcular_media_sql()
		obtener_limites_sql()
		return render_template("index.html",database=database_sql, umbral=umbral,lista_superado=lista_superado_sql,lista_no_superado=lista_no_superado_sql,
								media_acumulada=media_sql,media_datos_superados=media_superior_sql,
								media_datos_no_superados=media_inferior_sql)
	else:
		if (request.form['boton'] == 'Calcular Media') or (request.form['boton'] == 'Fijar Umbral'):
			if (request.form['db'] == 'sql'):
				mensaje= 'sql'
				calcular_media_sql()
								
				return render_template("index.html",database=database_sql, umbral=umbral,media_acumulada=media_sql,media_datos_superados=media_superior_sql,
											media_datos_no_superados=media_inferior_sql, mensaje=mensaje,)

			else:# 
				if(request.form['db']=='bbt'):
					mensaje= 'bbt'
					calcular_media_bbt()
					return render_template("index.html", database=num_btt, umbral=umbral,media_acumulada=media_bbt,media_datos_superados=media_superior_bbt,
											media_datos_no_superados=media_inferior_bbt, mensaje=mensaje)
				else:
					mensaje='mongodb'
					calcular_media_bbt()
					return render_template("index.html", database=cursor, umbral=umbral,
											media_acumulada=media_mongo,media_datos_superados=media_superior_mongo,
											media_datos_no_superados=media_inferior_mongo, mensaje=mensaje)

		
		else:
			if (request.form['boton'] == 'Fijar Umbral'):
				umbral=request.form['umbral']
				if (request.form['db'] == 'sql'):
					umbral=request.form['umbral']
					mensaje= 'sql'
					print 'pulsado'
					obtener_limites_sql()
					calcular_media_sql()

					return render_template("index.html",database=database_sql, umbral=umbral,lista_superado=lista_superado_sql,lista_no_superado=lista_no_superado_sql
													,mensaje=mensaje)
						
				else:
					if(request.form['db']=='bbt'):
						umbral=request.form['umbral']
						mensaje= 'bbt'
						calcular_media_bbt()
						return render_template("index.html", database=num_btt, umbral=umbral,lista_superado=lista_superado_bbt,
												lista_no_superado=lista_no_superado_bbt,mensaje=mensaje)
					else:
						umbral=request.form['umbral']
						mensaje='mongodb'
						calcular_media_bbt()
						return render_template("index.html", database=cursor, umbral=umbral,lista_superado=lista_superado_mongo,
												lista_no_superado=lista_no_superado_mongo, mensaje=mensaje)
	 			
			#umbral=request.form['umbral']
	 		#obtener_limites_sql()
	 		# mongo_db_prueba()
			# return render_template("index.html", umbral=umbral,database=database_sql,lista_superado=lista_superado_mongo,lista_no_superado=lista_no_superado_mongo)#,
   #   								#media_acumulada=media_acumulada)#,media_datos_superados=media_datos_superados,
   #   								#media_datos_no_superados=media_datos_no_superados)
		


@app.route('/loc')
def location(): 
	return '<p> UAH.EPS.EL10 </p>'



if __name__ == '__main__':
	global umbral
	global lista_superado
	global lista_no_superado
	global media_sql
	global media_superior_sql
	global media_inferior_sql
	global db
	global mensaje
	global lista

	umbral=50.00
	media_acumulada = 00.00
	media_datos_superados = 00.00
	media_datos_no_superados =00.00 
	#obtener_dato()
	obtener_limites_sql()
	calcular_media_bbt()
	mongo_db_prueba()
	app.debug = True
	app.run(host ='0.0.0.0')