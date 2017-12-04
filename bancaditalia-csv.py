import requests
import jaydebeapi
import jpype
import time

#CONNESSIONE A DB2
jar = 'db2jcc4.jar' # location of the jdbc driver jar
args='-Djava.class.path=%s' % jar
jvm = jpype.getDefaultJVMPath()
jpype.startJVM(jvm, args)
conn=jaydebeapi.connect('com.ibm.db2.jcc.DB2Driver', 'jdbc:db2://10.1.12.69:50000/s69mk0se',['db2inst1','db2inst1']) #connessione al db2
curs=conn.cursor()
#########FINE DB2

oggi=time.strftime('%Y-%m-%d')#data di oggi


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


file = open("result.txt","w")
for riga in cambigg.splitlines():#separo lo stringone per righe
	#print (riga)
	try:
		paese,valuta,iso,uic,quotazione,convenzione,Data=riga.split(",")
	except: #se non ci sono le valute esce. NB: per ora se ci sono le valute il file inizia con b", se non ci sono con b'
		print ("VALUTE NON DISPONIBILI SU BANCA D'ITALIA")
		errore_bdi=1
		break
	if paese=="Paese":
		print ("SALTA")
	else:
		file.write(paese)
		
	