"""
actor-annot-lite.py

actor-annot-lite.py is a Python program for annotating event files with sentence segmentation, actor, recipient, and 
location spans. It is designed to use minimal machine resources—in the Macintosh OS-X system, it takes about 6Mb of 
memory versus the 350Mb required for a single Google Chrome web page—and does not require connection to a server. 
The program is implemented using the C/Python "ncurses" terminal emulation and uses a small set of keyboard command
rather than a mouse, and is designed to run on a laptop. Like on an airplane.

TO RUN PROGRAM:

python3 actor-annot-lite.py <filename> <coder>

where the optional <filename> is the file to read with a hard-coded default; <coder> is optional coder initials

KEYS: see documentation pdf


PROGRAMMING NOTES:

1. The file FILEREC_NAME keeps track of the location in the file.

2. Output file names are coder- and time-stamped

3. Input is not case-sensitive

4. The test sentIndex == -1 effectively determines whether one is in the primary mode, which works on the main text,
   or the secondary mode working on a single sentence
 

SYSTEM REQUIREMENTS
This program has been successfully run under Mac OS 10.13.2 and Ubuntu 16.04; it is standard Python 3.7 so it should also run in Windows. 

PROVENANCE:
Programmer: Philip A. Schrodt
            Parus Analytics
            Charlottesville, VA, 22901 U.S.A.
            http://eventdata.parusanalytics.com

Copyright (c) 2021	Philip A. Schrodt.	All rights reserved.

This code is covered under the MIT license: http://opensource.org/licenses/MIT

Report bugs to: schrodt735@gmail.com

REVISION HISTORY:
19-Nov-21:  Modified from plovigy-PITF-DEDI.py

=========================================================================================================
"""
import textwrap
import datetime
import curses
import json
import sys
import os

FILEREC_NAME = "actorannot.filerecs.txt"

fieldoptions = " ARLBCFS!@-.:;,\"0123456789/-[]" + chr(10)
keyoptions = fieldoptions + "X=Q"

if len(sys.argv) > 1:
    filename = sys.argv[1]
    infix = filename[6:-5] + "-"
    """print(infix)
    exit()"""
else:  
    print("File name is required")
    exit()
    
if len(sys.argv) >= 3:
    coder = sys.argv[2]
else:  
    coder = "PAS"    


SUBW_HGT = 44
SUBW_WID = 148
INIT_Y = 2 
INIT_X = 4
EVNT_X = 64
MAIN_Y = SUBW_HGT-3

CHARLENGTH = 1024

MODELIST = ["actor", "recip", "locat"]    
ANNOTFIELD = {}
for md in MODELIST:
    ANNOTFIELD[md] = md + "Annot"

def next_key(win):    
    key = 31
    win.addstr(MAIN_Y, 4, "Enter option: ") 
    while chr(key).upper() not in keyoptions: 
        if key != 31:
            win.addstr(MAIN_Y, 4, "Invalid option '" + chr(key) + "', try again: ") 
        key = win.getch()
        win.clrtobot()
        win.border()
    win.refresh()
    return key, chr(key).upper()

    
def get_timestamp():
    return '-' + datetime.datetime.now().strftime("%Y%m%d")[2:] + "-" + datetime.datetime.now().strftime("%H%M%S") + ".jsonl"


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
        with open(filerec_name, "w") as fout:
            fout.write("")
        return

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
        print("Skipping first", nskip + 1,"records in",filename)            

    answ = input("Press return to start...")

    return nskip

def main(stdscr):
    global nacc, nrej, nskip, keych, record, curtext, curspan, cursel
    
    def showtext():
        y_curs = INIT_Y + 2
        x_curs = INIT_X
        for wrdtp in fulllist:
            if x_curs + len(wrdtp[0]) > 128:
                x_curs = INIT_X
                y_curs += 1
                if y_curs >= SUBW_HGT-2:
                    break
            if wrdtp[3] and sentIndex < 0:
                modwin.addstr(y_curs, x_curs, wrdtp[0], curses.A_STANDOUT)
            else:
                modwin.addstr(y_curs, x_curs, wrdtp[0])            
            x_curs += len(wrdtp[0])

        if sentlist:
            y_curs += 1
            for ks, sent in enumerate(sentlist):
                """if "actorSpan" in sent:
                    fout.write("Sent" + str(record["sentences"][ks - 1]) + "\n")"""
                y_curs += 1
                x_curs = INIT_X
                if ks + 1 == sentIndex:
                    modwin.addstr(y_curs, x_curs, "> " + str(ks + 1) + ": ")                
                else:
                    modwin.addstr(y_curs, x_curs, "  " + str(ks + 1) + ": ")                
                x_curs += 6
                for wrdtp in sent:
                    if x_curs + len(wrdtp[0]) > 128:
                        x_curs = INIT_X + 6
                        y_curs += 1
                        if y_curs >= SUBW_HGT-7:
                            break
                    if wrdtp[3] and sentIndex == ks + 1:
                        modwin.addstr(y_curs, x_curs, wrdtp[0], curses.A_STANDOUT)
                    else:
                        modwin.addstr(y_curs, x_curs, wrdtp[0])
                    x_curs += len(wrdtp[0])
                
        """if sentIndex > 0:
            modwin.addstr(SUBW_HGT-7, INIT_X, "Sentence: " + str(sentIndex))"""
        y_curs = SUBW_HGT-8
        for md in MODELIST:
            y_curs += 1
            if not curtext[md]:
                txt = "Not assigned"
            elif len(curtext[md]) == 1:
                txt = curtext[md][0]
            else:
                txt = str(curtext[md])
            modwin.addstr(y_curs, INIT_X, md + ": " + txt)
            modwin.clrtoeol()

        
    def moveinfo(mode):
        global curtext, curspan
        if not curspan[mode]:
            return
        record["sentences"][sentIndex - 1][ANNOTFIELD[mode]] = {"text" : curtext[mode], "span": curspan[mode]}

        
    def get_next_sentence(ltarch, addsent = True):
        global record, cursel

        tarst = ltarch + " "
        notfound = True
        for kw, wrdtp in enumerate(fulllist[cursel + 1:]):
            if wrdtp[0].endswith(tarst):
                notfound = False
                break
        if notfound:
            return False
        while fulllist[cursel + 1][0] == " ":
            cursel += 1
        wrdStart = cursel + 1
        for kw, wrdtp in enumerate(fulllist[wrdStart:]):
            cursel += 1
            if addsent:
                if wrdtp[0].endswith(tarst):
                    if cursel + 1 < len(fulllist):
                        wrdEnd = cursel + 1
                    else:
                        wrdEnd = len(fulllist) - 1
                    break
            else:
                wrdtp[3] = True
                if wrdtp[0].endswith(tarst):
                    break
        if addsent:
            sentlist.append(fulllist[wrdStart:wrdEnd])
            """for kb, st in enumerate(sentlist):
                fout.write(str(kb) + ": " + str(st) + "\n")"""
            record["sentences"].append(
                {"sentext": "".join([wd[0] for wd in fulllist[wrdStart:wrdEnd]]), 
                "sentStart": fulllist[wrdStart][1], "sentEnd":  fulllist[wrdEnd][2]}
                )
        return True

        
    def init_coding():
        global curtext, curspan
        for md in MODELIST:
            curtext[md] = []
            curspan[md] = []

            
    def show_error(err_strg):
        curses.beep()
        modwin.addstr(MAIN_Y+1, 4, err_strg)
            
            
    def get_string(prompt):
        modwin.addstr(MAIN_Y+1, 4, prompt)
        curses.echo()
        inbyte = modwin.getstr()
        tarstr = inbyte.decode("utf-8")
        curses.noecho()
        return tarstr
               

    modwin = curses.newwin(SUBW_HGT ,SUBW_WID, 2, 2)  # just erase
    keych = ""
    curtext, curspan = {}, {}
    init_coding()

    for ka, line in enumerate(fin):
        if ka <= nskip:
            continue
            
        record = json.loads(line[:-1])            
        thetext = record["text"][:CHARLENGTH].replace("\n", "  ")
        if len(thetext) >= CHARLENGTH:
            record["text"] = thetext[:thetext.rfind(" ")] # end at word boundary  
        else:
            record["text"] = thetext       
        if "sentences" not in record:
            record["sentences"] = []

        init_coding()
        sentlist = []
        sentIndex = -1
        gotF = False
                
        modwin.erase()
        modwin.border()
        modwin.addstr(INIT_Y, INIT_X, "Record {:3d}   Category: {:s}".format(ka+1, record['plevent']))

        fulllist = []  # get words for entire article
        wdstart = 0
        wd = ""
        for loc, ch in enumerate(record['text']):
            if ch == " ":
                fulllist.append([wd + " ", wdstart,loc, False])
                wdstart = loc + 1
                wd = ""
            else:
                wd += ch

        curlist = fulllist                        
        cursel = -1
        passkey = False
        
        showtext()

        x_curs = INIT_X
        #modwin.addstr(MAIN_Y, SUBW_WID - 120, "Options:  A/1/ /accept  X/0/3/=/reject  B/2 backdate  F/5 adddate  Q/quit")         
            
        modwin.refresh()
        key, keych = next_key(modwin)

        curmode = ""
        while keych in fieldoptions: # selections without writing 
        
            if " " == keych: # select next word #or keych == chr(curses.KEY_RIGHT): # turns out these are difficult to use in ncurses
                if cursel < len(curlist) - 1:
                    cursel += 1
                    curlist[cursel][3] = True
                else:
                    curses.beep()

            elif keych in ["[", "]"]:
                if sentIndex < 0:
                    show_error("Select a sentence to work on")
                elif not curmode:
                    show_error("Select an A, R, or L mode")                   
                elif keych == "[":
                    gotone = False
                    for kw, wrdtp in enumerate(curlist):
                        if wrdtp[0].istitle():
                            if gotone:
                                cursel = kw
                                curlist[cursel][3] = True
                                break
                            else:
                                gotone = True
                    else: # loop else
                        show_error("Second capitalized word not found ")

                else:
                    while (cursel + 1 < len(curlist) and 
                          (curlist[cursel + 1][0].istitle() or 
                           curlist[cursel + 1][0] in ["of ", "for ", "and ", "the "])
                          ):
                        cursel += 1
                        curlist[cursel][3] = True

            elif "B" == keych: # unselect last word # or key == curses.KEY_LEFT:
                if cursel > 0:
                    curlist[cursel][3] = False
                    cursel -= 1
                else:
                    curses.beep()

            elif "F" == keych:
                curlist[cursel][3] = False
                for kw, wrdtp in enumerate(curlist[cursel + 1:]):
                    if wrdtp[0].startswith(tarstr):
                        cursel = cursel + kw + 1
                        curlist[cursel][3] = True
                        gotF = True
                        break
                else:
                    if gotF:
                        curlist[cursel][3] = False
                        cursel = -1
                        passkey = True
                    else:    
                        show_error("Target '" + tarstr + "' not found ")

            elif keych in [".", '"', ':', ","] :
                if sentIndex > 0:
                    curses.beep()                
                elif not get_next_sentence(keych, False):
                    show_error("Delimiter '" + keych +  "' not found ")

            elif sentIndex < 0 and keych == ";" :
                #fout.write("Mk0 " + str(cursel) + " " + curlist[cursel][0] + "\n")
                curlist[cursel][3] = False
                while (cursel < len(fulllist) and 
                       len(fulllist[cursel][0]) >= 2 and 
                       (fulllist[cursel][0][-2:] not in ["- ", "— ", ") "])
                    ):
                    cursel += 1
                   # fout.write("Mk1 " + str(cursel) + " " + curlist[cursel][0] + "\n")
                if cursel >= len(fulllist):
                    show_error("No dateline delimiters found ")
                else:
                   # fout.write(str(cursel) + " " + curlist[cursel][0] + "\n")
                    cursel += 1
                    while fulllist[cursel][0] == " ":
                        cursel += 1
                    curlist[cursel][3] = True
                    
            elif keych == "A" or keych == "R" or keych == "L": 
                if sentIndex == -1:
                    show_error("Select a sentence to work on")
                else:     
                    typestr = "Actor target: " if keych == "A" else "Recip target: " if keych == "R" else "Locat target: "
                    curmode =  "actor" if keych == "A" else "recip" if keych == "R" else "locat"
                    modwin.addstr(MAIN_Y+1, 4, "Enter " + typestr)
                    curses.echo()
                    inbyte = modwin.getstr()
                    tarstr = inbyte.decode("utf-8")
                    curses.noecho()
                    #fout.write(str(cursel) + " 1: " + str(curlist[cursel]) + " 2: " + str(fulllist[cursel]) + "\n")
                    if not tarstr:
                        curlist[cursel][3] = True
                                                
                    elif tarstr[0] in ["[", "]"]:
                        key, keych = ord(tarstr[0]), tarstr[0]
                        passkey = True

                    elif tarstr[0] == "-":
                        try:
                            curtext[curmode].pop()
                            curspan[curmode].pop()
                        except:
                            show_error("Mode '" + curmode +  "' has not been assigned ")

                    else:   
                        for kw, wrdtp in enumerate(curlist):
                            if wrdtp[0].startswith(tarstr):
                                cursel = kw
                                curlist[cursel][3] = True
                                break
                        else:
                            show_error("Target '" + tarstr + "' not found ")

            elif keych == "S":  
                sentIndex = -1
                modwin.addstr(MAIN_Y+1, 4, "Enter sentence target or delimiter: ")
                curses.echo()
                inbyte = modwin.getstr()
                tarstr = inbyte.decode("utf-8")
                curses.noecho()
                if tarstr == "":  # <return>: select the first word of the next sentence
                    cursel += 1
                    while cursel < len(fulllist) and fulllist[cursel][0] == " ":
                        cursel += 1
                    if cursel < len(fulllist):
                        fulllist[cursel][3] = True
                elif tarstr in [".", '"', ':', ","] :
                    if not get_next_sentence(tarstr[0]):
                        show_error("Delimiter '" + tarstr[0] +  "' not found ")
                else:
                    dothe = tarstr == ";"
                    if dothe:
                        tarstr = "The"
                    for kw, wrdtp in enumerate(fulllist):
                        if wrdtp[0].startswith(tarstr):
                            cursel = kw +1 if dothe else kw
                            fulllist[cursel][3] = True
                            break
                    else:
                        show_error("Target '" + tarstr + "' not found ")

            elif keych == "/":
                while len(record["sentences"]) <= 10:
                    if not get_next_sentence("."): 
                        break

            elif keych >= "0" and keych <= "9": 
                if sentIndex > 0:
                    for md in MODELIST:
                        moveinfo(md)                   
                if keych == "0":
                    keych = "10"
                sentIndex = int(keych)
                if sentIndex > len(sentlist):
                    show_error("Index '" + keych + "' must be between 1 and " + str(len(sentlist)))
                    sentIndex = -1
                    curlist = fulllist 
                else:
                    """fout.write("\nStatus for " + str(sentIndex)  + "\n")
                    for st in record["sentences"]:
                        fout.write("\n" + str(st) + "\n")"""
                    curlist = sentlist[sentIndex - 1]
                    """for kw, wrdtp in enumerate(fulllist):
                        if wrdtp[1] == record["sentences"][sentIndex - 1]["sentStart"]:
                            cursel = kw
                            break"""
                    cursel = 0
                    while fulllist[cursel][0] == " ":
                        cursel += 1
                    curmode = ""
                    for md in MODELIST:
                        if ANNOTFIELD[md] in record["sentences"][sentIndex - 1]:
                            curtext[md] = record["sentences"][sentIndex - 1][ANNOTFIELD[md]]['text'] 
                            curspan[md] = record["sentences"][sentIndex - 1][ANNOTFIELD[md]]['span'] 
                        else:
                            curtext[md] = []
                            curspan[md] = []
                                                                  
            elif 10 == key: # <return>: accept input
                spanStart = -1
                spanText = ""
                for kw, wrdtp in enumerate(fulllist):
                    if wrdtp[3]:
                        if spanStart == -1:
                            spanStart = wrdtp[1]
                            wrdStart = kw
                        spanEnd = wrdtp[2]
                        wrdEnd = kw
                        spanText += wrdtp[0] 
                        wrdtp[3] = False               
                if sentIndex > 0:
                    if curmode:
                        curtext[curmode].append(spanText)
                        curspan[curmode].append((spanStart, spanEnd))
                    else:
                        show_error("Select an A, R, or L mode")                                       
                else:
                    sentlist.append(fulllist[wrdStart:wrdEnd + 1])
                    record["sentences"].append({"sentext": spanText, "sentStart": spanStart, "sentEnd": spanEnd})                                           
                    
            elif "!" == keych or "@" == keych:
                if "!" == keych:
                    sentlist = []
                    sentIndex = -1                
                    record["sentences"] = []
                init_coding()
                cursel = -1
                for wrdtp in fulllist:
                    wrdtp[3] = False
                curlist = fulllist
                
                modwin.erase()
                modwin.border()
                modwin.addstr(INIT_Y, INIT_X, "Record {:3d}   Category: {:s}".format(ka+1, record['plevent']))                
                
            elif "C" == keych:
                cmtstr = get_string("Enter comment: ")
                cmtstr = cmtstr + " <" + coder + " " + get_timestamp()[-19:-8] + ">"
                if "comment" in record:
                    record["comment"] += "; " + cmtstr
                else:
                    record["comment"] = cmtstr

            showtext()
            modwin.refresh()
                                     
            if passkey:
                passkey = False
            else:
                key, keych = next_key(modwin)
#            fout.write("key-2: " + keych + "\n")
     
        if "=" == keych or "X" == keych:
            if not record["sentences"] or "X" == keych:
                del record["sentences"]
                record["annotstatus"] = "reject"
                nrej += 1  
            else:
                if sentIndex > 0:
                    for md in MODELIST:
                        moveinfo(md)                   
                record["sentences"] = [sentrec for sentrec in record["sentences"] if
                                       ('actorAnnot' in sentrec) or ('recipAnnot' in sentrec) or ('locatAnnot' in sentrec)]
                nacc += 1
                record["annotstatus"] = "accept"
            fout.write(json.dumps(record, indent=2, sort_keys=True ) + "\n")            

        elif keych == "Q":
            nskip = ka - 1
            return

    print("All records have been coded")
    nskip = -1


nskip = set_nskip(filename, FILEREC_NAME)
#nskip = -1  ### DEBUG
#nskip = 8  ### DEBUG

nacc, nrej = 0,0  # counters for two annotations
timestr = get_timestamp()
fout = open("actor-" + infix + coder + timestr,'w')

fin = open(filename, "r")
curses.wrapper(main)

fin.close()
fout.close()

with open(FILEREC_NAME,'a') as frec:
    frec.write("{:s} {:d} {:s}".format(filename,nskip, timestr)) 
    frec.write( "   accept:{:3d}  reject:{:3d}  total:{:3d}\n".format(nacc, nrej, nacc + nrej))

print("Finished")
