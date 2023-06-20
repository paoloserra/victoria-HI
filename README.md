# victoria-HI

HI data reduction for the ViCTORIA project.

### data download

<img width="1438" alt="virgo_export" src="https://github.com/paoloserra/victoria-HI/assets/6591265/63831f9d-e736-4cbb-b10f-4b59b854ada9">

### data reduction

```
source /home/pserra/Astro/caracal-venv-3.7/bin/activate
mkdir -p /home/pserra/Astro/virgo/meerkat/data_reduction/<MS-id>
cd /home/pserra/Astro/virgo/meerkat/data_reduction/<MS-id>
mkdir -p input
cp /home/pserra/Astro/virgo/meerkat/brightHIcat.txt input/.
cp /home/pserra/Astro/virgo/meerkat/victoria-HI/caracal_config/*.yml .
[edit <MS-id> in .yml files]
caracal -c xcal.yml
python3.7 /home/pserra/Astro/virgo/meerkat/victoria-HI/scripts/calflagstats.py
caracal -c calflag.yml
python3.7 /home/pserra/Astro/virgo/meerkat/victoria-HI/scripts/targetflagstats.py
caracal -c line.yml
python3.7 /home/pserra/Astro/virgo/meerkat/victoria-HI/scripts/lineReport.py
[when done free up disc space]
rm -rf msdir/??????????_sdp_l0-cal.ms*
rm -rf msdir/??????????_sdp_l0-virgo???-corr.ms*
```
