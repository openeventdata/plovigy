"""
plovigy-PITF-annotate.py

Radical simplification of plovigy-PITF-DEDI.py to work with the PITF PLOVER/NGEC human annotations.

TO RUN PROGRAM:

python3 plovigy-PITF-annotate.py <filename> <coder>

where the optional <filename> is the file to read with a hard-coded default; <coder> is optional coder initials

KEYS

1/a/<space>   accept

3/0/x/        reject

q             quit 

PROGRAMMING NOTES:

1. The file FILEREC_NAME keeps track of the location in the file.

2. Output file names are coder- and time-stamped

3. Input is not case-sensitive
 

SYSTEM REQUIREMENTS
This program has been successfully run under Mac OS 10.13.2 and Ubuntu 16.04; it is standard Python 3.5 so it should also run in Windows. 

PROVENANCE:
Programmer: Philip A. Schrodt
            Parus Analytics
            Charlottesville, VA, 22901 U.S.A.
            http://eventdata.parusanalytics.com

Copyright (c) 2018	Philip A. Schrodt.	All rights reserved.

plovigy-mark.py was initially developed as part of research funded by a U.S. National Science Foundation "Resource 
Implementations for Data Intensive Research in the Social Behavioral and Economic Sciences (RIDIR)" 
project: Modernizing Political Event Data for Big Data Social Science Research (Award 1539302; 
PI: Patrick Brandt, University of Texas at Dallas)

This code is covered under the MIT license: http://opensource.org/licenses/MIT

Report bugs to: schrodt735@gmail.com

REVISION HISTORY:
15-Dec-17:	Initial version
04-Jan-18:	Default switching option
23-Jan-18:	Buffered output; comment option
14-May-19:  Modified for PITF-PROT
24-Jul-19:  Modified to use curses
04-Apr-20:  Added output buffer
17-Aug-21:  Radically modified to plovigy-PITF-annotate.py

=========================================================================================================
"""
from collections import deque
import textwrap
import datetime
import curses
import json
import sys
import os

dayOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

FILEREC_NAME = "plovigy.annotate.filerecs.txt"

MAX_QUEUE_SIZE = 8

fieldoptions = "RT"
keyoptions = fieldoptions + "SDA1 X30=Q+"

# ======= Routines from utilDEDI ==========    

def timestamp():
    return '-' + datetime.datetime.now().strftime("%Y%m%d")[2:] + "-" + datetime.datetime.now().strftime("%H%M%S")[:-2] + ".jsonl"

def set_nskip(filename, filerec_name):
    """ common routine for skipping previously coded records """
    nskip = -1
    havefile = False
    if os.path.exists(filerec_name):
        with open(filerec_name,'r') as frec:
            line = frec.readline() 
            while line:  # go through the entire file to get the last entry
                if filename in line:
                    nskip = int(line.split()[1])
                    havefile = True
                line = frec.readline()
    else:
        print("The record file", filerec_name, "is missing; please find or create it")
        exit()

    if nskip < 0 and havefile:
        print("All records in", filename, "have been coded")
        answ = input("Do you want to restart at the beginning of the file? (Y/N) -->")
        if answ in ['Y','y']:
            nskip = -1
        else:
            print("Please select another file: exiting")
            exit()    

    if nskip == -1:
        print("Starting at the beginning of", filename)
    else:
        print("Skipping first", nskip,"records in",filename)            

    answ = input("Press return to start...")

    return nskip

def read_file(filename):
    """ returns next record in a line-delimited JSON file """
    jstr = ""
    for line in open(filename, "r"):
        if line.startswith("}"):
#            print(jstr)   # debug: uncomment to find badly formed cases, or put this into a try/except
            adict = json.loads(jstr + "}")
            yield adict
            jstr = ""
        else:
            if "\t" in line:
                line = line.replace("\t", "\\t")
            jstr += line[:-1].strip()
            
# =======================================================

def write_header():
    record['coder'] = coder
    record['evalTime'] = timestamp()
    record['nskip'] = nskip
    record['sourceFile'] = filename
    fout.write(json.dumps(record, indent=2, sort_keys=True ) + "\n") 

if len(sys.argv) > 1:
    filename = sys.argv[1]
    infix = filename[filename.index("ases-")+5:-6] + "-"
    """print(infix)
    exit()"""
else:  
    print("File name is required")
    exit()
    
if len(sys.argv) >= 3:
    coder = sys.argv[2]
else:  
    coder = "PAS"    

def next_key(win):    
    key = 31
    win.addstr(SUBW_HGT-2, 2, "Enter option: ")  # maybe give an error here for invalid entry?
    while chr(key).upper() not in keyoptions: 
        if key != 31:
            win.addstr(SUBW_HGT-2, 2, "Invalid option '" + chr(key) + "', try again: ")  # maybe give an error here for invalid entry?
        key = win.getch()
        win.clrtobot()
        win.border()
    win.refresh()
    return key, chr(key).upper()


SUBW_HGT = 16
SUBW_WID = 148
INIT_Y = 2 
INIT_X = 4
EVNT_X = 64

def main(stdscr):
    global nacc, nrej, nskip, nauto, currec, keych, record, currmatch

    nauto = 0
    recque = deque()
    currec = 0
    keych = ""
    currmatch = ""
    hasshift = False

    ka = -1
    while True:
        if ka < nskip:
            record = next(reader)
            ka += 1
            if "include" in record:
                write_header()
            continue
#        fout.write("Mk0" + " " + str(ka) + "\n")
        if (currec < len(recque) - 1) or (currec == len(recque) - 1 and not recque[-1]["status"]):
            record = recque[currec]
        elif len(recque) <= MAX_QUEUE_SIZE or recque[-1]["status"]:
            while True:
#                    fout.write("Mk-1" + " " + str(ka) + "\n")
                try:
                    record = next(reader)
                except StopIteration:
                    print("All records have been coded")
                    nskip = -1
                    while len(recque) > 0:
                        rec = recque.popleft()
                        if rec["status"] == "accept":
                            fout.write(json.dumps(rec, indent=2, sort_keys=True ) + "\n")
                    return            
                ka += 1
                if "include" in record:
                    write_header()
                    continue           
                if len(recque) == MAX_QUEUE_SIZE:
                    rec = recque.popleft()
                    if rec["status"] == "accept":
                        fout.write(json.dumps(rec, indent=2, sort_keys=True ) + "\n")            
                record["status"] = None
                recque.append(record)
                currec = len(recque) - 1
                break                    
            
        modwin = curses.newwin(SUBW_HGT ,SUBW_WID, 2, 2)
        modwin.border()         
        
        if currec == len(recque)- 1:
            modwin.addstr(INIT_Y, INIT_X, str(ka) + '  ' + record['locationName']  + ": " + record['pubDate'][:10] )
        else:
            modwin.addstr(INIT_Y, INIT_X, "Queue loc " + str(currec - MAX_QUEUE_SIZE + 1) + '  '  + record['locationName']  + ": " + record['pubDate'][:10])
#        modwin.addstr(INIT_Y, SUBW_WID - 32, "Queue loc:" + str(currec))
        modwin.addstr(INIT_Y+2, INIT_X,record['title'])
        y_curs = INIT_Y + 4
        x_curs = INIT_X
        for ln in textwrap.wrap(record['description'],96):
            modwin.addstr(y_curs, x_curs, ln)
            y_curs += 1
            if y_curs >= SUBW_HGT-2:
                break
#        modwin.addstr(SUBW_HGT-3, x_curs+16, "currec:{:3d}  ka:{:3d}  ka:{:3d}".format(currec, ka, ka))
        modwin.addstr(SUBW_HGT-2, x_curs+16, "accept:{:3d}  reject:{:3d}  total:{:3d}".format(nacc, nrej, nacc + nrej))
        modwin.addstr(SUBW_HGT-2, x_curs+52, "auto:{:3d}".format(nauto))
        modwin.addstr(SUBW_HGT-2, SUBW_WID - 78, "Options:  A/1/ /accept  X/0/3/=/reject  B/2 backdate  F/5 adddate  Q/quit") 
        
            
        modwin.refresh()
        firstback = True
        key, keych = next_key(modwin)

        while keych in fieldoptions: # modifications without writing 
            if "R" == keych or "T"  == keych:  # save ids of records to reconsider
                if "R" == keych:  # move backwards in buffer
                    if currec > 0:
                        currec -= 1
                else: # move forward in buffer
                    if currec < len(recque) - 1:
                        currec += 1
                break
                
            key, keych = next_key(modwin)
#            fout.write("key-2: " + keych + "\n")
     
        if "A" == keych or "1"  == keych  or " "  == keych:
            nacc += 1
            record["status"] = "accept"
            currec += 1

        elif "X" == keych or "3"  == keych  or "0"  == keych or "=" == keych:
            nrej += 1
            record['status'] = "reject"
            currec += 1
 
        elif keych == "Q":
            nskip = ka - 1
            while len(recque) > 1:
                rec = recque.popleft()
                if rec["status"] == "accept":
                    fout.write(json.dumps(rec, indent=2, sort_keys=True ) + "\n")            
            return


nskip = set_nskip(filename, FILEREC_NAME)
#nskip = -1  ### DEBUG

nacc, nrej = 0,0  # counters for two annotations
timestr = timestamp()
fout = open("annotate-" + infix + coder + timestr,'w')

reader = read_file(filename)
curses.wrapper(main)

fout.close()

with open(FILEREC_NAME,'a') as frec:
    frec.write("{:s} {:d} {:s}".format(filename,nskip, timestr)) 
    frec.write( "   accept:{:3d}  reject:{:3d}  total:{:3d}\n".format(nacc, nrej, nacc + nrej))

print("Finished")
