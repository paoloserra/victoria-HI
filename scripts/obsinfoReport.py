import numpy as np
import os
import json
import glob
import shutil
import sys

def findString(fname, stringToFind):
    dataLog = []
    with open(fname, 'rt') as f:
        data = f.readlines()
        
    for line in data:
        if line.__contains__(stringToFind):
            dataLog.append(line)
    
    return dataLog

def pickLine(strList, strToMatch):    
    
    outp = []  

    for s in strList:
        if strToMatch in s:
            outp.append(s)
    
    return outp

def between(strToSearch, strBefore, strAfter):
    # Find and validate before-part.
    pos_a = strToSearch.find(strBefore)
    if pos_a == -1: return ""
    # Find and validate after part.
    pos_b = strToSearch.rfind(strAfter)
    if pos_b == -1: return ""
    # Return middle part.
    adjusted_pos_a = pos_a + len(strBefore)
    if adjusted_pos_a >= pos_b: return ""
    return strToSearch[adjusted_pos_a:pos_b]

def writeStat(strList):
    
    global f
    
    for line in strList:
        f.write(line)

import yaml
import os
import glob

summaryfile = glob.glob('{0:s}/msdir/?????????_sdp_l0-summary.json'.format(os.getcwd()))[0]

#'''
#MOVE ELEVATION PLOT TO REPORT FOLDER
#'''

#pngList = []
#dest_dir = "{}/mfs_report_track{}/".format(cwd, trackNr)

#for file in glob.glob(r'{}/msdir/{}*elevation-tracks.png'.format(cwd, msname)):
#    pngList.append(file.split('/')[-1])
#    shutil.copyfile(file, os.path.join(dest_dir, os.path.basename(file)))

#'''
#OPEN REPORT FILE
#'''

#frep = '{}/mfs_report_track{}/obsinfoReport.txt'.format(cwd, trackNr)
#f = open(frep, 'w')

#'''
#GET OBSINFO FROM THE JSON
#'''
#tmp = findString('xcal.yml', 'dataid')
#dataid = between(tmp[0], '[', ']').replace('\'','')

#if not dataid:
#    ftmp = open('xcal.yml', 'r')
#    Lines = ftmp.readlines()

#    for i, line in enumerate(Lines):
#        if 'dataid' in line:
#            dataid = Lines[i+1].replace('- ','')[:-1].strip()
#            break

with open(summaryfile) as t:
    obsinfo_dict = json.load(t)

ants = obsinfo_dict['ANT']['NAME']

os.system('mkdir -p {0:s}/gtb_reports'.format(os.getcwd()))
f = open('{0:s}/gtb_reports/obsinfo.txt'.format(os.getcwd()), 'w')
f.write('{} antennas in MS:\n'.format(len(ants)))
f.write('{}\n\n'.format(','.join(ants)))

cmd = 'python /home/pserra/Astro/virgo/meerkat/victoria-HI/scripts/baselinesReport.py --in {} --track {}'.format(
    ','.join(ants), trackNr)
os.system(cmd)

f.write('\n')

'''
GET POINTING INFO FROM LOG FILE
'''

obsInfo = findString(fin, 'CARACal INFO:')

'''
FORMAT LINES
'''

obsInfoFormatted = []

for lines in obsInfo:
    obsInfoFormatted.append(' '.join(lines.split()[4:])+'\n')

f.write('```\n')

keys = ['TARGET', 'CALIBRATE_AMPL',
       'CALIBRATE_FLUX', 'CALIBRATE_BANDPASS']

for key in keys:
    t = pickLine(obsInfoFormatted, key)[0]
    writeStat(t)
    temp = obsInfoFormatted.index(t)
    writeStat(obsInfoFormatted[temp+1])

f.write('```\n\n')

f.write('<mfs_report_track{}/{}>'.format(trackNr, pngList[0]))
f.close()
