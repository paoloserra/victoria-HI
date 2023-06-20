flagfracthr = 20 # percentage beyond which an alert is raised

import yaml
import os
import glob

obsinfofile = '{0:s}/output/log-caracal.txt'.format(os.getcwd())
start_record = 0

for ll in open(obsinfofile).readlines():
  if 'CARACal INFO: obsconf: running' in ll:
    break
  if ' CARACal INFO: MS #0:' in ll:
    start_record = 1
    goodlines = []
  if start_record:
    goodlines.append(ll)

g = open('{0:s}/gtb_reports/obsinfo.txt'.format(os.getcwd()), 'w')
g.write('## Obsinfo\n\n')
g.write('```\n')
for ll in goodlines:
  g.write(ll.split(' CARACal INFO: ')[-1])
g.write('```\n')
g.write('\n')
g.write('<elevation plot>')
g.close()

flagstatsfiles = glob.glob('{0:s}/output/diagnostic_plots/*cal*.json'.format(os.getcwd()))
flagstatsfiles.sort(key=lambda x: os.path.getmtime(x))

os.system('mkdir -p {0:s}/gtb_reports'.format(os.getcwd()))
g = open('{0:s}/gtb_reports/calflagstats.txt'.format(os.getcwd()), 'w')
g.write('## Calibrators flagged fraction\n\n')

for ff in flagstatsfiles:
  g.write('*{0:s}*\n'.format(os.path.basename(ff)))
  with open(ff,) as flagstatsfile:
    flagstats = yaml.load(flagstatsfile, yaml.SafeLoader)['Flag stats']

  scans = flagstats[0]['scans']
  antennas = flagstats[1]['antennas']
  fields = flagstats[2]['fields']
  corrs = flagstats[3]['corrs']

  g.write('```\n')
  g.write('FIELDS\n')
  field_names = list(fields.keys())
  field_names.sort()
  for fld in field_names:
    flagfrac = fields[fld]['frac']*100
    g.write('  {0:s} = {1:.1f}%'.format(fields[fld]['name'], flagfrac))
    if flagfrac >= flagfracthr:
      g.write(' !!! \n')
    else:
      g.write('\n')
  g.write('```\n')
  g.write('\n')

  g.write('```\n')
  g.write('ANTENNAS wth flagged fraction > {0:d}%\n'.format(flagfracthr))
  antenna_names = list(map(int,list(antennas.keys())))
  antenna_names.sort()
  nrantalarm = 0
  for ant in antenna_names:
    flagfrac = antennas[str(ant)]['frac']*100
    if flagfrac >= flagfracthr:
      nrantalarm += 1
      g.write('  {0:s} = {1:.1f}% !!! \n'.format(antennas[str(ant)]['name'], flagfrac))
  if not nrantalarm:
    g.write('  (none)\n')
  g.write('```\n')
  g.write('\n')

g.close()

os.system('cp {0:s}/msdir/??????????_sdp_l0-elevation-tracks.png {0:s}/gtb_reports/.'.format(os.getcwd()))
os.system('cp {0:s}/output/diagnostic_plots/crosscal/*_sdp_l0-1gc_primary.K1.png {0:s}/gtb_reports/.'.format(os.getcwd()))
os.system('cp {0:s}/output/diagnostic_plots/crosscal/*_sdp_l0-1gc_primary.B1.png  {0:s}/gtb_reports/.'.format(os.getcwd()))
os.system('cp {0:s}/output/diagnostic_plots/crosscal/*_sdp_l0-1gc_secondary.F0.png {0:s}/gtb_reports/.'.format(os.getcwd()))
os.system('cp {0:s}/output/diagnostic_plots/1gc/*_sdp_l0-cal-J1939-6342-CORRECTED_DATA-??-*-FREQ.png {0:s}/gtb_reports/.'.format(os.getcwd()))
os.system('cp {0:s}/output/diagnostic_plots/1gc/*_sdp_l0-cal-J1150-0023-CORRECTED_DATA-??-imag-real.png {0:s}/gtb_reports/.'.format(os.getcwd()))
