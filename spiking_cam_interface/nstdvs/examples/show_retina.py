import nstdvs
import time
import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wavfile
from scipy.signal import lfilter
from subprocess import check_call
import sys
import os
import wave
import pyaudio

def readHRTF(name):
    r = np.fromfile(file(name, 'rb'), np.dtype('>i2'), 256)
    r.shape = (128,2)
    # half the rate to 22050 and scale to 0 -> 1
    r = r.astype(float)
    # should use a better filter here, this is a box lowering the sample rate from 44100 to 22050
    r = (r[0::2,:] + r[1::2,:]) / 65536
    return r


# encode the values in the [-1 1]
def tracker():
    dvs = np.array(dvs_brd.get_frequency_info(0))
    dvs[np.isnan(dvs)]=np.zeros(len(dvs[np.isnan(dvs)]))
    xpos = dvs[0] # stimulus on x axis will be used in azimuth mapping
    ypos = dvs[1] # stimulus on y axis will be used in elevation mapping
    prob = dvs[2] # likelihood that it is the stimulus as a way to filter
    return [xpos, ypos, prob]

# initialize vision subsystem
dvs_brd = nstdvs.DVSBoard()
dvs_brd.connect(nstdvs.Serial('/dev/ttyUSB0', baud=12000000))
time.sleep(1)
# enable the tracker
dvs_brd.track_frequencies([500])
# enable the data acquisition
dvs_brd.retina(True)
dvs_brd.show_image()

# initialize the audio system
# recode the sound to mono and 22050
check_call(['sox', 'outsnap.wav', '-r', '22050', '-c1', '-b', '16', 'inp.wav'])
# read the input
rate, mono_sound = wavfile.read(file('inp.wav', 'rb'))
# remove that tmp file
os.remove('inp.wav')

# check the mode {pre-recorded or on-the-fly HRTF}
prerecorded = 1

while True:
    # enable py audio interface
    p = pyaudio.PyAudio()
    # get the position of the tracked stimulus
    target_stim = np.array(tracker())
    # interpolate and map to sound resolution
    snd = np.interp(target_stim[0], [-1,1], [-90, 90])
    resolution = 5
    snd -=snd%resolution

    # check the operation mode (pre-recorded soundscape or on-the-fly)
    if prerecorded == 0:
        sound = wave.open(file(os.path.join('soundscape', 'a%d.wav' % snd), 'rb'))
        stream = p.open(format=p.get_format_from_width(sound.getsampwidth()),
                    channels=sound.getnchannels(),
                    rate=sound.getframerate(),
                    output=True)

        data = sound.readframes(1024)

        while len(data) > 0:
            stream.write(data)
            data = sound.readframes(1024)

        stream.stop_stream()
        stream.close()
    else:
        # choose the desired HRTF depending on the location on x axis (azimuth)
        hrtf = readHRTF(os.path.join('elev0', 'H0e%03da.dat' % np.abs(snd)))
        # apply the filter
        left = lfilter(hrtf[:,1], 1.0, mono_sound)
        right = lfilter(hrtf[:,0], 1.0, mono_sound)
        # combine the channels
        result = np.array([left, right]).T.astype(np.int16)
        # separate the sides
        result_pos = result
        result_neg = result[:, (1, 0)]
        # intermediate buffer for replay
        wavfile.write('out.wav', rate, result_pos)
        check_call(['sox', 'out.wav', 'out_pos.wav'])
        wavfile.write('out.wav', rate, result_neg)
        check_call(['sox', 'out.wav', 'out_neg.wav'])
        # check where in the FOV we focus
        if snd < 0:
            sound = wave.open('out_pos.wav','rb')
        else:
            sound = wave.open('out_neg.wav','rb')
        # open the stream for replay
        stream = p.open(format=p.get_format_from_width(sound.getsampwidth()),
                        channels=sound.getnchannels(),
                        rate=sound.getframerate(),
                        output=True)
        # read the data frames
        data = sound.readframes(1024)

        while len(data) > 0:
            stream.write(data)
            data = sound.readframes(1024)

        stream.stop_stream()
        stream.close()
    # terminate the session
    p.terminate()
    time.sleep(0.001)
