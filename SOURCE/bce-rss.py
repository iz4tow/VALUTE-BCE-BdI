import feedparser
import unidecode
import time
from ftplib import FTP
import sqlite3
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

ftp = FTP('10.1.12.2')
ftp.login("utentes80","utentes80") 
cambi_file="cambigg.csv"

errore_bce=0

bce="bce.txt"
cambi=""

oggi=time.strftime('%Y-%m-%d')#data di oggi







################################################################################################
################################FUNZIONE VERIFICA CAMBI#########################################
################################################################################################

def verifica_cambi():
	file = open(bce,"r")
	###########CONNESSIONE SQLITE
	conn = sqlite3.connect('valute.db')
	curs = conn.cursor()
	###########FINE SQLITE
	curs.execute("SELECT esecuzione,errore FROM applicazione")
	rows=curs.fetchall()
	if len(rows)>0:#VERIFICA TABELLA DEGLI ERRORI
		errore_bce=2
		print ("VERIFICARE LA TABELLA applicazione")
		sys.exit(errore_bce)
	try:#PREPARO LA TABELLA VALUTE PER L'IMPORTAZIONE ELIMINANDO EVENTUALI RESIDUATI
		curs.execute("DELETE FROM VALUTE")
		curs.execute("commit")
	except:
		print ("IMPOSSIBILE ACCEDERE A TABELLA VALUTE")
		errore_bce=99
		sys.exit(errore_bce)
	try:
		curs.execute("INSERT INTO applicazione (esecuzione,errore) VALUES (1,0)")
		curs.execute("commit")
	except:
		print ("IMPOSSIBILE ACCEDERE A TABELLA APPLICAZIONE")
		errore_bce=99
		sys.exit(errore_bce)
	
	for riga in cambi.splitlines():#SCRIVO SUL DATABASE I CAMBI DI OGGI
		paese,valuta,iso,uic,quotazione,convenzione,data=riga.split(",")
		convenzione=convenzione.replace("'","")
		try:#INSERIMENTO VALUTA
			curs.execute("INSERT INTO VALUTE (paese,valuta,iso,uic,quotazione,convenzione,data) VALUES ('"+paese+"','"+valuta+"','"+iso+"','"+uic+"','"+quotazione+"','"+convenzione+"','"+data+"')")
		except:
			print ("ERRORE INSERIMENTO IN TABELLA VALUTE")
			errore_bce=5
			sys.exit(errore_bce)
		try:
			curs.execute("commit")
		except:
			print ("ERRORE INSERIMENTO IN TABELLA VALUTE")
			errore_bce=5
			sys.exit(errore_bce)


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
		errore_bce=9
		sys.exit(errore_bce)
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
		errore_bce=3
		sys.exit(errore_bce)
	try:#SPOSTO I CAMBI NELLA TABELLA VALUTE_IERI PER SUCCESSIVI CONFRONTI
		curs.execute("INSERT INTO VALUTE_IERI SELECT * FROM VALUTE")
	except:
		print("ERRORE COPIA IN VALUTE_IERI")
		errore_bce=4
		sys.exit(errore_bce)
	
	try:#SVUOTO LA TABELLA DI CONTROLLO APPLICAZIONE e la VALUTE 
		curs.execute("DELETE FROM APPLICAZIONE")
		curs.execute("DELETE FROM VALUTE")
	except:
		print("ERRORE IN PULIZIA TABELLA APPLICAZIONE")
		errore_bce=7
		sys.exit(errore_bce)
	
	try:#COMMIT FINALE
		curs.execute("commit")
	except:
		print("ERRORE IN COMMIT FINALE")
		errore_bce=6
		sys.exit(errore_bce)
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




















rss_root = 'https://www.ecb.europa.eu/rss/fxref-'
rss_curr={'usd','jpy','bgn','czk','dkk','eek','gbp','huf','pln','ron','sek','chf','nok','hrk','rub','try','aud','brl','cad','cny','hkd','idr','inr','krw','mxn','myr','nzd','php','sgd','thb','zar'}
rss_html=".html"

for rss_iso in rss_curr:
	rss=rss_root+rss_iso+rss_html
	feed = feedparser.parse(rss)
	for key in feed["entries"]:
		#print (key.keys()) ##DA DECOMMENTARE PER VEDERE GLI INDICI LEGGIBILI IN RSS
		cambi=cambi+unidecode.unidecode(key["title"])+"\n"
	
		
try:
	file = open(bce,"w")
except:
	print ("IMPOSSIBILE APRIRE IL FILE "+bce)

	
file.write("Paese,Valuta,Codice ISO,Codice UIC,Quotazione,Convenzione di cambio, Data di riferimento (CET)\n")
countbce=0
for riga in cambi.splitlines(): #separo lo stringone per riga
	if oggi in riga: #prendo solo le righe con la data di oggi
		quotazione,iso,inutile1,inutile2,inutile3,data,inutile4,inutile5,inutile6=riga.split(" ")
		file.write(iso+","+iso+","+iso+","+iso+","+quotazione+","+inutile3+","+data+"\n")
		countbce=countbce+1

if countbce<20:
	errore_bce=1
	print ("CAMBI BCE NON DISPONIBILI")
		
		
####IL DOLLARO TAIWANESE SI PESCA DA UN ALTRO SITO http://eur.it.fxexchangerate.com/twd.xml
rss_twd="http://eur.it.fxexchangerate.com/twd.xml"
feed_twd = feedparser.parse(rss_twd)
for twd_key in feed_twd["entries"]: 
	#print (twd_key.keys()) ##DA DECOMMENTARE PER VEDERE GLI INDICI LEGGIBILI IN RSS
	twd=unidecode.unidecode(twd_key["description"])+"\n" 
	twd_data=unidecode.unidecode(twd_key["published"])


giorno_settimana,mese,giorno, anno,ora,utc=twd_data.split(" ")
if mese=="Jan":
	mese="01"
if mese=="Feb":
	mese="02"
if mese=="Mar":
	mese="03"
if mese=="Apr":
	mese="04"
if mese=="May":
	mese="05"
if mese=="Jun":
	mese="06"
if mese=="Jul":
	mese="07"
if mese=="Aug":
	mese="08"
if mese=="Sep":
	mese="09"
if mese=="Oct":
	mese="10"
if mese=="Nov":
	mese="11"
if mese=="Dec":
	mese="12"

if int(giorno)<10:
	giorno="0"+giorno

data_twd=anno+"-"+mese+"-"+giorno
count_twd=0
if data_twd==oggi: #CONTROLLO SE ESISTONO CAMBI CON DATA OGGI
	for riga in twd.splitlines():#TAGLIO PER RIGA
		if "1.00 EUR =" in riga:
			valeuro,euro,inutile,quotazione,iso=riga.split(" ")
			iso=iso.replace("<br/>","")
			file.write(iso+","+iso+","+iso+","+iso+","+quotazione+","+inutile+","+data_twd+"\n")
			count_twd=count_twd+1
else:
	print ("CAMBIO TWD NON DISPONIBILE")
	errore_bce=2
if count_twd!=1:
	print ("CAMBIO TWD IN ERRORE")
	errore_bce=3
file.close()	


if errore_bce!=0:
	sys.exit(errore_bce)
verifica_cambi()


if errore_bce==0:
	file = open(bce,'rb')
	ftp.cwd("ribasece")
	ftp.storbinary("STOR bce.txt",file)
	try:
		ftp.rename(bce,cambi_file)
	except:#se esiste già cancello il vecchio
		ftp.delete(cambi_file)
		ftp.rename(bce,cambi_file)
	file.close()
	sys.exit(0)
else:
	sys.exit(errore_bce)