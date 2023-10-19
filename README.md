# victoria-HI

HI data reduction for the ViCTORIA project.

### data download

<img width="1438" alt="virgo_export" src="https://github.com/paoloserra/victoria-HI/assets/6591265/63831f9d-e736-4cbb-b10f-4b59b854ada9">

### data reduction on the OAC cluster

## 1. Single observation
```
mkdir -p /scratch/usd/pserra/Astro/virgo/meerkat/datareduction/<MS-id>
cd /scratch/usd/pserra/Astro/virgo/meerkat/datareduction/<MS-id>
mkdir sbatch_logs
cp /home/pserra/victoria-HI/caracal_config/*.yml .
cp /home/pserra/victoria-HI/caracal_config/*.sbatch .
[edit <MS-id> in .yml files]
nano *.yml
caracal -c xcal.yml
caracal -c calflag.yml
caracal -c cont.yml
caracal -c line.yml
```

## 2. Mosaic
```
rm /scratch/usd/pserra/Astro/virgo/meerkat/datareduction/mosaics/mos_input/*.fits
python /home/pserra/victoria-HI/scripts/make_mos_symlinks.py
cd /scratch/usd/pserra/Astro/virgo/meerkat/datareduction/mosaics
sbatch mos.sbatch
```
