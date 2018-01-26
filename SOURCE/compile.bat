rem C:\Program Files\Python36\Scripts\pyinstaller.exe --hidden-import jaydebeapi,jpype,pyodbc,time,decimal  -F SYBASEIQ-DB2-NOGUI.py
"C:\Program Files\Python36\Scripts\pyinstaller.exe" --hidden-import time,feedparser,unidecode,FTP,sys,sqlite3,smtplib,email  -F bce-rss.py
"C:\Program Files\Python36\Scripts\pyinstaller.exe" --hidden-import time,requests,FTP,sys,sqlite3,smtplib,email  -F bdi-csv.py
"C:\Program Files\Python36\Scripts\pyinstaller.exe" --hidden-import requests,time,feedparser,unidecode,FTP,appJar --noconsole -F VALUTE.py
"C:\Program Files\Python36\Scripts\pyinstaller.exe" --hidden-import requests,time,feedparser,unidecode,FTP,datetime,appJar,sqlite3 --noconsole -F VALUTE-DATA.py

pause > nul
