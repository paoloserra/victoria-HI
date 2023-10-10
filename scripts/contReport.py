from matplotlib import pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from astropy.nddata import Cutout2D
from astropy.coordinates import SkyCoord
import numpy as np
import glob

imgs = sorted(glob.glob('output/continuum/image_3/*_virgo???_3-MFS-image.fits'))
ress = [jj.replace('-image.fits', '-residual.fits') for jj in imgs]
mods = [jj.replace('-image.fits', '-model.fits') for jj in imgs]
bads = [jj.replace('/image_3/', '/image_0/').replace('_3-MFS-', '_0-MFS-') for jj in imgs]
flds = [jj.split('virgo')[1][:3] for jj in imgs]

vmin, vmax = -1e-4, 1e-3

f = open('gtb_reports/cont.txt', 'w')
f.write('## Continuum\n\n')
f.write('Noise levels:\n\n')

for ii in range(len(flds)):
  fld = flds[ii]
  with fits.open(imgs[ii]) as fts:
    img  = fts[0].data
    head = fts[0].header
  with fits.open(ress[ii]) as fts:
    res  = fts[0].data
  with fits.open(mods[ii]) as fts:
    mod  = fts[0].data
  with fits.open(bads[ii]) as fts:
    bad  = fts[0].data
  if head['naxis'] == 4:
    img, res, mod, bad = img[0], res[0], mod[0], bad[0]
    head['naxis'] = 3
    del(head['naxis4'])
    del(head['crval4'])
    del(head['crpix4'])
    del(head['cdelt4'])
    del(head['cunit4'])
    del(head['ctype4'])
  if head['naxis'] == 3:
    img, res, mod, bad = img[0], res[0], mod[0], bad[0]
    head['naxis'] = 2
    del(head['naxis3'])
    del(head['crval3'])
    del(head['crpix3'])
    del(head['cdelt3'])
    del(head['cunit3'])
    del(head['ctype3'])
  wcs = WCS(head)

  crn = int(np.floor(head['naxis1']/4))
  noise1 = np.nanmedian(np.abs(res[:crn, :crn]))
  noise2 = np.nanmedian(np.abs(res[3*crn:4*crn, :crn]))
  noise3 = np.nanmedian(np.abs(res[:crn, 3*crn:4*crn]))
  noise4 = np.nanmedian(np.abs(res[3*crn:4*crn, 3*crn:4*crn]))
  noise = np.mean(np.array([noise1, noise2, noise3, noise4]))
  f.write('- virgo{0} : {1:.1e} Jy/beam\n'.format(fld, noise))

  centre = SkyCoord(head['crval1'], head['crval2'], unit='deg')
  size   = (head['naxis1']/2, head['naxis2']/2)
  img = Cutout2D(img, centre, size, wcs=wcs)
  res = Cutout2D(res, centre, size, wcs=wcs)
  mod = Cutout2D(mod, centre, size, wcs=wcs)
  bad = Cutout2D(bad, centre, size, wcs=wcs)

  fig = plt.figure(figsize=(9,8))
  fig.subplots_adjust(left=0.12, bottom=0.07, right=0.99, top=0.95, wspace=0.3, hspace=0.3)

  ax1 = plt.subplot(221, projection=img.wcs)
  ax1.imshow(bad.data, vmin=vmin, vmax=vmax)
  ax1.set_title('virgo{} - before selfcal'.format(fld))
  ax1.set_xlabel('RA(J2000)')
  ax1.set_ylabel('Dec(J2000)')

  ax2 = plt.subplot(222, projection=img.wcs)
  ax2.imshow(img.data, vmin=vmin, vmax=vmax)
  ax2.set_title('virgo{} - after selfcal'.format(fld))
  ax2.set_xlabel('RA(J2000)')
  ax2.set_ylabel('Dec(J2000)')

  ax3 = plt.subplot(223, projection=img.wcs)
  ax3.imshow(res.data, vmin=vmin, vmax=vmax)
  ax3.set_title('virgo{} - residual'.format(fld))
  ax3.set_xlabel('RA(J2000)')
  ax3.set_ylabel('Dec(J2000)')

  ax4 = plt.subplot(224, projection=img.wcs)
  ax4.imshow(img.data, vmin=vmin, vmax=vmax)
  ax4.contour(mod.data, levels=[-1e-10, 1e-10], colors=['r', 'w'])
  ax4.set_title('virgo{} - model'.format(fld))
  ax4.set_xlabel('RA(J2000)')
  ax4.set_ylabel('Dec(J2000)')

  plt.savefig('gtb_reports/cont_virgo{}.png'.format(fld), dpi=300)

f.write('\n')
for fld in flds:
  f.write('<cont_virgo{}.png>\n'.format(fld))
f.close()
