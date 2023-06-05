# victoria-HI

HI data reduction for the ViCTORIA project.

### data download

...

### data reduction

```
cd /home/pserra/Astro/virgo/meerkat/data_reduction/<MS-id>
caracal -c xcal.yml
python3.7 /home/pserra/Astro/virgo/meerkat/victoria-HI/scripts/flagstats.py
