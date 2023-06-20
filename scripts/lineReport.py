import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec
import os
import sys
import glob
import datetime
import shutil

from astropy.wcs import WCS
from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy.nddata import Cutout2D
from astropy import units as u
from astropy.wcs.utils import pixel_to_skycoord
from mpl_toolkits.axes_grid1 import make_axes_locatable

'''
FUNCTIONS TO FIND STRINGS IN FILES AND EXTRACT VALUES
'''

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

def orderedLogs(parentFolder):
    global cwd
    tmp, tmp2 = [], []
    for name in glob.glob('{}/{}/logs-????????-??????'.format(cwd, parentFolder)):
        tmp.append(name.split('/')[-1].split('-')[-2:])

    for l in tmp:
        tmp2.append('-'.join(l))

    if 'logs' in tmp2: tmp2.remove('logs')

    logSorted = sorted(tmp2, reverse= True)

    return ['logs-' + s for s in logSorted]

def cubeRead(imName):

    imhdu = fits.open(imName)[0]

    global conv_dict, axis_dict

    zAxisType = imhdu.header['CTYPE3'].lower()

    try:
        zAxisUnit = imhdu.header['CUNIT3']
    except KeyError:
        zAxisUnit = 'km/s'

    if zAxisType.lower() == 'freq'.lower():
        imhdu.header['CDELT3'] = imhdu.header['CDELT3']*conv_dict[zAxisUnit]
        imhdu.header['CRVAL3'] = imhdu.header['CRVAL3']*conv_dict[zAxisUnit]
        zAxisUnit = 'MHz'
    else:
        imhdu.header['CDELT3'] = imhdu.header['CDELT3']*1e-3
        imhdu.header['CRVAL3'] = imhdu.header['CRVAL3']*1e-3

    wcs = WCS(imhdu.header)

    return imhdu, wcs, zAxisType, zAxisUnit


cwd = os.getcwd()

fin = open('{0:s}/gtb_reports/obsinfo.txt'.format(cwd)).readlines()
add_targets = 0
for ff in fin:
  if '  target (TARGET):' in ff:
    add_targets = 1
    target_list = []
  if add_targets and ff[:9] == '    virgo':
    target_list.append(ff)
target_list = np.array([tt.split() for tt in target_list])
target_name, target_ra, target_dec = target_list[:,0], target_list[:,6], target_list[:,8]
target_ra = [float(ra.split('RA=')[-1]) for ra in target_ra]
target_dec = [float(dec.split('Dec=')[-1]) for dec in target_dec]
radec = [[target_ra[ii], target_dec[ii]] for ii in range(len(target_ra))]
radec = dict(zip(target_name, radec))

fin = 'output/log-caracal.txt'
prefix = pickLine(findString(fin, 'CARACal INFO:'), 'prefix:')[0].strip().split()[-1]

f = open('{}/gtb_reports/linereport.txt'.format(cwd), 'w')
f.write('# Line\n\n')

conv_dict = {'Hz'  : 1e-6,
             'MHz' : 1,
             'GHz' : 1e+3,
}

axis_dict = {'freq' : 'Frequency',
             'vrad'  : 'Velocity',
}

dpi = 500
vmin, vmax = -2, 2 #endpoints of colourscale in mJy/beam

f = open('{}/gtb_reports/linereport.txt'.format(cwd), 'w')
f.write('# Line\n\n')
f.write('```\n')
f.write('   field rms_expect rms_measur\n')
f.write('         (mJy/beam) (mJy/beam)\n')

'''
READ IN FREQUENCY BINNED CUBE
'''

expected_rms = [[float(rms.split('Natural noise applying flags: median = ')[-1].split()[0]),] for rms in findString(fin, ' CARACal INFO:     Natural noise applying flags: median = ')]
expected_trg = [trg.split('Target #')[-1].split(',')[0].split()[-1] for trg in findString(fin, ' CARACal INFO:   Target #')]
rms = dict(zip(expected_trg, expected_rms))

cols=('r', 'y', 'g', 'c', 'b')
coli=0
for tt in target_name:
  imName = 'output/cubes/cube_2/{}_{}_HI.image.fits'.format(prefix, tt)
  imhdu, wcs, zAxisType, zAxisUnit = cubeRead(imName)
  head = imhdu.header
  cube = imhdu.data
  rms[tt].append(1.4826*np.median(np.abs(cube)))
  f.write('{0:s} {1:10.3f} {2:10.3f}\n'.format(tt,rms[tt][0]*1000,rms[tt][1]*1000))
  plt.plot( head['crval3'] + (np.arange(head['naxis3'])-head['crpix3']+1) * head['cdelt3'], 1.4826*np.median(np.abs(cube)*1000, axis=(1,2)), cols[coli]+'-', label=tt)
  coli += 1

f.write('```\n\n')
f.write('<rms.png>')
f.close()

plt.legend()
plt.xlabel('radio velocity (km/s)')
plt.ylabel('noise (mJy/beam)')
plt.savefig('gtb_reports/rms.png', dpi=dpi)
