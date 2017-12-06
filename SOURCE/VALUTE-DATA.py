# import the library
import requests
#import jaydebeapi
#import jpype
import time
import feedparser
import unidecode
#import os 
from ftplib import FTP
import datetime
from appJar import gui

ftp = FTP('10.1.12.2')
ftp.login("utentes80","utentes80") 
cambi_file="cambigg.csv"

#CONNESSIONE A DB2
#jar = 'db2jcc4.jar' # location of the jdbc driver jar
#args='-Djava.class.path=%s' % jar
#jvm = jpype.getDefaultJVMPath()
#jpype.startJVM(jvm, args)
#conn=jaydebeapi.connect('com.ibm.db2.jcc.DB2Driver', 'jdbc:db2://10.1.12.69:50000/s69mk0se',['db2inst1','db2inst1']) #connessione al db2
#curs=conn.cursor()
#########FINE DB2


########################################################################################################################################################################################
#######CAMBI BANCA D'ITALIA#############################################################################################################################################################
########################################################################################################################################################################################
def BdI():
	data=app.getEntry("data")
	if data == "":#se vuoto metto la data di oggi
		data=time.strftime('%d-%m-%Y')#data di oggi
	try:#verifica formato
		giorno,mese,anno=data.split("-")
	except ValueError:
		app.showLabel("dispBdI") #Errore cambi
		app.setLabelFg("dispBdI", "red")
		app.setLabel("dispBdI","Formato data non valido, formato valido GG-MM-AAAA")
		return 1
	if len(giorno)<2:
		giorno="0"+giorno
	if len(mese) <2:
		mese="0"+mese
	
	oggi=anno+"-"+mese+"-"+giorno
	#isdigit() restituisce vero se l'array o variabile è solo numerica, se contiene altro falso
	try: #verifica validita data
		newDate = datetime.datetime(int(anno), int(mese), int(giorno))
	except ValueError:
		app.showLabel("dispBdI") #Errore cambi
		app.setLabelFg("dispBdI", "red")
		app.setLabel("dispBdI","Formato data non valido, formato valido GG-MM-AAAA")
		return 1
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
	file.close()
	
	errore_bdi=0
	for riga in cambigg.splitlines():#separo lo stringone per righe
		#print (riga)
		try:
			paese,valuta,iso,uic,quotazione,convenzione,Data=riga.split(",")
		except: #se non ci sono le valute esce. NB: per ora se ci sono le valute il file inizia con b", se non ci sono con b'
			print ("VALUTE NON DISPONIBILI SU BANCA D'ITALIA")
			app.showLabel("dispBdI") #Errore cambi
			app.setLabelFg("dispBdI", "red")
			app.setLabel("dispBdI","Cambi non disponibili su Banca d'Italia")
			errore_bdi=1
			break
	########FINE CAMBI BdI
	if errore_bdi==0:
		file = open(bdi,'rb')
		ftp.cwd("ribasece")
		ftp.storbinary("STOR "+bdi,file)
		try:
			ftp.rename(bdi,cambi_file)
		except:#se esiste già cancello il vecchio
			ftp.delete(cambi_file)
			ftp.rename(bdi,cambi_file)
		file.close()
	app.showButton("Verifica disponibilità")
	app.showButton("BdI")
	app.showButton("BCE")
########################################################################################################################################################################################	
########FINE BANCA D'ITALIA################################################################################################################################################################################	
########################################################################################################################################################################################	


########################################################################################################################################################################################	
#######CAMBI BCE########################################################################################################################################################################
########################################################################################################################################################################################
def BCE():
	data=app.getEntry("data")
	if data == "":#se vuoto metto la data di oggi
		data=time.strftime('%d-%m-%Y')#data di oggi
	try:#verifica formato
		giorno,mese,anno=data.split("-")
	except ValueError:
		app.showLabel("dispBdI") #Errore cambi
		app.setLabelFg("dispBdI", "red")
		app.setLabel("dispBdI","Formato data non valido, formato valido GG-MM-AAAA")
		return 1
	if len(giorno)<2:
		giorno="0"+giorno
	if len(mese) <2:
		mese="0"+mese
	
	oggi=anno+"-"+mese+"-"+giorno
	#isdigit() restituisce vero se l'array o variabile è solo numerica, se contiene altro falso
	try: #verifica validita data
		newDate = datetime.datetime(int(anno), int(mese), int(giorno))
	except ValueError:
		app.showLabel("dispBdI") #Errore cambi
		app.setLabelFg("dispBdI", "red")
		app.setLabel("dispBdI","Formato data non valido, formato valido GG-MM-AAAA")
		return 1
	bce="bce.txt"
	cambi=""
	
	rss_root = 'https://www.ecb.europa.eu/rss/fxref-'
	rss_curr={'usd','jpy','bgn','czk','dkk','eek','gbp','huf','pln','ron','sek','chf','nok','hrk','rub','try','aud','brl','cad','cny','hkd','idr','inr','krw','mxn','myr','nzd','php','sgd','thb','zar'}
	rss_html=".html"
	
	for rss_iso in rss_curr:
		rss=rss_root+rss_iso+rss_html
		feed = feedparser.parse(rss)
		for key in feed["entries"]: 
			cambi=cambi+unidecode.unidecode(key["title"])+"\n"
	#print(cambi)
		
			
	try:
		file = open(bce,"w")
	except:
		print ("IMPOSSIBILE APRIRE IL FILE "+bce)
	
		
	file.write("Paese,Valuta,Codice ISO,Codice UIC,Quotazione,Convenzione di cambio, Data di riferimento (CET)\n")
	countbce=0
	errore_bce=0
	for riga in cambi.splitlines(): #separo lo stringone per riga
		if oggi in riga: #prendo solo le righe con la data di oggi
			quotazione,iso,inutile1,inutile2,inutile3,data,inutile4,inutile5,inutile6=riga.split(" ")
			file.write(iso+","+iso+","+iso+","+iso+","+quotazione+","+inutile3+","+data+"\n")
			countbce=countbce+1
	if countbce<20:
		errore_bce=1
		app.showLabel("dispBCE") #Errore cambi
		app.setLabelFg("dispBCE", "red")
		app.setLabel("dispBCE","Cambi non disponibili su Banca Centrale Europea")
	########FINE CAMBI BCE
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
		app.showLabel("dispTWD") #Errore cambi
		app.setLabelFg("dispTWD", "red")
		app.setLabel("dispTWD","Cambio TWD non disponibile")
		errore_bce=2
	if count_twd!=1:
		app.showLabel("dispTWD") #Errore cambi
		app.setLabelFg("dispTWD", "red")
		app.setLabel("dispTWD","Cambio TWD in ERRORE - CONTATTARE FRANCO!!!!")	
		errore_bce=3
	file.close()
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
	app.showButton("Verifica disponibilità")
	app.showButton("BdI")
	app.showButton("BCE")
########################################################################################################################################################################################
#####FINE BCE###################################################################################################################################################################################
########################################################################################################################################################################################


########PROCEDURA SYBASE -> DB2
def disp():
	data=app.getEntry("data")
	if data == "":#se vuoto metto la data di oggi
		data=time.strftime('%d-%m-%Y')#data di oggi
	try:#verifica formato
		giorno,mese,anno=data.split("-")
	except ValueError:
		app.showLabel("dispBdI") #Errore cambi
		app.setLabelFg("dispBdI", "red")
		app.setLabel("dispBdI","Formato data non valido, formato valido GG-MM-AAAA")
		return 1
	if len(giorno)<2:
		giorno="0"+giorno
	if len(mese) <2:
		mese="0"+mese
	
	oggi=anno+"-"+mese+"-"+giorno
	#isdigit() restituisce vero se l'array o variabile è solo numerica, se contiene altro falso
	try: #verifica validita data
		newDate = datetime.datetime(int(anno), int(mese), int(giorno))
	except ValueError:
		app.showLabel("dispBdI") #Errore cambi
		app.setLabelFg("dispBdI", "red")
		app.setLabel("dispBdI","Formato data non valido, formato valido GG-MM-AAAA")
		return 1
	###################DISPONIBILITA BdI#######################################################
	header={'Accept': 'text/csv'}
	richiesta='https://tassidicambio.bancaditalia.it/terzevalute-wf-web/rest/v1.0/dailyRates?referenceDate='+oggi+'&currencyIsoCode=EUR'
	cambi=requests.get(richiesta,headers=header,verify=False) #verify false serve per ignorare gli errori SSL
		
	cambigg=str(cambi.content)#cambi è una richiesta con risultato 200, cambi.content è il contenuto della richiesta
	cambigg=cambigg.replace("\\n","\n") #RIMETTE A POSTO GLI A CAPO
	cambigg=cambigg.replace('b"',"")
	cambigg=cambigg.replace('"',"")

	for riga in cambigg.splitlines():#separo lo stringone per righe
		try:
			paese,valuta,iso,uic,quotazione,convenzione,Data=riga.split(",")
		except: #se non ci sono le valute esce. NB: per ora se ci sono le valute il file inizia con b", se non ci sono con b'
			print ("VALUTE NON DISPONIBILI SU BANCA D'ITALIA")
			app.showLabel("dispBdI") #Errore cambi
			app.setLabelFg("dispBdI", "red")
			app.setLabel("dispBdI","Cambi non disponibili su Banca d'Italia")
			break
		app.showLabel("dispBdI") #Errore cambi
		app.setLabelFg("dispBdI", "green")
		app.setLabel("dispBdI","Cambi disponibili su Banca d'Italia")
################FINE DISPONIBILITA BdI#######################################################

################DISPONIBILITA BCE########################################################################################################################################################################
	cambi=""
	rss_root = 'https://www.ecb.europa.eu/rss/fxref-'
	rss_curr={'usd','jpy','bgn','czk','dkk','eek','gbp','huf','pln','ron','sek','chf','nok','hrk','rub','try','aud','brl','cad','cny','hkd','idr','inr','krw','mxn','myr','nzd','php','sgd','thb','zar'}
	rss_html=".html"
	for rss_iso in rss_curr:
		rss=rss_root+rss_iso+rss_html
		feed = feedparser.parse(rss)
		for key in feed["entries"]: 
			cambi=cambi+unidecode.unidecode(key["title"])+"\n"

	countbce=0
	for riga in cambi.splitlines(): #separo lo stringone per riga
		if oggi in riga: #prendo solo le righe con la data di oggi
			quotazione,iso,inutile1,inutile2,inutile3,data,inutile4,inutile5,inutile6=riga.split(" ")
			countbce=countbce+1
	if countbce<20:
		app.showLabel("dispBCE") #Errore cambi
		app.setLabelFg("dispBCE", "red")
		app.setLabel("dispBCE","Cambi non disponibili su Banca Centrale Europea")
	else:
		app.showLabel("dispBCE") #Errore cambi
		app.setLabelFg("dispBCE", "green")
		app.setLabel("dispBCE","Cambi disponibili su Banca Centrale Europea")
		
	########FINE CAMBI BCE
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
				count_twd=count_twd+1
	else:
		app.showLabel("dispTWD") #Errore cambi
		app.setLabelFg("dispTWD", "red")
		app.setLabel("dispTWD","Cambio TWD non disponibile")
	if count_twd!=1:
		app.showLabel("dispTWD") #Errore cambi
		app.setLabelFg("dispTWD", "red")
		app.setLabel("dispTWD","Cambio TWD non presente in BCE!!!!")		

	
	app.showButton("Verifica disponibilità")
	app.showButton("BdI")
	app.showButton("BCE")
	


def press(button):
	if button == "Verifica disponibilità":
		disp()
	if button == "BdI":
		BdI()
	if button == "BCE":
		BCE()
		






app = gui("IMPORTAZIONE CAMBI IN EURO", "600x300")
app.setBg("yellow")
app.setFont(18)
app.addLabel("title", "\nIMPORTAZIONE CAMBI IN EURO\n") #NOMELABEL, CONTENUTO
app.setLabelBg("title", "blue")#NOMELABEL, COLORE SFONDO
app.setLabelFg("title", "red") #NOME LABEL, COLORE CARATTERE

oggi=time.strftime('%d-%m-%Y')
app.addEntry("data") #NOMELABEL, CONTENUTO
app.setEntryDefault("data",oggi)
app.addLabel("dispBdI"," ") #NOMELABEL, CONTENUTO
app.hideLabel("dispBdI") #nascondo avviso1 di comodo per avvisi
app.addLabel("dispBCE"," ") #NOMELABEL, CONTENUTO
app.hideLabel("dispBCE") #nascondo avviso1 di comodo per avvisi
app.addLabel("dispTWD"," ") #NOMELABEL, CONTENUTO
app.hideLabel("dispTWD") #nascondo avviso1 di comodo per avvisi


app.addButtons(["Verifica disponibilità","BdI","BCE"], press)

app.go()