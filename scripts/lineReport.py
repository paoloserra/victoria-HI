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

f.write('```\n')
f.close()
plt.legend()
plt.xlabel('radio velocity (km/s)')
plt.ylabel('noise (mJy/beam)')
plt.savefig('gtb_reports/rms.png', dpi=dpi)
exit()


'''
MAKE XY CUBE CENTRAL FREQ/VELO CROSS-SECT
'''

dpi = 500
vmin, vmax = -0.4, 0.4 #endpoints of colourscale in mJy/beam

fcut = int(imhdu.data.shape[0]/2)

ax = plt.subplot(projection=wcs, slices=('x', 'y', fcut))
fq = ax.coords[2]
fq.set_axislabel('')
fq.set_ticks_visible(False)
fq.set_ticklabel_visible(False)

img = ax.imshow(imhdu.data[fcut,:,:]*1e+3, origin='lower', vmin=vmin, vmax=vmax)
plt.colorbar(img, ax=ax, label='Flux density [mJy/beam]', pad = 0.01)

plt.xlabel('RA [J2000]')
plt.ylabel('Dec [J2000]')

plt.title('mfs{}, track{}, 103 km/s \n HI cube channel map at central {}'.format(pointingID, trackNr, axis_dict[zAxisType].lower()))

xyName_lr = imName.replace('.fits','_XY.png')
plt.savefig('{}/mfs_report_track{}/{}'.format(cwd, trackNr, xyName_lr), dpi = dpi)

'''
READ IN CUBE
'''

imName = 'track{}_mfs{}_HI_lwstack.image.fits'.format(trackNr,pointingID)
imhdu, wcs, zAxisType, zAxisUnit = cubeRead(imName)

vmin, vmax = -2, 2 #endpoints of colourscale in mJy/beam

'''
MAKE XY CUBE CENTRAL FREQ/VELO CROSS-SECT
'''

dcut = int(imhdu.data.shape[0]/2)

ax = plt.subplot(projection=wcs, slices=('x', 'y', dcut))
fq = ax.coords[2]
fq.set_axislabel('')
fq.set_ticks_visible(False)
fq.set_ticklabel_visible(False)

img = ax.imshow(imhdu.data[dcut,:,:]*1e+3, origin='lower', vmin=vmin, vmax=vmax)
plt.colorbar(img, ax=ax, label='Flux density [mJy/beam]', pad = 0.01)

plt.xlabel('RA [J2000]')
plt.ylabel('Dec [J2000]')

plt.title('mfs{}, track{} \n HI cube channel map at central {}'.format(pointingID, trackNr, axis_dict[zAxisType].lower()))

xyName = imName.replace('.fits','_XY.png')
plt.savefig('{}/mfs_report_track{}/{}'.format(cwd, trackNr, xyName), dpi = dpi)

'''PLOT CHANNEL WITH POTENTIAL SOURCE'''

sumPerChan = np.nansum(imhdu.data, axis = (1,2))
maxChan = np.argmax(sumPerChan)

fcut = int(maxChan)

ax = plt.subplot(projection=wcs, slices=('x', 'y', fcut))
fq = ax.coords[2]
fq.set_axislabel('')
fq.set_ticks_visible(False)
fq.set_ticklabel_visible(False)

img = ax.imshow(imhdu.data[fcut,:,:]*1e+3, origin='lower', vmin=vmin, vmax=vmax)
plt.colorbar(img, ax=ax, label='Flux density [mJy/beam]', pad = 0.01)

plt.title('mfs{}, track{} \n HI cube channel map with a source candidate'.format(pointingID, trackNr))

plt.xlabel('RA [J2000]')
plt.ylabel('Dec [J2000]')

xySouName = imName.replace('.fits','_XY_SourceCandidate.png')
plt.savefig('{}/mfs_report_track{}/{}'.format(cwd, trackNr, xySouName), dpi = dpi)

'''
MAKE XZ CUBE CROSS-SECT
'''

dcut = int(imhdu.data.shape[-1]/2)

ax = plt.subplot(projection=wcs, slices=('x', dcut, 'y'))

dec = ax.coords[1]
dec.set_axislabel('')
dec.set_ticks_visible(False)
dec.set_ticklabel_visible(False)

img = ax.imshow(imhdu.data[:,dcut,:]*1e+3, origin='lower', vmin=vmin, vmax=vmax)
plt.colorbar(img, ax=ax, label='Flux density [mJy/beam]', pad = 0.01)

#ax.set_aspect('0.2')

plt.xlabel('RA [J2000]')
plt.ylabel('{} [{}]'.format(axis_dict[zAxisType],zAxisUnit))

plt.title('mfs{}, track{} \n HI cube cross section at central declination'.format(pointingID, trackNr))

xzName = imName.replace('.fits','_XZ.png')
plt.savefig('{}/mfs_report_track{}/{}'.format(cwd, trackNr, xzName), dpi = dpi)

'''
GET MEASURED RMS PRODUCED BY PLOTRMS.PY
'''

frms = open('tempRMS.txt', 'r')
temp = frms.readlines()
frms.close()

rmsMeasFullRes = float(temp[0].split(',')[0])*1e3
rmsMeasLowRes = float(temp[0].split(',')[1])*1e3

os.remove('tempRMS.txt')

'''
EXTRACT EXPECTED RMS FROM LOGFILE
'''

def pickLog(logs):
    global trackNr, cwd
    for log in logs:
        obsInfo = findString('{}/{}/log-caracal.txt'.format(cwd,log), 'CARACal INFO:')
        t = pickLine(obsInfo, 'prefix:')
        pref = t[0].split()[-1]
        ind = pref.find('track')
        trck = pref[ind+5]
        if trck != trackNr:
            continue

        fin = ''
        ln = findString('{}/{}/log-caracal.txt'.format(cwd, log),
                        'applying flags: median')

        if len(ln) > 0:
            r = log
            break

    return r


tmp = []
for nr, log in enumerate(logLs):
    if len(sys.argv) < 3:
        sortedLwLogs = orderedLogs('output_lw1{}'.format(nr))
        sortedLwLogs = ['output_lw1{}/'.format(nr) + s for s in sortedLwLogs]
        log = pickLog(sortedLwLogs)

    fin = '{}/output_lw1{}/{}/log-caracal.txt'.format(cwd,nr,log.split('/')[-1])

    ln = findString(fin, 'applying flags: median')

    tmp.append(float(between(ln[0], 'median = ', ' Jy/beam, range'))*1e3) #in mJy

rmsExpected = np.median(np.asarray(tmp))
f.write('- Expected noise: {:.3f} mJy/beam (from `output_lw??/log-caracal.txt` of lw10, 11, 12, 13, scaled by 1.5/sqrt(3))\n'.format(rmsExpected/np.sqrt(3)*1.5))

f.write('- Measured noise: {:.3f} mJy/beam (median value from `MFS-data-reduction/miscellaneous_scripts/plotrms.py`)\n'.format(rmsMeasFullRes))

f.write('- Measured noise in low-res cube: {:.3f} mJy/beam\n\n'.format(rmsMeasLowRes))

f.write('<mfs_report_track{}/{}>\n\n'.format(trackNr,
                                             'track{1:s}_mfs{0:s}_HI_lwstack_rms.png'.format(
                                                 pointingID,trackNr)))

f.write('<mfs_report_track{}/{}>\n\n'.format(trackNr,
                                             'lr_track{1:s}_mfs{0:s}_HI_lwstack_rms.png'.format(
                                                 pointingID,trackNr)))

f.write('<mfs_report_track{}/{}>\n\n'.format(trackNr, xyName))

f.write('<mfs_report_track{}/{}>\n\n'.format(trackNr, xySouName))

f.write('<mfs_report_track{}/{}>\n\n'.format(trackNr, xzName))

f.write('<mfs_report_track{}/{}>\n\n'.format(trackNr, xyName_lr))

f.close()
