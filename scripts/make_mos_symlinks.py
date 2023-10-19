import os
import sys
import glob

im_type = [
           'image',
           'pb',
           'model',
           'residual',
           ]

base_dir   = '/scratch/usd/pserra/Astro/virgo/meerkat/datareduction'
cube_dir   = 'output/cubes/cube_1'
prefix     = 'oct'
mos_in_dir = '{0:s}/mosaics/mos_input'.format(base_dir)

cubes = sorted(glob.glob('{0:s}/*/{1:s}/{2:s}_virgo???_HI.image.fits'.format(base_dir, cube_dir, prefix)))

for cc in cubes:
  for tp in im_type:
    cube = cc.replace('.image.fits', '.{0:s}.fits'.format(tp))
    bsnm = os.path.basename(cube)
    link = '{0:s}/{1:s}'.format(mos_in_dir, bsnm)
    print('  {0:s}'.format(cube))
    os.symlink(cube, link)
