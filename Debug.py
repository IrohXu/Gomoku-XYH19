LOG_MODE = 'FILE'

# define a file for logging ...
WORK_FOLDER = r"F:\OneDrive\课件\人工智能\final\Gomoku-XYH19\log/"
DEBUG_LOGFILE = 'mylog'
DEBUG_LOGPATH = WORK_FOLDER + DEBUG_LOGFILE
# ...and clear it initially
with open(DEBUG_LOGPATH,"w") as f:
	pass
# define a function for writing messages to the file
def logDebug(msg):
    if LOG_MODE == 'FILE':
        with open(DEBUG_LOGPATH,"a") as f:
            f.write(str(msg)+"\n")
            f.flush()
    else:
        print(msg)

# define a function to get exception traceback
def logTraceBack():
    import traceback
    if LOG_MODE == 'FILE':
        with open(DEBUG_LOGPATH,"a") as f:
            traceback.print_exc(file=f)
            f.flush()
    else:
        traceback.print_exc()
    raise Exception('fuck')