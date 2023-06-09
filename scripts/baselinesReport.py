#############################
### START HARDCODED INPUT ###
#############################

# X,Y cartesian position of MeerKAT antennas (ignoring Z)
# Downloaded on 07/10/2020 from
# https://docs.google.com/spreadsheets/d/1T6bqZBnEXMTFqMFCLs221qOvIOTSLHz_oxbI6RE4TrQ/edit#gid=0

antpos={'m000': [-8.264, -207.290],
        'm001': [1.121, -171.762],
        'm002': [-32.113, -224.236],
        'm003': [-66.518, -202.276],
        'm004': [-123.624, -252.946],
        'm005': [-102.088, -283.120],
        'm006': [-18.232, -295.428],
        'm007': [-89.592, -402.732],
        'm008': [-93.527, -535.026],
        'm009': [32.357, -371.056],
        'm010': [88.095, -511.872],
        'm011': [84.012, -352.078],
        'm012': [140.019, -368.267],
        'm013': [236.792, -393.460],
        'm014': [280.669, -285.792],
        'm015': [210.644, -219.142],
        'm016': [288.159, -185.873],
        'm017': [199.624, -112.263],
        'm018': [105.727, -245.870],
        'm019': [170.787, -285.223],
        'm020': [97.016, -299.638],
        'm021': [-295.966, -327.241],
        'm022': [-373.002, 0.544],
        'm023': [-322.306, -142.185],
        'm024': [-351.046, 150.088],
        'm025': [-181.978, 225.617],
        'm026': [-99.004, 17.045],
        'm027': [40.475, -23.112],
        'm028': [-51.179, -87.170],
        'm029': [-88.762, -124.111],
        'm030': [171.281, 113.949],
        'm031': [246.567, 93.756],
        'm032': [461.275, 175.505],
        'm033': [580.678, 863.959],
        'm034': [357.811, -28.308],
        'm035': [386.152, -180.894],
        'm036': [388.257, -290.759],
        'm037': [380.286, -459.309],
        'm038': [213.308, -569.080],
        'm039': [253.748, -592.147],
        'm040': [-26.858, -712.219],
        'm041': [-287.545, -661.678],
        'm042': [-361.714, -460.318],
        'm043': [-629.853, -128.326],
        'm044': [-896.164, 600.497],
        'm045': [-1832.860, 266.750],
        'm046': [-1467.341, 1751.923],
        'm047': [-578.296, -517.297],
        'm048': [-2805.653, 2686.863],
        'm049': [-3605.957, 436.462],
        'm050': [-2052.336, -843.715],
        'm051': [-850.255, -769.359],
        'm052': [-593.192, -1148.652],
        'm053': [9.365, -1304.462],
        'm054': [871.980, -499.812],
        'm055': [1201.780, 96.492],
        'm056': [1598.403, 466.668],
        'm057': [294.645, 3259.915],
        'm058': [2805.764, 2686.873],
        'm059': [3686.427, 758.895],
        'm060': [3419.683, -1840.478],
        'm061': [-16.409, -2323.779],
        'm062': [-1440.632, -2503.773],
        'm063': [-3419.585, -1840.480]}

# Baseline length intervals where to check the fraction of available baselines (in m)
bl_intervals = [0, 50, 100, 200, 400, 1000, 3000, 6000, 9000]

# Minimum fraction of available baselines in the above intervals
# Different projects will have different constraints
minfrac = [0.80, 0.75, 0.75, 0.75, 0.75, 0.75, 0.50, 0.00] # Fornax

###########################
### END HARDCODED INPUT ###
###########################


import os
import numpy as np
import sys

################################
### START COMMAND-LINE INPUT ###
################################

commandline=sys.argv
antall=range(len(antpos))

if '--help' in commandline:
    print('# Run the code as:')
    print('#     python baselines.py [--help]')
    print('#     [--in <comma-separated list of included antennas (integers or mxxx)>]')
    print('#     [--out <comma-separated list of excluded antennas (integers or mxxx)>]')
    print('#     [--plot]')
    sys.exit()
elif '--in' in commandline:
    antsel=list(map(int,commandline[commandline.index('--in')+1].replace('m','').split(',')))
    del(commandline[commandline.index('--in'):commandline.index('--in')+2])
    print('# The following {0:d}/{1:d} antennas have been included in the array:'.format(len(antsel),len(antpos)))
    print('#     {0:}'.format(antsel))
elif '--out' in commandline:
    antsel=list(range(len(antpos)))
    antdel=list(map(int,commandline[commandline.index('--out')+1].replace('m','').split(',')))
    del(commandline[commandline.index('--out'):commandline.index('--out')+2])
    for aa in antdel:
        if aa in antsel:
            del(antsel[antsel.index(aa)])
    print('# The following {0:d}/{1:d} antennas have been removed from the array:'.format(len(antdel),len(antpos)))
    print('#     {0:}'.format(antdel))
else:
    antsel=range(len(antpos))
    print('# All {0:d} antennas have been selected'.format(len(antpos)))

antsel=np.array(['m{0:03d}'.format(jj) for jj in antsel])
antall=np.array(['m{0:03d}'.format(jj) for jj in antall])

if '--plot' in commandline:
    do_plot = True
    del(commandline[commandline.index('--plot')])
else: do_plot = False

##############################
### END COMMAND-LINE INPUT ###
##############################

cwd = os.getcwd()
frep = '{}/obsinfoReport.txt'.format(cwd)

##############################
### START ARRAY EVALUATION ###
##############################

#print('#')
#print('# Hardcoded minimum fraction of available baselines as a function of baseline length:')
#for ii in range(len(bl_intervals)-1):
#    print('# {0:4d} - {1:4d} m: {2:3.0f}%'.format(bl_intervals[ii],bl_intervals[ii+1],100*minfrac[ii]))
#print('#')

# baseline length histogram for full array
xyall=np.array([antpos[jj] for jj in antall]).astype(float)
baselines_all=[]
for ii in range(antall.shape[0]):
    for jj in range(ii+1,antall.shape[0]):
        baselines_all.append(np.sqrt(((xyall[ii]-xyall[jj])**2).sum()))
baselines_all=np.array(baselines_all)

# baseline length histogram for selected array
xysel=np.array([antpos[jj] for jj in antsel]).astype(float)
baselines_sel=[]
for ii in range(antsel.shape[0]):
    for jj in range(ii+1,antsel.shape[0]):
        baselines_sel.append(np.sqrt(((xysel[ii]-xysel[jj])**2).sum()))
baselines_sel=np.array(baselines_sel)

nrs_sel = [((baselines_sel >= bl_intervals[ii])*(baselines_sel < bl_intervals[ii+1])).sum() for ii in range(len(bl_intervals)-1)]
nrs_all = [((baselines_all >= bl_intervals[ii])*(baselines_all < bl_intervals[ii+1])).sum() for ii in range(len(bl_intervals)-1)]

f = open(frep, 'a')

f.write('```\n')    

f.write('# Fraction of available baselines as a function of baseline length:\n')
for ii in range(len(bl_intervals)-1):
    if round(float(nrs_sel[ii])/float(nrs_all[ii]), 2)<minfrac[ii]: flag = '!!! NOT OK !!!'
    else: flag = 'OK'
    f.write('# {3:4d} - {4:4d} m: {0:3d} / {1:3d} = {2:3.0f}% -- {5:s}\n'.format(nrs_sel[ii],
          nrs_all[ii],100*nrs_sel[ii]/nrs_all[ii],bl_intervals[ii],bl_intervals[ii+1],flag))

f.write('```\n')    

f.close()    
#print('# The ten shortest baselines have length {0:} metres'.format(np.sort(baselines)[:10]))

##############################
### END ARRAY EVALUATION ###
##############################



############################
### START ARRAY PLOTTING ###
############################

if do_plot:
    from matplotlib import pyplot as pl
    # Show array layout
    pl.figure(figsize=(14,6))
    pl.subplot(121)
    for aa in antall: pl.plot(antpos[aa][0],antpos[aa][1],'ko',mfc='none',mec='k')
    for aa in antsel: pl.plot(antpos[aa][0],antpos[aa][1],'ko',mfc='k',mec='k')
    pl.xlim(-4000,4000)
    pl.ylim(-4000,4000)
    pl.xlabel('X (m)')
    pl.ylabel('Y (m)')

    # Show baseline length distribution
    pl.subplot(122)
    pl.hist(baselines_all,bins=range(0,8000,50),histtype='step',color='k')
    pl.hist(baselines_sel,bins=range(0,8000,50),color='k')
    pl.xlabel('baseline length (m)')
    pl.ylabel('nr baselines')
    #pl.hist(baselines,bins=range(0,8000,50),color='k')
    pl.show()

##########################
### END ARRAY PLOTTING ###
##########################
