"""
plovigy-NGEC-review.py

plovigy-NGEC-review.py is a very tiny footprint Python program distantly based on the prodigy program that is used to 
review the NGEC training cases. It is keyboard based and runs in a terminal using the incredibly robust golden-oldie 
`curses` library.

See the document plovigy-NGEC-review.documentation.pdf for operating details

TO RUN PROGRAM:

python3 plovigy-NGEC-review.py <filename> <coder>

where the optional <filename> is the file to read; <coder> is optional coder initials

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
21-Nov-22:  Modified for NGEC training review
30-Nov-22:  Assorted additional options: D,V,F

=========================================================================================================
"""
import textwrap
import datetime
import curses
import json
import sys
import os

SERIAL = "1234567890ABCDEFG"
FILEREC_NAME = "plovigy.ngec.filerecs.txt"

PLOVERLIST = ["AGREE", "CONSULT", "SUPPORT", "CONCEDE", "COOPERATE", "AID", "RETREAT", "REQUEST",
              "ACCUSE", "REJECT", "THREATEN", "PROTEST", "SANCTION", "MOBILIZE", "COERCE", "ASSAULT", "EXIT"]
OPTIONLIST = ["A: USA", "C: crime", "V: A + C", "D: disaster", "F: accident", "S: too short", "W: wrong categry"] # this will be extended 

if not os.path.exists(FILEREC_NAME):
    fout = open(FILEREC_NAME, "w")
    fout.close()

keyoptions = "ADXSWECPVF Q"
keyoptions += chr(10)


if len(sys.argv) > 1:
    filename = sys.argv[1]
    isJSON = filename.endswith(".json")
    try:
        infix = filename[:filename.index("_fill4")] + "-"
    except:
        if isJSON:
            infix = filename[:filename.index(".json")] + "-"
        else:
            infix = filename[:filename.index(".txt")] + "-"              
    #print(isJSON, infix)
    #exit()
else:  
    print("File name is required")
    exit()
    
coder = sys.argv[sys.argv.index("-c") + 1] if "-c" in sys.argv else "PAS"
    
recodestr = sys.argv[sys.argv.index("-r") + 1] if "-r" in sys.argv else "---"
if recodestr != "---":
    if recodestr not in PLOVERLIST:
        print("\aWarning: -r option is not a PLOVER category\nQuit and try again if this is not deliberate")
    keyoptions += "R"
    OPTIONLIST.append("R: " + recodestr)
    
OPTIONLIST.extend(["X: discard", "<space> or <return>: okay", "Q: quit"])

excludelist = []
nexcl = 0
if "-x" in sys.argv:
    idx = sys.argv.index("-x") + 1
    while not sys.argv[idx].startswith("-"):
        excludelist.append(sys.argv[idx]) 
        idx += 1
        if idx >= len(sys.argv):
            break


def next_key(win):    
    key = 31
    win.addstr(SUBW_HGT-2, 2, "Enter option: ")  
    while chr(key).upper() not in keyoptions: 
        if key != 31:
            win.addstr(SUBW_HGT-3, 2, "Invalid option '" + chr(key) + "', try again: ") 
        key = win.getch()
        win.clrtobot()
        win.border()
    win.refresh()
    return key, chr(key).upper()


SUBW_HGT = 32
SUBW_HGT = 36
SUBW_WID = 148
INIT_Y = 2 
INIT_X = 4

MIN_LENGTH = 224  # texts below this length are automatically coded "short"
TEXT_WIDTH = 96   # textwrap() width

def set_nskip(filename, filerec_name):
    """ skip previously coded records """
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
    global nUSA, ncrm, nskip, npass, nodd, ndis, nsht, nnew, nexcl, recloc, keych, record

    def show_labels():
        Y_ORG = 4
        X_ORG = 108
        modwin.addstr(Y_ORG, X_ORG, "CATEGORIES")
        modwin.addstr(Y_ORG + 1, X_ORG, "----------")
        yc = Y_ORG + 2
        for ka, val in enumerate(PLOVERLIST):
            modwin.addstr(yc, X_ORG, SERIAL[ka]  + ": " + val + "               ")
            yc += 1

    def show_options():
        Y_ORG = 4
        X_ORG = 108
        modwin.addstr(Y_ORG, X_ORG, "OPTIONS")
        modwin.addstr(Y_ORG + 1, X_ORG, "----------")
        yc = Y_ORG + 2
        for ka, val in enumerate(OPTIONLIST):
            modwin.addstr(yc, X_ORG, val)
            yc += 1

    keych = ""

    ka = -1
    while True:
        if ka < nskip:
            record = next(reader)
            ka += 1
            continue
#        fout.write("Mk0" + " " + str(ka) + "\n")
            
        try:
            record = next(reader)
        except:
            recloc = ka - nskip
            nskip = -1   # indicates EOF
            break
            
        ka += 1

        if excludelist:
            if any(targ in record[textfield] for targ in excludelist):
                nexcl += 1
                continue                    
            
        modwin = curses.newwin(SUBW_HGT ,SUBW_WID, 2, 2)
        modwin.border() 
        
        show_options()        
        
        modwin.addstr(INIT_Y, INIT_X, str(ka) + '  ' + str(record[idfield])  + '  ' + record['plevent'])
        y_curs = INIT_Y + 3
        
        x_curs = INIT_X
        if len(record[textfield]) < MIN_LENGTH:
            nsht += 1
            write_rec("short")
            continue
        idx = record[textfield].find(' . ')
        if idx >= 0:
            for ln in textwrap.wrap(record[textfield][:idx + 2].strip(),TEXT_WIDTH):
                modwin.addstr(y_curs, x_curs, ln)
                y_curs += 1
            y_curs += 1
        else:
            idx = -2
           
        for ln in textwrap.wrap(record[textfield][idx + 2:].strip(),TEXT_WIDTH):
            modwin.addstr(y_curs, x_curs, ln)
            y_curs += 1
            if y_curs >= SUBW_HGT-2:
                break
        modwin.addstr(INIT_Y, INIT_X+48, f"okay: {npass:3d}   USA: {nUSA:3d}  crime: {ncrm:3d}   disast/accid: {ndis:3d}   recoded: {nnew:3d}  odd: {nodd:3d}  short: {nsht:3d}")
            
        modwin.refresh()
        key, keych = next_key(modwin)
     
        if " "  == keych or chr(10)  == keych:  # space and <rtn>
            npass += 1            
        elif "A" == keych:  # this block of code could be converted to a table lookup
            nUSA += 1
            write_rec("USA")
        elif keych == "S":
            nsht += 1
            write_rec("short")
        elif keych == "W":
            show_labels()
            thecat = "---"
            while thecat == "---":
                modwin.addstr(SUBW_HGT-3, 2, "Enter correct categories: ")  
                curses.echo()
                inbyte = modwin.getstr()
                curses.noecho()
                thestr = inbyte.decode("utf-8").upper()
                thecat = ""
                for ch in thestr:
                    if ch not in SERIAL:
                        modwin.addstr(SUBW_HGT-2, 2, "Category label " + ch +" not found; try again")  
                        thecat = "---"
                        break
                    thecat += PLOVERLIST[SERIAL.find(ch)] + ", "
            write_rec("category:" + thecat[:-2])
            nnew += 1
        elif keych == "R":
            write_rec("category:" + recodestr)
            nnew += 1
        elif keych == "C":
            write_rec("crime")
            ncrm += 1
        elif keych == "D":
            write_rec("disaster")
            ndis += 1
        elif keych == "F":
            write_rec("accident")
            ndis += 1
        elif keych == "X":
            write_rec("error")
            nodd += 1                        
        elif keych == "V":
            write_rec("USA, crime")
            ncrm += 1                        
            nUSA += 1                        
        elif keych == "Q":
            recloc = ka - nskip
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
    outrec = {"id": record[idfield], "plevent": context, "text": record[textfield]}
    fout.write(json.dumps(outrec, sort_keys=True ) + "\n")            

nskip = set_nskip(filename, FILEREC_NAME)
firstrec = nskip
#nskip = -1  ### DEBUG

nUSA, ncrm, npass, nodd, nsht, ndis, nnew = 0, 0, 0, 0, 0, 0, 0  # counters for annotations
timestr = timestamp()

NGECDIR = "../NGC-HuggingFace/Annot_train4_Mk7/"  # set default dictionary
NGECDIR = "./"  # set default dictionary
fout = open("plovigy_ngec_review." + infix + coder + timestr, 'w')
textfield = "text"
idfield = "id"

reader = read_file(os.path.join(NGECDIR, filename))
curses.wrapper(main)

fout.close()

with open(FILEREC_NAME,'a') as frec:
    frec.write("{:s} {:d} {:s}".format(filename,nskip, timestr)) 
    frec.write(f"Totals:  okay: {npass:3d}   USA: {nUSA:3d}  crime: {ncrm:3d}   disast/accid: {ndis:3d}   recoded: {nnew:3d}  odd: {nodd:3d}  short: {nsht:3d}") 
    if excludelist:
        frec.write(f"   Excluded {nexcl:3d}: " + str(excludelist))
    frec.write("\n")
print(f"Totals:  okay: {npass:3d}   USA: {nUSA:3d}  crime: {ncrm:3d}   disast/accid: {ndis:3d}   recoded: {nnew:3d}  odd: {nodd:3d}  short: {nsht:3d}", end="")
if excludelist:
    print("   excluded:", nexcl)
else:
    print()
fileloc = str(nskip) if nskip >= 0 else "EOF"
print(f"Records coded: {recloc: 3d}   File location: {fileloc:s}")

print("Finished")