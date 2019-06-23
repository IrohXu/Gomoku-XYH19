TASKKILL /IM piskvork.exe
TASKKILL /IM pbrain-mcts.exe
pyinstaller.exe mcts_factor.py pisqpipe.py --name pbrain-mcts_factor.exe --onefile
pause