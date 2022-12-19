"""
utilDEDI.py

jsonl read/write for the DEDI programs and other utilities

NOTE 19.10.22: Those customized writeedit()/writesrc() -- originally there is provide a more readable 
               JSONL format for manual editing, which wasn't needed after a while -- were a bad idea,
               or at least should have used a more systematic (and compatible) way of dealing with None

Programmer: Philip A. Schrodt <schrodt735@gmail.com>
This code is covered under the MIT license: http://opensource.org/licenses/MIT

REVISION HISTORY:
31-Jul-2019:	Initial version
07-Aug-2019:    Added timestamp()
22-Apr-2020:    Added read_autocodes()
=========================================================================================================
"""

import subprocess
import datetime
import json
import os

#MONTH_INFIX = "201503"
MONTH_INFIX = "202212"
#MONTH_INFIX = "201913"
MONTH_SUFFIX = "-" + MONTH_INFIX + ".jsonl"

VERSION = "1.8b1"

# Autocode tuple indices
AUTOCODE = 0
AUTODMND = 1
AUTOCONT = 2
AUTOCASE = 3
AUTOREJT = 4
AUTOREMV = 5


recOrder = ["ccode", "status", 
            "+date", "comment", "country", 
            "+id", "icewsid",
            "-headline", 
            "-text", 
            "+size", "sizeCategory", 
            "+protesterdemand", "stateresponse", 
            "+protest",  "protesterviolence", "protesteridentity",
            "+event", "eventText",
            "-location", 
            "+region", "version", "language",  "publication", "year", "enddate", "citation", "codedDate", "coder"]

srcOrder = ["ccode", "status", "+id",
            "+date", "comment", "country", "region", "event", "eventText",            
            "-headline", 
            "-text", 
            "+size", "sizeCategory", 
            "+protesterdemand", "stateresponse", 
            "+protesterviolence", "protesteridentity",
            "-location", 
            "+region", "version", "language", "publication", "year", "enddate", "citation"]

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
            
def writeedit(rec, fout):
    """ Write combined record """
    fout.write('{\n')
    for fl in recOrder[:-1]:
        if fl.startswith("-"):
            fl = fl[1:]
            fout.write('\n"' + fl + '":\n')
            if fl == "location":
                fout.write(json.dumps(rec[fl]) + ",")
            else:
                fout.write(json.dumps(rec[fl], indent=2, sort_keys=True ) + ",")
                        
        elif fl.startswith("+"):
            fout.write("\n")
            fl = fl[1:]
            fout.write('"' + fl + '": "' + str(rec[fl])  + '", ')
        else:
            if fl == "eventText":
                fout.write(json.dumps(rec[fl]) + ",")
            else:
                fout.write('"' + fl + '": "' + str(rec[fl])  + '", ')
    fl = recOrder[-1]
    fout.write('"' + fl + '": "' + str(rec[fl])  + '"\n}\n')


def writesrc(rec, fout):
    """ Write original record """
    fout.write('{\n')
    for fl in srcOrder[:-1]:
        if fl.startswith("-"):
            fl = fl[1:]
            fout.write('\n"' + fl + '":\n')
            if fl == "location":
                fout.write(json.dumps(rec[fl]) + ",")
            else:
                fout.write(json.dumps(rec[fl], indent=2, sort_keys=True ) + ",")
                        
        elif fl.startswith("+"):
            fout.write("\n")
            fl = fl[1:]
            fout.write('"' + fl + '": "' + str(rec[fl])  + '", ')
        else:
            if fl == "eventText":
                fout.write('"eventText": '+ json.dumps(rec[fl]) + ",")
            elif fl == "language":
                fout.write('"language": "'+ rec[fl][0] + '", ')
            else:
                if rec[fl]:
                    fout.write('"' + fl + '": "' + str(rec[fl])  + '", ')
                else:
                    fout.write('"' + fl + '": null, ')
    fl = srcOrder[-1]  
    if rec[fl]:
        fout.write('"' + fl + '": "' + str(rec[fl])  + '"\n}\n')
    else:
        fout.write('"' + fl + '": null\n}\n')

    
def timestamp():
    return '-' + datetime.datetime.now().strftime("%Y%m%d")[2:] + "-" + datetime.datetime.now().strftime("%H%M%S") + ".jsonl"

    
def newdate(isodate, forward = False):
    """move the date back one day
    Note: Python 3.7 has a "datetime.fromisoformat()" function to do the conversion without the string conversions. Though now I've written them..."""
    if forward:
        thedate = datetime.date(int(isodate[:4]), int(isodate[5:7]), int(isodate[-2:])) + datetime.timedelta(days = 1)
    else:
        thedate = datetime.date(int(isodate[:4]), int(isodate[5:7]), int(isodate[-2:])) - datetime.timedelta(days = 1)
    return thedate.isoformat(), thedate
    

def read_autocodes(demandset = None, fromplovigy = False):
    auto ={}
    autoshort = {}
    for autofile in ["autocodes-DEDI.txt", "autocodes-" + MONTH_INFIX + "-DEDI.txt"]:
        if not os.path.isfile(autofile):
            print("\aError: could not locate", autofile + ". Exiting")
            exit()
        for line in open(autofile,"r"):
            if line.startswith("-- STOP"):
                break
            if not fromplovigy and line.startswith("-- SEL"):
                break
            if len(line) < 32 or line.startswith("#"):
                continue
            rec = json.loads(line[:-1])

            if demandset:
                for li in rec['demands']:
                    if li not in demandset and li[7].upper() + li[8:] not in demandset: # second option is a constructed "Oppose"
                        print("Error: Unrecognized add-demand in", rec)
                        exit()
                if "remove" in rec:
                    for li in rec['remove']:
                        if li not in demandset and li[7].upper() + li[8:] not in demandset: # second option is a constructed "Oppose"
                            print("Error: Unrecognized remove-demand in", rec)
                            exit()
                    
            if autofile != "autocodes-DEDI.txt":
                rec['yrmon'] = MONTH_INFIX
            if 'yrmon' not in rec or rec['yrmon'] == MONTH_INFIX:
                if "keyseq" in rec:
                    shortkey = rec['keyseq'][1]
                    if shortkey not in autoshort:
                        autoshort[shortkey]  = {}
                    if 'continuation' in rec:
                        autoshort[shortkey][rec['ccode']] = (rec['demands'], rec['continuation'])
                    else:
                        autoshort[shortkey][rec['ccode']] = (rec['demands'], False)
                
                if "targetstr" in rec:
                    if "$" in rec['targetstr']:
                        if "$p" in rec['targetstr']:
                            targlist = [rec['targetstr'].replace("$p", li) for li in ["people", "demonstrators", "protesters"]]
                        elif "$d" in rec['targetstr']:
                            targlist = [rec['targetstr'].replace("$d", li) for li in ["protest", "demonstration", "rally", "march",
                                                                                      "sit in", "sit-in"]]
                        elif "$e" in rec['targetstr']:
                            targlist = [rec['targetstr'].replace("$e", li) for li in 
                                        ["protesting", "demonstrating", "rallying", "gathering", "marching",
                                         "protested", "demonstrated", "rallied", "gathered", "marched",
                                         "protest", "demonstrate"]
                                       ]
                        elif "$t" in rec['targetstr']:
                            targlist = [rec['targetstr'].replace("$t", li) for li in ["price", "tax", "rent"]]
                        else:
                            print("\aError: Unrecognized substitution token in autodemand file:\n" + line[:-1])
                            print("Exiting")
                            exit()                        
                    else:
                        targlist = [rec['targetstr']]
                    
                    for targ in targlist:
                        if ("case" not in rec or rec['case'] != "True") and not targ.islower():
                            print("\aError: Upper-cased target without `case = True` in autodemand file:\n" + line[:-1])
                            print("Exiting")
                            exit()
                        if targ not in auto:
                            auto[targ] = []

                        auto[targ].append((rec['ccode'], rec['demands'], 'continuation' in rec, 'case' in rec, 
                                        'reject' in rec, rec.get("remove")))

                elif "keyseq" not in rec:
                    print("\aMissing 'targetstr' and 'keyseq' fields in autocodes-DEDI.txt:\n", line,"Exiting")
                    exit() 
    return auto, autoshort
    
    
def check_autopat(wrd, thetext):
    if "*" in wrd:
        part = wrd.partition("*")
        idx = thetext.find(part[0])
        if idx >= 0:
            ida = thetext.find(part[2],idx + len(part[0]))
#            print("'"+thetext[idx + len(part[0]):ida]+"'")
            return (ida > 0 and thetext[idx + len(part[0]):ida].count(" ")<= 3)
        else:
            return False
    elif "?" in wrd:
        part = wrd.partition("?")
        idx = thetext.find(part[0])
        if idx >= 0:
            ida = thetext.find(part[2],idx + len(part[0]))
            return (ida > 0 and ida - idx - len(part[0])<= 1)
        return False
    else:
        return (wrd in thetext)


def mergerecords(rec, mrec):
    """ Merge mrec into rec """            
    def mergefield(field):
    #    print(field)
        if mrec[field] and rec[field]:
            for li in mrec[field]:
                if li not in rec[field]:
                    rec[field].append(li)
        elif mrec[field] and not rec[field]:
            rec[field] = mrec[field]

    def mergelocation():
        citylist = [li['city'] for li in rec['location']]
        for li in mrec['location']:
            if li['city'] not in citylist:
                rec['location'].append(li)

    def mergeboolean(field):
        if mrec[field] or rec[field]:
            rec[field] = True
    
    mergefield('icewsid')
    mergefield('headline')
    mergefield('text')
    mergefield('event')
    mergefield('eventText')
    mergefield('size')
    if rec['sizeCategory'] == "None" or rec['sizeCategory'] == "":  # 19.08.26 this is a kludge... <20.05.19> and probably no longer needed
        rec['sizeCategory'] = []
    mergefield('sizeCategory')
    mergefield('protesterdemand')
    mergefield('protesteridentity')
    mergefield('publication')
    mergefield('citation')
    mergefield('language')
    mergefield('stateresponse')
    mergelocation()
    mergeboolean('continuation')
    mergeboolean('protesterviolence')
    rec['status'] = "accept"
    
    return(rec)

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
    
serial = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ" # labels for organize

def parse_orgstring(orgstrg):
        """ make sure this will parse """
        if "/" in orgstrg:
            scrlist = [li.strip().upper() for li in orgstrg.split("/")]
        else:
            scrlist = [li.replace("[", "").replace(","," ").strip().upper() for li in orgstrg.split("]")]
        orglist = []
        for li in scrlist:
            if not li:
                continue
            for la in li.split():
#                fout.write(la + "\n")
                if "-" in la:
                    orglist.append(la)
                    continue
                if len(la) > 1 or serial.find(la) < 0:
                    return None
            orglist.append(li)
#        fout.write("\nMk1 " + str(orglist) + "\n")
        return orglist
        

def get_stamp():
    try:
        for line in open("codedfiles.list." + MONTH_INFIX + ".txt","r"):
            if line.startswith("Stamp: "):
                suffix = line[7:-1]  # get last suffix entry
        return suffix
    except:
        print("\a\aCould not find the required file 'codedfiles.list." + MONTH_INFIX + ".txt': exiting")
        exit()

def get_splitlist():
    suffix = get_stamp()
    splitlist = []
    ka = 0
    while True:
        filename = "protest-coded-split-" + suffix + "-" + serial[ka] + ".jsonl"
        if os.path.isfile(filename):
            splitlist.append(filename)
            ka += 1
        else:
            return splitlist
        