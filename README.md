# victoria-HI

HI data reduction for the ViCTORIA project.

### data download

<img width="1440" alt="virgo_export" src="https://github.com/paoloserra/victoria-HI/assets/6591265/9ebbd8fa-4a27-4d92-991d-6fbea69c9bd4">

### data reduction

```
cd /home/pserra/Astro/virgo/meerkat/data_reduction/<MS-id>
caracal -c xcal.yml
python3.7 /home/pserra/Astro/virgo/meerkat/victoria-HI/scripts/flagstats.py
