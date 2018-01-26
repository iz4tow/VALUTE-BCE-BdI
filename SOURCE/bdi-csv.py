import requests
#import jaydebeapi
#import jpype
import time
from ftplib import FTP
import sqlite3
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


cambi_file="cambigg.csv"
#CONNESSIONE A DB2
#jar = 'db2jcc4.jar' # location of the jdbc driver jar
#args='-Djava.class.path=%s' % jar
#jvm = jpype.getDefaultJVMPath()
#jpype.startJVM(jvm, args)
#conn=jaydebeapi.connect('com.ibm.db2.jcc.DB2Driver', 'jdbc:db2://10.1.12.69:50000/s69mk0se',['db2inst1','db2inst1']) #connessione al db2
#curs=conn.cursor()
#########FINE DB2

oggi=time.strftime('%Y-%m-%d')#data di oggi
#oggi='2018-01-24'



################################################################################################
################################FUNZIONE VERIFICA CAMBI#########################################
################################################################################################

def verifica_cambi():
	file = open(bdi,"r")
	###########CONNESSIONE SQLITE
	conn = sqlite3.connect('valute.db')
	curs = conn.cursor()
	###########FINE SQLITE
	curs.execute("SELECT esecuzione,errore FROM applicazione")
	rows=curs.fetchall()
	if len(rows)>0:#VERIFICA TABELLA DEGLI ERRORI
		errore_bdi=2
		print ("VERIFICARE LA TABELLA applicazione")
		sys.exit(errore_bdi)
	try:#PREPARO LA TABELLA VALUTE PER L'IMPORTAZIONE ELIMINANDO EVENTUALI RESIDUATI
		curs.execute("DELETE FROM VALUTE")
		curs.execute("commit")
	except:
		print ("IMPOSSIBILE ACCEDERE A TABELLA VALUTE")
		errore_bdi=99
		sys.exit(errore_bdi)
	try:
		curs.execute("INSERT INTO applicazione (esecuzione,errore) VALUES (1,0)")
		curs.execute("commit")
	except:
		print ("IMPOSSIBILE ACCEDERE A TABELLA APPLICAZIONE")
		errore_bdi=99
		sys.exit(errore_bdi)
	
	for riga in cambigg.splitlines():#SCRIVO SUL DATABASE I CAMBI DI OGGI
		paese,valuta,iso,uic,quotazione,convenzione,data=riga.split(",")
		convenzione=convenzione.replace("'","")
		try:#INSERIMENTO VALUTA
			curs.execute("INSERT INTO VALUTE (paese,valuta,iso,uic,quotazione,convenzione,data) VALUES ('"+paese+"','"+valuta+"','"+iso+"','"+uic+"','"+quotazione+"','"+convenzione+"','"+data+"')")
		except:
			print ("ERRORE INSERIMENTO IN TABELLA VALUTE")
			errore_bdi=5
			sys.exit(errore_bdi)
		try:
			curs.execute("commit")
		except:
			print ("ERRORE INSERIMENTO IN TABELLA VALUTE")
			errore_bdi=5
			sys.exit(errore_bdi)


##############CONTROLLO DATE!!!
	variazione=""
	try:#SELEZIONO DALLE TABELLE LE DATE
		curs.execute("SELECT data FROM VALUTE")
		rows=curs.fetchall()
		data=rows[3][0]
		curs.execute("SELECT data FROM VALUTE_IERI")
		rows=curs.fetchall()
		data_ieri=rows[3][0]
	except:
		print ("ERRORE CONFRONTO DATE - IMPOSSIBILE LEGGERE DATI")
		data_ieri='123stella'

	if data==data_ieri:#CONFRONTO
		print ("ERRORE CONFRONTO DATE - DATA IDENTICA"+data+data_ieri)
		errore_bdi=9
		sys.exit(errore_bdi)
##############FINE CONTROLLO DATE!!!

##############CONTROLLO SCOSTAMENTO PERCENTUALE
	curs.execute("SELECT iso,quotazione FROM VALUTE")
	riga_valuta=curs.fetchall()
	for valuta in riga_valuta:
		iso=valuta[0]
		quotazione=valuta[1]
		curs.execute("SELECT quotazione FROM VALUTE_IERI WHERE iso='"+iso+"'")
		riga_valuta_ieri=curs.fetchall()
		try:
			quotazione_ieri=riga_valuta_ieri[0][0]
			scostamento=(quotazione_ieri*100/quotazione)-100
			if scostamento>2 or scostamento<-2:
				print ("SCOSTAMENTO DELLA VALUTA "+iso+" SUPERIORE A 1%, SCOSTAMENTO DEL "+str(scostamento)+"%")
				variazione=variazione+"SCOSTAMENTO DELLA VALUTA "+iso+" SUPERIORE A 1%, SCOSTAMENTO DEL "+str(scostamento)+"%<br>"
		except Exception as e:
			print(e)
			variazione=variazione+"SALTATO CONTROLLO PER ISO: "+iso+"<br>"
##############FINE CONTROLLO SCOSTAMENTO PERCENTUALE

	try:#PROVO A SVUOTARE I CAMBI PRECEDENTI
		curs.execute("DELETE FROM VALUTE_IERI")
	except:
		print ("ERRORE SVUOTAMENTO VALUTE_IERI")
		errore_bdi=3
		sys.exit(errore_bdi)
	try:#SPOSTO I CAMBI NELLA TABELLA VALUTE_IERI PER SUCCESSIVI CONFRONTI
		curs.execute("INSERT INTO VALUTE_IERI SELECT * FROM VALUTE")
	except:
		print("ERRORE COPIA IN VALUTE_IERI")
		errore_bdi=4
		sys.exit(errore_bdi)
	
	try:#SVUOTO LA TABELLA DI CONTROLLO APPLICAZIONE e la VALUTE 
		curs.execute("DELETE FROM APPLICAZIONE")
		curs.execute("DELETE FROM VALUTE")
	except:
		print("ERRORE IN PULIZIA TABELLA APPLICAZIONE")
		errore_bdi=7
		sys.exit(errore_bdi)
	
	try:#COMMIT FINALE
		curs.execute("commit")
	except:
		print("ERRORE IN COMMIT FINALE")
		errore_bdi=6
		sys.exit(errore_bdi)
	if variazione!="":#se c'è stato scostamento > 1% INVIA LA MAIL A ME
		mail_variazioni = MIMEMultipart()
		mail_variazioni['From'] = "inviofatture@melchioni.it"
		mail_variazioni['To'] = "f.avino@melchioni.it"
		mail_variazioni['Subject'] = "VERIFICARE VARIAZIONE STATISTICA CAMBI"
		corpo=variazione

		mail_variazioni.attach(MIMEText(corpo, 'html'))
		server = smtplib.SMTP('owa.melchioni.it', 25)
		server.starttls()
		server.login("inviofatture@melchionispa", "invio123")
		mail_variazionior = mail_variazioni.as_string()
		server.sendmail("inviofatture@melchioni.it","f.avino@melchioni.it", mail_variazionior)
		server.quit()
		

################################################################################################
###########################FINE FUNZIONE VERIFICA CAMBI#########################################
################################################################################################











bdi="bdi.txt"
header={'Accept': 'text/csv'}
richiesta='https://tassidicambio.bancaditalia.it/terzevalute-wf-web/rest/v1.0/dailyRates?referenceDate='+oggi+'&currencyIsoCode=EUR'
print (richiesta)
cambi=requests.get(richiesta,headers=header,verify=False) #verify false serve per ignorare gli errori SSL
try:
	file = open(bdi,"w")
except:
	print ("IMPOSSIBILE APRIRE IL FILE "+bdi)
	
cambigg=str(cambi.content)#cambi è una richiesta con risultato 200, cambi.content è il contenuto della richiesta
cambigg=cambigg.replace("\\n","\n") #RIMETTE A POSTO GLI A CAPO
cambigg=cambigg.replace('b"',"")
cambigg=cambigg.replace('"',"")
file.write(cambigg) 


errore_bdi=0
for riga in cambigg.splitlines():#separo lo stringone per righe
	#print (riga)
	try:
		paese,valuta,iso,uic,quotazione,convenzione,Data=riga.split(",")
	except: #se non ci sono le valute esce. NB: per ora se ci sono le valute il file inizia con b", se non ci sono con b'
		print ("VALUTE NON DISPONIBILI SU BANCA D'ITALIA")
		errore_bdi=1
		break
	#if paese=="Paese":
	#	print ("SALTA")
	#else:
	#	file.write(paese)
file.close()

if errore_bdi!=0:
	sys.exit(errore_bdi)
	
verifica_cambi()

if errore_bdi==0:
	try:
		ftp = FTP('10.1.12.2')
		ftp.login("utentes80","utentes80") 
		file = open(bdi,'rb')
	except:
		errore_bdi=20
	try:
		ftp.cwd("ribasece")
	except:
		errore_bdi=20
	try:
		ftp.storbinary("STOR "+bdi,file)
	except:
		errore_bdi=20
	try:
		ftp.rename(bdi,cambi_file)
	except:
		ftp.delete(cambi_file)
		ftp.rename(bdi,cambi_file)
	file.close()


sys.exit(errore_bdi)











