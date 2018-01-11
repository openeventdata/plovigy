"""
plovigy-mark.py

A very tiny footprint program that pretty much duplicates the functionality of the "mark" function in 'prodigy'
See the output line for the key combinations; all of these require a <return> since it doesn't look worth the trouble
to program around this; a simple <return> can be treated as <accept> [default] or "reject".

Input and output formats are the same as prodigy.

TO RUN PROGRAM:

python3 plovigy-mark.py <filename> <coder>

where the optional <filename> is the file to read with a hard-coded default; <coder> is typically the coder initials and
will be incorporated into the file name.

KEYS

1/a        accept

2/x        reject

0/<space>  ignore

3/z        toggles the display of the "meta" information

4/d        cycles <return> between accept/reject/ignore

q          quit 

PROGRAMMING NOTES:

1. The file FILEREC_NAME keeps track of the location in the file.

2. Output file names are coder- and time-stamped

3. Input is not case-sensitive

SYSTEM REQUIREMENTS
This program has been successfully run under Mac OS 10.13.2; it is standard Python 3.5
so it should also run in Unix or Windows. 

PROVENANCE:
Programmer: Philip A. Schrodt
            Parus Analytics
            Charlottesville, VA, 22901 U.S.A.
            http://eventdata.parusanalytics.com

Copyright (c) 2018	Philip A. Schrodt.	All rights reserved.

This program was developed as part of research funded by a U.S. National Science Foundation "Resource 
Implementations for Data Intensive Research in the Social Behavioral and Economic Sciences (RIDIR)" 
project: Modernizing Political Event Data for Big Data Social Science Research (Award 1539302; 
PI: Patrick Brandt, University of Texas at Dallas)

This code is covered under the MIT license: http://opensource.org/licenses/MIT

Report bugs to: schrodt735@gmail.com

REVISION HISTORY:
15-Dec-17:	Initial version
04-Jan-18:	Default switching option

=========================================================================================================
"""
import textwrap
import datetime
import json
import sys
import os

FILEREC_NAME = "plovigy.filerecs.txt"

defaultopt = "A"

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:  
    filename = "verify_reutlev171229_4.jsonl"  
        
if len(sys.argv) >= 3:
    coder = sys.argv[2]
else:  
    coder = "PLV"
    
timestamp =  coder  + '-' + datetime.datetime.now().strftime("%Y%m%d")[2:] + "-" + datetime.datetime.now().strftime("%H%M%S") + ".txt"

nskip = 0
if os.path.exists(FILEREC_NAME):
    with open(FILEREC_NAME,'r') as frec:
        line = frec.readline() 
        while line:  # go through the entire file to get the last entry
            if filename in line:
                nskip = int(line.split()[1])
            line = frec.readline()

if nskip < 0:
    print("All records in", filename, "have been coded")
    answ = input("Do you want to restart at the beginning of the file? (Y/N) -->")
    if answ in ['Y','y']:
        nskip = 0
    else:
        print("Please select another file: exiting")
        exit()    

fin = open(filename,'r')
if nskip == 0:
    print("Restarting at the beginning of", filename)
    line = fin.readline() 
else:
    print("Skipping first", nskip,"records in",filename)            
    for ka in range(nskip + 1):
        line = fin.readline() 

firstrec = nskip
lastrec = None
answ = input("Press return to start...")

fout = open("plovigy-eval." + timestamp,'w')
ka = 0
nacc, nrej, nign = 0,0,0
show_meta = False
while len(line) > 0:  
    record = json.loads(line[:-1])
#    print(record)
    print(chr(27) + "[2J")

    if defaultopt == "A":
        print("a/1/DEFAULT: accept  x/2: reject  space/0: ignore   z/3: toggle meta  d/4: toggle default  q: quit\n")
    elif defaultopt == "X":
        print("a/1: accept  x/2/DEFAULT: reject  space/0: ignore   z/3: toggle meta  d/4: toggle default  q: quit\n")
    else:
        print("a/1: accept  x/2: reject  space/0/DEFAULT: ignore   z/3: toggle meta  d/4: toggle default  q: quit\n")
    for ln in textwrap.wrap(record['text'],80):
        print(ln) 
    print("\n\x1B[34m{:20s}\x1B[00m".format(record["label"]),end="")
    print( "                                 accept:{:3d}  reject:{:3d}  ignore:{:3d}  total:{:3d}".format(nacc, nrej, nign, nacc + nrej + nign))
    if show_meta:
        if "pattern" in record["meta"]:
            print("\npattern: " + record["meta"]["pattern"] + "   coding: " + record["meta"]["coding"] )
            print("coder: " + record["meta"]["coder"] + "   class: " + record["meta"]["class"] )
            print("text ID: " + record["meta"]["textid"])
        else:
            print("\nclass: " + record["meta"]["class"])
    
    print()
    scr = input("Evaluate--> ").upper()
    if scr == "":
        scr = defaultopt
    while scr not in "01234AXZDQ ":
        print("Unrecognized option '" + scr + "'. Try again")
        scr = input("Evaluate--> ").upper()
    if "Q" == scr:
        break
    if "Z" == scr or "3" == scr: 
        show_meta = not show_meta
    if "D" == scr or "4" == scr: 
        if defaultopt == "A":
            defaultopt = "X"
        elif defaultopt == "X":
            defaultopt = " "
        else:
            defaultopt = "A"
    else:
        record["_input_hash"] = 0
        record["_task_hash"] = 0
        if "A" == scr or "1" == scr:
            record["answer"] = "accept"
            nacc += 1
        if "X" == scr or "2" == scr:
            record["answer"] = "reject"
            nrej += 1
        if " " == scr or "0" == scr:
            record["answer"] = "ignore"
            nign += 1
        nskip += 1
        line = fin.readline() 
        fout.write(json.dumps(record, sort_keys = True) + "\n")
else:  # reached EOF
    print("All records have been coded")
    lastrec = nskip
#    nskip = -1

fin.close()
fout.close()
with open(FILEREC_NAME,'a') as frec:
    frec.write("{:s} {:d} {:s}".format(filename,nskip, timestamp)) 
    frec.write( "   accept:{:3d}  reject:{:3d}  ignore:{:3d}  total:{:3d}".format(nacc, nrej, nign, nacc + nrej + nign))

print("Finished")
