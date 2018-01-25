@echo off
SchTasks /Delete /TN "VALUTE_TEMP" /f
set data=%date:~6,4%%date:~3,2%%date:~0,2%
set ora=%time:~0,2%%time:~3,2%%time:~6,2%
echo %data% %ora% > ERRORE.TXT
echo INIZIO DOWNLOAD VALUTE DA BANCA D'ITALIA >> ERRORE.TXT
start /WAIT bdi-csv.exe >> ERRORE.TXT
if %ERRORLEVEL% NEQ 0 goto :errore_bdi
set data=%date:~6,4%%date:~3,2%%date:~0,2%
set ora=%time:~0,2%%time:~3,2%%time:~6,2%
echo. >> ERRORE.TXT
echo. >> ERRORE.TXT
echo **************************************************************** >> ERRORE.TXT
echo **************************************************************** >> ERRORE.TXT
echo **************************************************************** >> ERRORE.TXT
echo **************************************************************** >> ERRORE.TXT
echo CONTENUTO DEL FILE >> ERRORE.TXT
echo **************************************************************** >> ERRORE.TXT
echo. >> ERRORE.TXT
echo. >> ERRORE.TXT
type bdi.txt >> ERRORE.TXT
echo. >> ERRORE.TXT
echo. >> ERRORE.TXT
echo **************************************************************** >> ERRORE.TXT
echo **************************************************************** >> ERRORE.TXT
echo "FINE DEL FILE" >> ERRORE.TXT
echo **************************************************************** >> ERRORE.TXT
echo **************************************************************** >> ERRORE.TXT
echo. >> ERRORE.TXT
echo. >> ERRORE.TXT
echo **************************************************************** >> ERRORE.TXT
echo **************************************************************** >> ERRORE.TXT
echo CONTENUTO DEL FILE RICOPIATO >> ERRORE.TXT
echo **************************************************************** >> ERRORE.TXT
echo. >> ERRORE.TXT
echo. >> ERRORE.TXT
type D:\FTP-da-s80\dati\ribasece\cambigg.csv >> ERRORE.TXT
echo. >> ERRORE.TXT
echo. >> ERRORE.TXT
echo **************************************************************** >> ERRORE.TXT
echo **************************************************************** >> ERRORE.TXT
echo "FINE DEL FILE RICOPIATO" >> ERRORE.TXT
echo **************************************************************** >> ERRORE.TXT
echo **************************************************************** >> ERRORE.TXT
echo. >> ERRORE.TXT
echo. >> ERRORE.TXT
echo COMPARAZIONE DEI FILES >> ERRORE.TXT
fc bdi.txt D:\FTP-da-s80\dati\ribasece\cambigg.csv
if %ERRORLEVEL% NEQ 0 goto :errore_diversi
echo "CONTROLLO ZAMBIA, UNGHERIA, TAIWAN" >> ERRORE.TXT
findstr /m "ZAMBIA" bdi.txt
if %ERRORLEVEL% NEQ 0 goto :errore_zambia_bdi
findstr /m "UNGHERIA" bdi.txt
if %ERRORLEVEL% NEQ 0 goto :errore_zambia_bdi
findstr /m "TAIWAN" bdi.txt
if %ERRORLEVEL% NEQ 0 goto :errore_zambia_bdi
echo "NESSUNA DISCORDANZA RILEVATA" >> ERRORE.TXT
copy "ERRORE.TXT" "LOG\LOG_%data%_%ora%.TXT"
echo Y | del ERRORE.TXT
exit




:errore_bdi
SchTasks /Create /TN "VALUTE_TEMP" /XML VALUTE.xml >> ERRORE.TXT
blat -install owa.melchioni.it cambi@melchioni.it
blat ERRORE.TXT -to listasalamacchine@melchioni.it -subject "CAMBI PIANIFICATI ALLE 19.00 PER SECONDO TENTATIVO"
copy "ERRORE.TXT" "LOG\LOG_%data%_%ora%.TXT"
echo Y | del ERRORE.TXT
exit



:errore_zambia_bdi
echo FILE INCOMPLETO!!! >> ERRORE.TXT
goto errore_bdi

:errore_diversi
cp bdi.txt D:\FTP-da-s80\dati\ribasece\cambigg.csv
blat -install owa.melchioni.it cambi@melchioni.it
blat ERRORE.TXT -to listasalamacchine@melchioni.it -subject "CONTROLLARE FILE IN ribasece PER ULTERIORE VERIFICA!"
exit


