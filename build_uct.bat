TASKKILL /IM piskvork.exe
TASKKILL /IM pbrain-uct.exe
pyinstaller.exe uct.py pisqpipe.py --name pbrain-uct.exe --onefile
pause