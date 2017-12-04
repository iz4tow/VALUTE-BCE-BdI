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
		cambi=cambi+unidecode.unidecode(key["title"])+"\n"
#print(cambi)
	
		
try:
	file = open(bce,"w")
except:
	print ("IMPOSSIBILE APRIRE IL FILE "+bce)

	
	
for riga in cambi.splitlines(): #separo lo stringone per riga
	if oggi in riga: #prendo solo le righe con la data di oggi
		file.write(riga+"\n") 