import nstdvs
import time

# test scenario
brd1 = nstdvs.DVSBoard()
brd1.connect(nstdvs.Serial('/dev/ttyUSB1', baud=12000000))

time.sleep(1)

# enable the data acquisition
brd1.retina(True)
brd1.show_image()

# if trackinug is used parametrize the spike tracker and
# make sure the LED freq is set
# you can choose to split the FOV for different frequencies
# brd1.track_spike_rate(all=(0, 0, 128, 128))
# left=(0,0,64,128),
# right=(64,0,128,128))
# you can track multiple frequencies in the same event stream
# brd1.track_frequencies(freqs=[40, 50, 60])

while True:
    time.sleep(1)
