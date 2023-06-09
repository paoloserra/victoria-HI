# victoria-HI

HI data reduction for the ViCTORIA project.

### data download

<img width="1438" alt="virgo_export" src="https://github.com/paoloserra/victoria-HI/assets/6591265/63831f9d-e736-4cbb-b10f-4b59b854ada9">

### data reduction

```
cd /home/pserra/Astro/virgo/meerkat/data_reduction/<MS-id>
mkdir -p input
cp /home/pserra/Astro/virgo/meerkat/brightHIcat.txt input/.
caracal -c xcal.yml
python3.7 /home/pserra/Astro/virgo/meerkat/victoria-HI/scripts/calflagstats.py
caracal -c calflag.yml
python3.7 /home/pserra/Astro/virgo/meerkat/victoria-HI/scripts/targetflagstats.py
caracal -c cont.yml
caracal -c line.yml
