TASKKILL /IM piskvork.exe
TASKKILL /IM pbrain-uctrandom.exe
pyinstaller.exe uct_random.py pisqpipe.py --name pbrain-uctrandom.exe --onefile
pause