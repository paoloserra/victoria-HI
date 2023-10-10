#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --job-name='xcal'
#SBATCH --cpus-per-task=32
#SBATCH --mem=220GB
#SBATCH --output=sbatch_logs/xcal-%j-out.log
#SBATCH --error=sbatch_logs/xcal-%j-err.log
#SBATCH --time=72:00:00
#SBATCH --mail-user=paolo.serra@inaf.it
#SBATCH --mail-type=END,FAIL

now=$(date)
echo "Submitting single node SLURM job"
echo "Running on node $HOSTNAME"
echo "Current time is: $now"

mkdir -p input
cp /home/pserra/victoria-HI/caracal_config/brightHIcat.txt input/.
mkdir -p gtb_reports

export SINGULARITY_CACHEDIR=/scratch/usd/pserra/.singularity_cache
export SINGULARITY_TMPDIR=/scratch/usd/pserra/.singularity_tmp
export SINGULARITY_LOCALCACHEDIR=/scratch/usd/pserra/.singularity_localcache

source /home/floi/stimela_venv/bin/activate
caracal -c xcal.yml -sid /home/floi/singularity_images
python /home/pserra/victoria-HI/scripts/calflagstats.py
deactivate

chmod -R g+w .

# Check that the caracal log exists
if [ ! -f output/log-caracal.txt ]; then
  echo "CARACal log not found!"
  now=$(date)
  echo "Current time is: $now"
  exit 1
fi

# Check if the pipeline completed or crashed
string=$(tail -1 output/log-caracal.txt)
if [[ $string == *"error code 1"* ]]; then
  echo "CARACal crashed :("
  now=$(date)
  echo "Current time is: $now"
  exit 1
else
  echo "CARACal finished successfully! Huzzah!!"
  now=$(date)
  echo "Current time is: $now"
fi
