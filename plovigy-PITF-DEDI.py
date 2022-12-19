"""
plovigy-PITF-DEDI.py

A subset of plovigy-mark.py which uses the PITF-PROT jsonl format and just does simple accept/reject classification without
any other options; also does quite a bit of autocoding. 

TO RUN PROGRAM:

python3 plovigy-PITF-Protest.py <filename> <coder>

where the optional <filename> is the file to read with a hard-coded default; <coder> is optional coder initials

KEYS

1/a/<space>   accept

3/0/x/        reject

2/B           move date back one day

5/F           move date back one day

r or t        write previous/previous - 1 ID to filerecs on exit

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

=========================================================================================================
"""
from collections import deque
import utilDEDI
import textwrap
import datetime
import curses
import json
import sys
import os

dayOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

FILEREC_NAME = "plovigy.filerecs.txt"

MAX_QUEUE_SIZE = 8

fieldoptions = "RT2B5F"
keyoptions = fieldoptions + "SDA1 X30=Q+"

if len(sys.argv) > 1:
    filename = sys.argv[1]
    infix = filename[filename.index("rds-")+4:-6] + "-"
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

    def check_autodemand(txtstr, doreject = False):
        global currmatch
#        fout.write("CA-1"  + " " + str(doreject) + "\n")
        if hasshift:
            return False
        lowtxt = txtstr.lower()
        for wrd, val in auto.items():
#            fout.write("CA-2" + wrd + " " + str(val) + "\n")
            for tu in val:
                if tu[utilDEDI.AUTOCODE] == "ALL" or tu[utilDEDI.AUTOCODE] == record['ccode']:
                    tupmatch = tu
                    break
            else:  # for loop else
                continue
            if doreject and not tupmatch[utilDEDI.AUTOREJT]:
                continue
                """fout.write("Mk1-Checking "  + wrd + ": " + str(tupmatch) + "\n")
                if tupmatch[utilDEDI.AUTOCASE]: 
                        if utilDEDI.check_autopat(wrd, txtstr):
                            return True
                    else:
                        if utilDEDI.check_autopat(wrd, lowtxt):
                            return True
                    if len(tupmatch) == 2 or not tupmatch[3]:
                        if wrd in lowtxt:
#                            fout.write("rejecting " + wrd + " " + str(tupmatch)  + "\n")
                            return True
                    elif wrd in txtstr:
#                        fout.write("rejecting w/case " + wrd + " " + str(tupmatch)  + "\n")
                        return True"""                
            """fout.write("Check '" + wrd + "' against '" + txtstr[:64] +"' : ")
            fout.write(" (" + str((txtstr.find(wrd) >= 0)) + ") ")
            fout.write(" (-" + str((wrd in txtstr)) + "-) ")"""
            if tupmatch[utilDEDI.AUTOCASE]:
                if utilDEDI.check_autopat(wrd, txtstr):
                    currmatch = wrd
                    return True
            elif utilDEDI.check_autopat(wrd, lowtxt):
                currmatch = wrd
                return True
            #fout.write("False\n")
        return False
        

    def process_auto(cmtstr, isrej = False):
        global nauto, currec, nacc, nrej, keych, record 
        if isrej:
            nrej += 1
            record["status"] = "reject"
        else:
            nacc += 1
            record["status"] = "accept"        
        record["comment"] = "auto-" + record["status"] + ": " + cmtstr + " '" + currmatch + "'"          
        fout.write(json.dumps(record, indent=2, sort_keys=True ) + "\n")
        nauto += 1
        currec += 1
        keych = "-"


    autohead = ""
    autoid = ""
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
            continue
#        fout.write("Mk0" + " " + str(ka) + "\n")
            
        if "S" != keych and "D" != keych:
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
                            fout.write(json.dumps(recque.popleft(), indent=2, sort_keys=True ) + "\n")
                        return            
                    ka += 1
                    if ("esterday" in record['text'] or "omorrow" in record['text'] or "last night" in record['text'] or 
                        "day after" in record['text'] or
                        "esterday" in record['headline'] or "omorrow" in record['headline']):
                        hasshift = True
                    else: 
                        hasshift = False
#                    fout.write("Mk2" + " " + str(ka) + "\n")
                    if record['headline'].isupper():
                        process_auto("all-caps headline", True)
                    elif record['ccode'] == "---":  # 21.04.22: Deals with the NULLs in 07/08-2015
                        process_auto("--- NULL ccode", True)
                    elif record['ccode'] == "USA":  # 21.02.04: should be redundant now; moved this filter into ICEWS-to-jsonl-DEDI.py
                        process_auto("USA", True)
                    elif check_autodemand(record['text'], True) or check_autodemand(record['headline'], True):
                        process_auto("", True)
                    elif check_autodemand(record['text']) or check_autodemand(record['headline']):
                        process_auto("")
                    elif currec == len(recque) and autohead == record['headline']:
                        process_auto("headline match " + autoid)
                    else:
                        if len(recque) == MAX_QUEUE_SIZE:
                            fout.write(json.dumps(recque.popleft(), indent=2, sort_keys=True ) + "\n")            
                        record["status"] = None
                        recque.append(record)
                        currec = len(recque) - 1
                        break                    

        """# code for selecting single day to coder
        if record['date'] != "2020-03-31":
            continue"""

        modwin = curses.newwin(SUBW_HGT ,SUBW_WID, 2, 2)
        modwin.border()         
        
        thedate = datetime.datetime(int(record['date'][:4]), int(record['date'][5:7]), int(record['date'][-2:]))
        if currec == len(recque)- 1:
            modwin.addstr(INIT_Y, INIT_X, str(ka) + '  ' + record['country']  + ": " + record['date'] + " (" + dayOfWeek[thedate.weekday()] + ")")
        else:
            modwin.addstr(INIT_Y, INIT_X, "Queue loc " + str(currec - MAX_QUEUE_SIZE + 1) + '  ' + record['country']  + ": " + record['date'] + " (" + dayOfWeek[thedate.weekday()] + ")")
        if ("restrictions" in record["eventText"] or "administrative" in record["eventText"] or
            "hreaten" in record["eventText"] or "urfew" in record["eventText"] or
            "tactics" in record["eventText"] or "Ban" in record["eventText"] or 
            "mpose blockade" in record["eventText"] or "artial law" in record["eventText"]):
            modwin.addstr(INIT_Y, INIT_X + EVNT_X, record["eventText"],curses.A_STANDOUT)
        else:
            modwin.addstr(INIT_Y, INIT_X + EVNT_X, record["eventText"])        
#        modwin.addstr(INIT_Y, SUBW_WID - 32, "Queue loc:" + str(currec))
        if hasshift:
            modwin.addstr(INIT_Y, INIT_X + EVNT_X - 12, ">DATE<", curses.A_STANDOUT)
            curses.beep()
        modwin.addstr(INIT_Y+2, INIT_X,record['headline'])
        y_curs = INIT_Y + 4
        x_curs = INIT_X
        for ln in textwrap.wrap(record['text'],96):
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
            else:
                if firstback:
                    record['text'] = record['text'] + " [backdated from " + record['date'] +"]"
                    record['headline'] = record['headline'] + " [backdated from " + record['date'] +"]"
                    firstback = False
                """record['date'] = record['date'][:-2] + "{:02d}".format(int(record['date'][-2:]) - 1)
                
                thedate = datetime.datetime(int(record['date'][:4]), int(record['date'][5:7]), int(record['date'][-2:]))"""
                if "2" == keych or "B"  == keych:
                    record['date'], thedate = utilDEDI.newdate(record['date'])
                else:
                    record['date'], thedate = utilDEDI.newdate(record['date'], True)  # 5/F are the only allowable keych options at this point
                record['enddate'] = record['date']
                modwin.addstr(INIT_Y, INIT_X, str(ka) + '  ' + record['country']  + 
                            ": " + record['date'] + " (" + dayOfWeek[thedate.weekday()] + ")")
                
            key, keych = next_key(modwin)
#            fout.write("key-2: " + keych + "\n")
     
        if "A" == keych or "1"  == keych  or " "  == keych:
            nacc += 1
            record["status"] = "accept"
            autohead = record['headline']
            autoid = record['id']
            currec += 1

        elif "X" == keych or "3"  == keych  or "0"  == keych or "=" == keych:
            nrej += 1
            record['status'] = "reject"
            autohead = ""
            autoid = ""
            currec += 1

        elif "S" == keych or "D"  == keych:  # autosave/delete to end of country-day
            curdate = record['date']
            curctry = record['ccode']
            eof = False
            while curdate == record['date'] and curctry == record['ccode'] :
                nauto += 1
                ka += 1
                if keych == "S":
                    record["status"] = "accept"
                    nacc += 1
                else:
                    record["status"] = "reject"
                    nrej += 1
                record["comment"] = "auto-" + record["status"] + " for country-day"
                fout.write(json.dumps(record, indent=2, sort_keys=True ) + "\n")            
                try:
                    record = next(reader)
                except StopIteration:
                    eof = True
                    break
            if eof:
                break  # terminates while True
            record["status"] = None
            recque[-1] = record
            autohead = ""
            autoid = ""
 
        elif keych == "Q":
            nskip = ka - 1
            while len(recque) > 1:
                fout.write(json.dumps(recque.popleft(), indent=2, sort_keys=True ) + "\n")            
            return


nskip = utilDEDI.set_nskip(filename, FILEREC_NAME)
#nskip = -1  ### DEBUG

nacc, nrej = 0,0  # counters for two annotations
auto, autoshort = utilDEDI.read_autocodes(None, True) # only auto is actually used
"""print("Auto:")
for key, val in auto.items():
    print(key, val)
#print("Autoshort:",autoshort)
exit()"""
timestr = utilDEDI.timestamp()
fout = open("plovigy-eval." + infix + coder + timestr,'w')
"""for key, val in auto.items():
    fout.write(key + " " + str(val) + "\n")
exit()"""

reader = utilDEDI.read_file(filename)
curses.wrapper(main)

fout.close()

with open(FILEREC_NAME,'a') as frec:
    frec.write("{:s} {:d} {:s}".format(filename,nskip, timestr)) 
    frec.write( "   accept:{:3d}  reject:{:3d}  total:{:3d}\n".format(nacc, nrej, nacc + nrej))

print("Finished")
