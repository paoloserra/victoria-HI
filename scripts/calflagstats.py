flagfracthr = 20 # percentage beyond which an alert is raised

import yaml
import os
import glob

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
