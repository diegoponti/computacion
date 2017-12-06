#!/usr/bin/env python
#-*- coding: UTF-8 -*-
from __future__ import division
from flask import Flask
from flask import render_template
from flask import send_from_directory
from flask import request
#from __future__ import division


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

	muestra = Aleatorio(valor,fecha,hora);

	mongoClient = MongoClient('localhost',27017) 	# conectar a mongo
	db = mongoClient.Aleatorio
	collection = db.Valores
	collection.insert(muestra.toDBCollection())


	# cursor = collection.find()
	# for elemento in cursor:
	#     print "%s - %s - %s " \
	#           %(elemento['valor'], elemento['fecha'], elemento['hora'])

	# #collection.update({"edad":{"$gt":30}},{"$inc":{"edad":100}}, upsert = False, multi = True)
	# #collection.remove({"internacional":True})
	mongoClient.close()















def obtener_limites_mongodb():
	###########################  MONGO DB  ######################
	global lista_superado
	global lista_no_superado
	global database
	global umbral

	url = 'http://www.numeroalazar.com.ar/'
	global cursor
	r = requests.get(url)
	patron1 = re.compile(r'\d{1,2}[.]\d{1,2}')
	fecha = time.strftime("%Y/%m/%d")
	hora = time.strftime("%X")
	valor = patron1.findall(r.text)[3]
	#print valor + ' ' +fecha +' '+ hora
	

	muestra = Aleatorio(valor,fecha,hora);

	mongoClient = MongoClient('localhost',27017) 	# conectar a mongo
	db = mongoClient.Aleatorio
	collection = db.Valores

	#collection.insert(muestra.toDBCollection())
	#print collection

	cursor = collection.find()
	data=cursor
	
	
	lista_superado=[] 
	lista_no_superado=[] 
	

		
	for elemento in data:
		if float(elemento['valor']) > float(umbral) :
	 		lista_superado.append([elemento['valor'], elemento['fecha'], elemento['hora']])
	 		#print 'a'
	 	else:
	 		lista_no_superado.append([elemento['valor'], elemento['fecha'], elemento['hora']])
	 		#print 'b'



								# database=[]
								
								# for elemento in cursor:																#solo lee el primer for --¿¿¿????
								#     database.append([elemento['valor'], elemento['fecha'], elemento['hora']])

								
								# print database
								# #collection.update({"edad":{"$gt":30}},{"$inc":{"edad":100}}, upsert = False, multi = True)
								# #collection.remove({"internacional":True})
								# mongoClient.close()

def obtener_database_mongo():
	global database
	global umbral

	url = 'http://www.numeroalazar.com.ar/'
	global cursor
	r = requests.get(url)
	patron1 = re.compile(r'\d{1,2}[.]\d{1,2}')
	fecha = time.strftime("%Y/%m/%d")
	hora = time.strftime("%X")
	valor = patron1.findall(r.text)[3]
	#print valor + ' ' +fecha +' '+ hora
	

	muestra = Aleatorio(valor,fecha,hora);

	mongoClient = MongoClient('localhost',27017) 	# conectar a mongo
	db = mongoClient.Aleatorio
	collection = db.Valores

	#collection.insert(muestra.toDBCollection())
	#print collection

	cursor = collection.find()
	data=cursor

	database=[]
	
	for elemento in cursor:																#solo lee el primer for --¿¿¿????
	    database.append([elemento['valor'], elemento['fecha'], elemento['hora']])

	
	#print database
	#collection.update({"edad":{"$gt":30}},{"$inc":{"edad":100}}, upsert = False, multi = True)
	#collection.remove({"internacional":True})
	mongoClient.close()

def calcular_media_mongo():
	global media
	global media_superior
	global media_inferior
	global a
	global b
	global c
	global umbral

	media =0.0
	#media_inferior=0.0
	#media_superior=0.0
	a=1
	#b=1
	#c=1



	mongoClient = MongoClient('localhost',27017) 	# conectar a mongo
	db = mongoClient.Aleatorio
	collection = db.Valores
	
	cursor = collection.find()
	data=cursor


												##Comentado porque solo entra al primer for
	# for elemento in cursor:
	# 	if float(elemento['valor']) > umbral :
	# 		media_superior= float(elemento['valor']) + media_superior
	# 		b=b+1
	# 		print 'b'
	# 	else:
	# 		media_inferior= float(elemento['valor']) + media_inferior
	# 		c=c+1
	# 		print 'c'

	
	#media_superior=media_superior/(b-1)
	#media_inferior=media_inferior/(c-1)

	for elemento in cursor:
		media = float(elemento['valor']) + media
		a=a+1

	media=media/(a-1)



	#print media
	#print media_superior
	#print media_inferior

	mongoClient.close()

def calcular_media_mongo_sup():
	global media
	global media_superior
	global media_inferior
	global a
	global b
	global c
	global umbral

	#media =0.0
	media_inferior=0.0
	media_superior=0.0
	#a=1
	b=0
	c=0



	mongoClient = MongoClient('localhost',27017) 	# conectar a mongo
	db = mongoClient.Aleatorio
	collection = db.Valores
	
	cursor = collection.find()
	data=cursor


												##Comentado porque solo entra al primer for
	for elemento in cursor:
		if float(elemento['valor']) > float(umbral) :
			media_superior= float(elemento['valor']) + media_superior
			b=b+1
			#print 'b'
		else:
			media_inferior= float(elemento['valor']) + media_inferior
			c=c+1
			#print 'c'

	
	media_superior=media_superior/(b)
	media_inferior=media_inferior/(c)

	# for elemento in cursor:
	# 	media = float(elemento['valor']) + media
	# 	a=a+1

	# media=media/(a-1)



	#print media
	#print media_superior
	#print media_inferior

	mongoClient.close()

def obtener_limites_sql():
	global umbral
	global lista_superado
	global lista_no_superado
	global database

	query_umbralsuperado = "SELECT * from N_aleatorio WHERE valor >= %f order by fecha desc LIMIT 30" %(float(umbral))
	run_query(query_umbralsuperado) 
	lista_superado=run_query(query_umbralsuperado) 
	#print lista_superado_sql


	query_umbral_no_superado = "SELECT * from N_aleatorio WHERE valor <= %f order by fecha desc LIMIT 30" %(float(umbral))
	run_query(query_umbral_no_superado)
	lista_no_superado=run_query(query_umbral_no_superado)
	#print lista_no_superado

	query_database= "SELECT * from N_aleatorio"
	run_query(query_database)
	database=run_query(query_database)


	#print database

def calcular_media_sql():
	global media
	global media_superior
	global media_inferior


	query_media = "select avg(valor) from N_aleatorio"
	run_query(query_media)
	media = run_query(query_media)[0]
	

	query_media_superada = "select avg(valor) from N_aleatorio where valor >= %f" %(float(umbral))
	run_query(query_media_superada)
	media_superior = run_query(query_media_superada)[0]

	query_media_no_superada = "select avg(valor) from N_aleatorio where valor <= %f" %(float(umbral))
	run_query(query_media_no_superada)
	media_inferior = run_query(query_media_no_superada)[0]

def obtener_limites_bbt():
	global database_bbt
	global database
	global lista_superado
	global lista_no_superado
	global umbral
	global d
	global f

	d = 0
	f= 0

	w, h = 3, 30;
	#dabatase=[]
	#database = [[0 for x in range(w)] for y in range(h)]
	#lista_superado = [[0 for x in range(w)] for y in range(h)]
	#lista_no_superado = [[0 for x in range(w)] for y in range(h)]
	
	lista_superado=[]
	lista_no_superado=[]

	num_bbt_valor = bbt.read("n_aleatorios","valor",limit=300)
	num_bbt_fecha = bbt.read("n_aleatorios","fecha",limit=300)
	num_bbt_hora = bbt.read("n_aleatorios","hora",limit=300)
	
	#umbral=request.form['umbral']
	


														# for i in range (0,30):
														#  	database[i][0]=num_bbt_valor[i]['data']
														# 	database[i][1]=num_bbt_fecha[i]['data']
														#  	database[i][2]=num_bbt_hora[i]['data']
		

														# for i in range (0,30):
														# 	if num_bbt_valor[i]['data'] > float(umbral):
														# 		lista_superado[d][0]=num_bbt_valor[i]['data']
														# 		lista_superado[d][1]=num_bbt_fecha[i]['data']
														#  		lista_superado[d][2]=num_bbt_hora[i]['data']
														#  		d=d+1
														#  	else:
														#  		lista_no_superado[f][0]=num_bbt_valor[i]['data']
														# 		lista_no_superado[f][1]=num_bbt_fecha[i]['data']
														#  		lista_no_superado[f][2]=num_bbt_hora[i]['data']
														#  		f=f+1

	for i in range(0,len(num_bbt_valor)):
	 	if num_bbt_valor[i]['data'] > float(umbral):
	 		lista_superado.append([num_bbt_valor[i]['data'],num_bbt_fecha[i]['data'],num_bbt_hora[i]['data']])
	 	else:
	 		lista_no_superado.append([num_bbt_valor[i]['data'],num_bbt_fecha[i]['data'],num_bbt_hora[i]['data']])
	 	
	#print lista_superado
	#print lista_no_superado

def obtener_database_bbt():
	global database
	global umbral

	num_bbt_valor = bbt.read("n_aleatorios","valor",limit=300)
	num_bbt_fecha = bbt.read("n_aleatorios","fecha",limit=300)
	num_bbt_hora = bbt.read("n_aleatorios","hora",limit=300)

	database=[]
	
	for i in range(0,len(num_bbt_valor)):																#solo lee el primer for --¿¿¿????
		database.append([num_bbt_valor[i]['data'],num_bbt_fecha[i]['data'],num_bbt_hora[i]['data']])

	#print database
	
def calcular_media_bbt():
	global media
	global lista
	global media_inferior
	global media_superior
	global media_inferior1
	global media_superior1
	global a
	global b
	global c
	global database
	
	num_bbt = bbt.read("n_aleatorios", "valor", limit=300)
	#database_bbt=num_bbt
	
	media= 0.0
	media_superior1 = 1
	media_inferior1 = 1
	media_superior = 0.0
	media_inferior = 0.0
	a = 1
	b= 1
	c= 1

	for i in range(0,len(num_bbt)):
		 
	     media=num_bbt[i]['data'] + media
	     #print num_bbt[i]['data']
	     lista=num_bbt[i]['data']
	     c=c+1

		
	for i in range(0,len(num_bbt)):

		if num_bbt[i]['data'] > float(umbral):
			media_superior= num_bbt[i]['data'] + media_superior
			a=a+1
			#print a
			#print media_superior1
			#media_superior=media_superior1/a
					
		else: 
			media_inferior= num_bbt[i]['data'] + media_inferior
			#media_inferior=media_inferior1/b
			b=b+1
		

	media = (media)/(c-1)
	media_superior =media_superior/(a-1)
	media_inferior = media_inferior/(b-1)
	

	
	#print media
	#print media_superior
	#print media_inferior
	


	
	












	
		


@app.route('/', methods=['GET','POST'] )
def index():
	global umbral
	global media_acumulada
	global media_sql
	global media_datos_superados
	global media_datos_no_superados
	global mensaje
	global mensaje1
	global mensaje2
	global lista_superado
	global lista_no_superado
	global flag

		
	if (request.method == 'GET'):
		print "Metodo GET"
		mensaje1 = 'sql'
		mensaje2 = 'sql'
		obtener_limites_sql()
		calcular_media_sql()
		return render_template("index2.html", umbral=umbral,database=database,
								lista_superado=lista_superado,lista_no_superado=lista_no_superado,
								media_acumulada=media,media_datos_superados=media_superior,media_datos_no_superados=media_inferior,
								mensaje1=mensaje1,mensaje2=mensaje2)# mensaje3=mensaje3)

	elif (request.form['boton1'] == 'Fijar Umbral'):
		if (request.form['db1'] == 'sql'):
			mensaje1 = 'sql'
			umbral=request.form['umbral']
			print umbral
			obtener_limites_sql()
			#calcular_media_sql()
			return render_template("index2.html",database=database, umbral=umbral,
									lista_superado=lista_superado,lista_no_superado=lista_no_superado,
									#media_acumulada=media,media_datos_superados=media_superior,media_datos_no_superados=media_inferior, 
									mensaje1=mensaje1)
		else:
			if (request.form['db1'] == 'bbt'):
				mensaje1= 'bbt'
				umbral=request.form['umbral']
				obtener_limites_bbt()
				obtener_database_bbt()
				#calcular_media_bbt()
				return render_template("index2.html",database=database, umbral=umbral,
													lista_superado=lista_superado,lista_no_superado=lista_no_superado,
													#media_acumulada=media,media_datos_superados=media_superior,media_datos_no_superados=media_inferior, 
													mensaje1=mensaje1)
			elif (request.form['db1'] == 'mongo'):
				mensaje1 = 'mongo'
				umbral=request.form['umbral']	
				obtener_limites_mongodb()
				obtener_database_mongo()
				#calcular_media_mongodb()
				return render_template("index2.html",database=database, umbral=umbral,
													lista_superado=lista_superado,lista_no_superado=lista_no_superado,
													#media_acumulada=media,media_datos_superados=media_superior,media_datos_no_superados=media_inferior, 
													mensaje1=mensaje1)
			else:
				print "No se eligio nada"

	elif (request.form['boton1'] == 'Calcular Media'):
		if (request.form['db2'] == 'sql2'):
			mensaje2= 'sql'
			#print "calcula media"
			calcular_media_sql()
			#obtener_limites_sql()					
			return render_template("index2.html", umbral=umbral,database=database,
												#lista_superado=lista_superado,lista_no_superado=lista_no_superado,
												media_acumulada=media,media_datos_superados=media_superior,media_datos_no_superados=media_inferior, 
												mensaje2=mensaje2)
			

		elif (request.form['db2']=='bbt2'):
			mensaje2= 'bbt'
			calcular_media_bbt()

			return render_template("index2.html", umbral=umbral,#database=database,
								   #lista_superado=lista_superado,lista_no_superado=lista_no_superado,
			 						media_acumulada=media,media_datos_superados=media_superior,media_datos_no_superados=media_inferior,
			 						mensaje2=mensaje2)
		
		elif (request.form['db2']=='mongo2'):
			mensaje2='mongodb'
			calcular_media_mongo()
			calcular_media_mongo_sup()
	 		return render_template("index2.html",  umbral=umbral,#database=database,
	 								#lista_superado=lista_superado,lista_no_superado=lista_no_superado,
									media_acumulada=media,media_datos_superados=media_superior,media_datos_no_superados=media_inferior,
								    mensaje2=mensaje2)

	else:
		if(flag):
			mensaje3= 'bbt'
			calcular_media_bbt()
			flag=0
		else:
			mensaje3='mongodb'
			calcular_media_mongo()
			calcular_media_mongo_sup()
			flag=1
		return render_template("index2.html", #umbral=umbral,#database=database,
								   #lista_superado=lista_superado,lista_no_superado=lista_no_superado,
			 						media_acumulada2=media,
			 						#media_datos_superados=media_superior,media_datos_no_superados=media_inferior,
			 						mensaje3=mensaje3)
		# else:
		# 	print "hecho"

@app.route('/loc')
def location(): 
	return '<p> UAH.EPS.EL10 </p>'



if __name__ == '__main__':
	global umbral
	global lista_superado
	global lista_no_superado
	global flag

	global media
	global media_superior
	global media_inferior
	
	
	global mensaje1
	global mensaje2
	global mensaje3
	
	# global database

	flag= 0
	
	umbral=50.00
	media = 00.00
	media_superior= 00.00
	media_inferior= 00.00
	
	#mensaje1 ='_'
	#mensaje2 ='_'
	#mensaje3 ='_'
	
	lista_superado = '.'
	lista_no_superado ='.'


	#obtener_dato()
	obtener_limites_sql()
	calcular_media_sql()

	#calcular_media_bbt()
	#obtener_limites_bbt()
	#obtener_database_bbt()
	
	#obtener_limites_mongodb()
	#calcular_media_mongo()
	#obtener_database_mongo()
	#calcular_media_mongo_sup()
	
	app.debug = True
	app.run(host ='0.0.0.0')