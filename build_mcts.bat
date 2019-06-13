TASKKILL /IM piskvork.exe
TASKKILL /IM pbrain-mcts.exe
pyinstaller.exe mcts.py pisqpipe.py --name pbrain-mcts.exe --onefile
pause