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
	url = 'http://www.numeroalazar.com.ar/'

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

	collection.insert(muestra.toDBCollection())
	print collection

	cursor = collection.find()
	for nn in cursor:
	    print "%s - %s - %s - " \
	          %(nn['valor'], nn['fecha'], nn['hora'])

	#collection.update({"edad":{"$gt":30}},{"$inc":{"edad":100}}, upsert = False, multi = True)
	#collection.remove({"internacional":True})
	mongoClient.close()

def obtener_limites():
	global umbral
	global lista_superado
	global lista_no_superado

	query_umbralsuperado = "SELECT * from N_aleatorio WHERE valor >= %f order by fecha desc LIMIT 30" %(float(umbral))
	run_query(query_umbralsuperado) 
	lista_superado=run_query(query_umbralsuperado) 
	#print lista_superado


	query_umbral_no_superado = "SELECT * from N_aleatorio WHERE valor <= %f order by fecha desc LIMIT 30" %(float(umbral))
	run_query(query_umbral_no_superado)
	lista_no_superado=run_query(query_umbral_no_superado)
	#print lista_no_superado



def calcular_media():
	global media_acumulada
	global media_datos_superados
	global media_datos_no_superados


	query_media = "select avg(valor) from N_aleatorio"
	run_query(query_media)
	media_acumulada = run_query(query_media)[0]
	

	query_media_superada = "select avg(valor) from N_aleatorio where valor >= %f" %(float(umbral))
	run_query(query_media_superada)
	media_datos_superados = run_query(query_media_superada)[0]

	query_media_no_superada = "select avg(valor) from N_aleatorio where valor <= %f" %(float(umbral))
	run_query(query_media_no_superada)
	media_datos_no_superados = run_query(query_media_no_superada)[0]

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

	for i in range(0,30):
		if num_bbt[i]['data'] > umbral:
			a=a+1
			media_superior= num_bbt[i]['data'] +media_superior
		else: 
			b=b+1
			media_inferior= num_bbt[i]['data'] + media_inferior
	media_datos_superados=media_superior/a
	media_datos_no_superados=media_inferior/b

	print media_datos_superados
	print media_datos_no_superados
		


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
		
		obtener_limites()
		return render_template("index.html", umbral=umbral,lista_superado=lista_superado,lista_no_superado=lista_no_superado,
								media_acumulada=media_acumulada,media_datos_superados=media_datos_superados,
								media_datos_no_superados=media_datos_no_superados)
	else:
		if (request.form['boton'] == 'Calcular Media'):
			if (request.form['db'] == 'sql'):
				mensaje= 'sql'
				calcular_media()
				return render_template("index.html", umbral=umbral,lista_superado=lista_superado,lista_no_superado=lista_no_superado,
	 									media_acumulada=media_acumulada,media_datos_superados=media_datos_superados,
										media_datos_no_superados=media_datos_no_superados, mensaje=mensaje)

			else:# (request.form['db']=='bbt'):
				mensaje= 'bbt'
				calcular_media_bbt()
				return render_template("index.html", umbral=umbral,lista_superado=lista_superado,lista_no_superado=lista_no_superado,
										media_acumulada=media,media_datos_superados=media_datos_superados,
										media_datos_no_superados=media_datos_no_superados, mensaje=mensaje)

		
		else:
			umbral=request.form['umbral']
	 		obtener_limites()
	 		#if 	(umbral == '13.00'):
	 		#		print "Finalizado"

			return render_template("index.html", umbral=umbral,lista_superado=lista_superado,lista_no_superado=lista_no_superado)#,
     								#media_acumulada=media_acumulada)#,media_datos_superados=media_datos_superados,
     								#media_datos_no_superados=media_datos_no_superados)
		


@app.route('/loc')
def location(): 
	return '<p> UAH.EPS.EL10 </p>'



if __name__ == '__main__':
	global umbral
	global lista_superado
	global lista_no_superado
	global media_acumulada
	global media_datos_superados
	global media_datos_no_superados
	global db
	global mensaje
	global lista

	umbral=50.00
	media_acumulada = 00.00
	media_datos_superados = 00.00
	media_datos_no_superados =00.00 
	#obtener_dato()
	obtener_limites()
	#calcular_media_bbt()
	mongo_db_prueba()
	app.debug = True
	app.run(host ='0.0.0.0')