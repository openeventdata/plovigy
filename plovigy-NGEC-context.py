"""
plovigy-NGEC-context.py

A subset of plovigy-mark.py which uses the NGEC jsonl or .txt format -- choice of format is determined by the file suffix and is in 
the code as `isJSON` and just does simple accept/reject/ignore classification without any other options. In `isJSON` mode, only
records where `thecontext` occurs in `record['contexts']` are presented.

TO RUN PROGRAM:

python3 plovigy-NGEC-context.py <filename> <coder>

where the optional <filename> is the file to read; <coder> is optional coder initials

KEYS

1/a/<space>   accept

3/0/x/        reject

P/-           pass/ignore: skip record and don't write

q             quit 

PROGRAMMING NOTES:

1. The file FILEREC_NAME keeps track of the location in the file.  Use `NGECDIR` to set the default directory

2. Output file names are coder- and time-stamped

3. Input is not case-sensitive
 

SYSTEM REQUIREMENTS
This program has been successfully run under Mac OS 12.2.1; it is standard Python 3.11 so it should also run in Windows. 

PROVENANCE:
Programmer: Philip A. Schrodt
            Parus Analytics
            Charlottesville, VA, 22901 U.S.A.
            http://eventdata.parusanalytics.com

Copyright (c) 2018, 2022	Philip A. Schrodt.	All rights reserved.

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
16-Nov-22:  Modified for NGEC contexts

=========================================================================================================
"""
import textwrap
import datetime
import curses
import json
import sys
import os

FILEREC_NAME = "plovigy.ngec.filerecs.txt"

keyoptions = "A1 X0=E3P-Q"

if len(sys.argv) > 1:
    filename = sys.argv[1]
    isJSON = filename.endswith(".json")
    if filename.endswith(".txt"):
        infix = filename[:filename.index(".txt")]  + "-" 
    elif "Mk7" in filename:
        infix = filename[:filename.index("_fill4")] + "-"    
    else:
        infix = filename[:filename.index(".rftr")] + "-"     
    #print(isJSON, infix)
    #exit()
else:  
    print("File name is required")
    exit()
    
coder = "PAS" 
doUSAcrime = False
if len(sys.argv) > 2:
    if len(sys.argv[2]) > 2:
        coder = sys.argv[2]
    elif sys.argv[2] == "U":
        doUSAcrime = True
        import utilities_NGEC_v0_2b2 as utilNG
        keyoptions += "SWE"


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


SUBW_HGT = 24
SUBW_HGT = 36
SUBW_WID = 148
INIT_Y = 2 
INIT_X = 4

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

def main(stdscr):
    global nacc, nrej, nskip, npass, nodd, keych, record

    keych = ""

    ka = -1
    while True:
        if ka < nskip:
            record = next(reader)
            ka += 1
            continue
#        fout.write("Mk0" + " " + str(ka) + "\n")
            
        record = next(reader)
        ka += 1
        if not doUSAcrime and isJSON and thecontext not in record['contexts']:
            continue

        modwin = curses.newwin(SUBW_HGT ,SUBW_WID, 2, 2)
        modwin.border()         
        
        #thedate = datetime.datetime(int(record['date'][:4]), int(record['date'][5:7]), int(record['date'][-2:]))
        thedate = "YYYYMMDD"
        if doUSAcrime:
            modwin.addstr(INIT_Y, INIT_X, str(ka) + '  ' + record[idfield]  + '  ' + record['plevent'])
            y_curs = INIT_Y + 3
        else:
            if isJSON:
                modwin.addstr(INIT_Y, INIT_X, str(ka) + '  ' + record['text_feed'] +  ": " + record['SourceName'] +  ": " + record['FactivaAccessionNo'] + "     Date: " + record['PublicationDate'])
                modwin.addstr(INIT_Y+1, INIT_X, str(record["contexts"]))        
                modwin.addstr(INIT_Y+3, INIT_X,record['HeadLine'])
                y_curs = INIT_Y + 5
            else:
                modwin.addstr(INIT_Y, INIT_X, str(ka) + '  ' + record[idfield])
                y_curs = INIT_Y + 3
        
        x_curs = INIT_X
        if doUSAcrime:
            fout.write("Start: " + str(len(record["text"])))
            record['text'], filt = utilNG.preprocess(record["text"])
            fout.write("     End: " + str(len(record["text"])) + "\n")
        if len(record[textfield]) < 2:
            record[textfield] = "--short--"
        startch = 3 if record[textfield][1] == '"' else 1
        for ln in textwrap.wrap(record[textfield][startch:],96):
            modwin.addstr(y_curs, x_curs, ln)
            y_curs += 1
            if y_curs >= SUBW_HGT-2:
                break
        if doUSAcrime:
            modwin.addstr(SUBW_HGT-2, x_curs+16, "accept:{:3d}  reject:{:3d}  odd:{:3d}  okay:{:3d}  total:{:3d}".format(nacc, nrej, nodd, npass, nacc + nrej + nodd + npass))
        else:
            modwin.addstr(SUBW_HGT-2, x_curs+16, "accept:{:3d}  reject:{:3d}  skip:{:3d}  total:{:3d}".format(nacc, nrej, npass, nacc + nrej + npass))
            
        modwin.refresh()
        key, keych = next_key(modwin)
     
        if "A" == keych or "1"  == keych  or " "  == keych:
            nacc += 1
            write_rec(thecontext)

        elif "X" == keych  or "0"  == keych or "=" == keych:
            nrej += 1
            if doUSAcrime:
                write_rec("crime")
            else:
                write_rec("reject")
 
        elif "P" == keych or "-"  == keych:
            npass += 1
            
        elif keych in ["S", "W", "E"]:
            nodd += 1
            if keych == "S":
                write_rec("short")
            elif keych == "W":
                write_rec("category")
            else: 
                write_rec("error")
            
            
        elif keych == "Q":
            nskip = ka - 1
            return


def read_file(filename):
    """ returns next JSON record in a JSON or mixed txt/JSON file """
    jstr = ""
    for line in open(filename, "r"):
            if line[0] != "{":
                continue
            adict = json.loads(line[:-1])
            yield adict

def timestamp():
    return '-' + datetime.datetime.now().strftime("%Y%m%d")[2:] + "-" + datetime.datetime.now().strftime("%H%M%S") + ".jsonl"

def write_rec(context):
    outrec = {"id": record[idfield], "plcontext": context, "text": record[textfield]}
    fout.write(json.dumps(outrec, sort_keys=True ) + "\n")            

nskip = set_nskip(filename, FILEREC_NAME)
#nskip = -1  ### DEBUG

nacc, nrej, npass, nodd = 0, 0, 0, 0  # counters for two annotations
timestr = timestamp()


if doUSAcrime:
    NGECDIR = "../NGC-HuggingFace/Annot_train4_Mk7/"  # set default dictionary
    thecontext = "USA"
    fout = open("plovigy_ngec_review." + infix + coder + timestr, 'w')
    textfield = "text"
    idfield = "id"
else:
    NGECDIR = "../data-Trove/NGEC-JSON/"  # set default dictionary
    NGECDIR = "./"
    thecontext = "gender"
    fout = open("plovigy_ngec_eval." + infix + coder + timestr,'w')
    textfield = "event_text"
    idfield = "StoryId"

reader = read_file(os.path.join(NGECDIR, filename))
curses.wrapper(main)

fout.close()

with open(FILEREC_NAME,'a') as frec:
    frec.write("{:s} {:d} {:s}".format(filename,nskip, timestr)) 
    frec.write( "   accept:{:3d}  reject:{:3d}    pass:{:3d}  total:{:3d}\n".format(nacc, nrej, npass, nacc + nrej + npass))

print("Finished")
