# Repository for the Hack the Senses Hackaton 2016 #

## Hearing motion synesthesia ##

DONE:

Using spiking cameras to capture motion and generate audio information for triggering synesthesia in blind.

* basic interface to acquire spikes from a single camera
* algorithm for tracking "labels" in visual space (i.e. LED @ different frequencies) and provide position in 2 D visual field and probability (confidence) depending on the distance
* code the position and distance of the "labels" into 3D sound (azimuth, elevation from direct 2D visual field and volume for depth (confidence))

WIP:

* extend the principle to 2 cameras and update depth computation
* use Nengo as simulator to implement a neurally plausible spiking neural network