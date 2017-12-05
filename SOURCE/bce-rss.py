import feedparser
import unidecode
import time

bce="bce.txt"
cambi=""

oggi=time.strftime('%Y-%m-%d')#data di oggi

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
for riga in cambi.splitlines(): #separo lo stringone per riga
	if oggi in riga: #prendo solo le righe con la data di oggi
		quotazione,iso,inutile1,inutile2,inutile3,data,inutile4,inutile5,inutile6=riga.split(" ")
		file.write(iso+","+iso+","+iso+","+iso+","+quotazione+","+inutile3+","+data+"\n")

		
		
		
		
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
if count_twd!=1:
	print ("CAMBIO TWD IN ERRORE")		