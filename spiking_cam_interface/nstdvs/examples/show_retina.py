import nstdvs
import time
import numpy as np

# test scenario
dvs_brd = nstdvs.DVSBoard()
dvs_brd.connect(nstdvs.Serial('/dev/ttyUSB0', baud=12000000))
time.sleep(1)
# enable the tracker
dvs_brd.track_frequencies([50])

# encode the values in the [-1 1]
def tracker():
    dvs = np.array(dvs_brd.get_frequency_info(0))
    dvs[np.isnan(dvs)]=np.zeros(len(dvs[np.isnan(dvs)]))
    xpos = dvs[0] # stimulus on x axis
    ypos = dvs[1] # stimulus on y axis
    prob = dvs[2] # likelihood that it is the stimulus
    return [xpos, ypos, prob]

# enable the data acquisition
dvs_brd.retina(True)
dvs_brd.show_image()

while True:
    print tracker()
    time.sleep(0.5)
