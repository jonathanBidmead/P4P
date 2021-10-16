import os
import platform
import time
import pickle as p

def modification_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getmtime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime
            
modifieddate=time.ctime(modification_date("build/Kereru.bin"))
print("Current modification date: "+ time.ctime(modification_date("build/Kereru.bin")))

#lastmodification="foobar"
#>>> p.dump(mystr,open('/tmp/t.txt','wb'))
logfile="lastdate.txt"
lastdate="0"
if os.path.isfile(logfile):
    lastdate=p.load(open('lastdate.txt','rb'))
print("Logged modification date: "+lastdate)
#'foobar'

if lastdate != modifieddate:
    print("Bin changed. About to flash")
    os.system("idf.py flash")
else:
    print("Bin not changed. No need to flash.")
#print(lastdate)
p.dump(modifieddate,open('lastdate.txt','wb'))