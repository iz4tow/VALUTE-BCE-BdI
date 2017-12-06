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
rem echo CONTENUTO DEL FILE RICOPIATO >> ERRORE.TXT
rem echo **************************************************************** >> ERRORE.TXT
rem echo. >> ERRORE.TXT
rem echo. >> ERRORE.TXT
rem type D:\FTP-da-s80\dati\ribasece\cambigg.csv >> ERRORE.TXT
rem echo. >> ERRORE.TXT
rem echo. >> ERRORE.TXT
rem echo **************************************************************** >> ERRORE.TXT
rem echo **************************************************************** >> ERRORE.TXT
rem echo "FINE DEL FILE RICOPIATO" >> ERRORE.TXT
rem echo **************************************************************** >> ERRORE.TXT
rem echo **************************************************************** >> ERRORE.TXT
echo. >> ERRORE.TXT
echo. >> ERRORE.TXT
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
blat ERRORE.TXT -to listasalamacchine@melchioni.it -subject "CAMBI PIANIFICATI ALLE 17.00 PER SECONDO TENTATIVO"
copy "ERRORE.TXT" "LOG\LOG_%data%_%ora%.TXT"
echo Y | del ERRORE.TXT
exit



:errore_zambia_bdi
echo FILE INCOMPLETO!!! >> ERRORE.TXT
goto errore_bdi



