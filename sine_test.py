from WF_SDK import device, scope, wavegen, tools, error  # WaveForms SDK Libraries
# Generating BE Waveforms
from BandExcitation.Measurement.BEMeasurement import BEWaveform, BE_Spectroscopy
from BandExcitation.Viz.Waveform import BE_Viz
import matplotlib.pyplot as plt  # Plotting
import numpy as np

try:
    # Connect to device
    device_data = device.open(config=0)

    # Generate band excitation waveform
    BEppw = 2**14
    BErep = 1
    # BEdata = BEWaveform(BEppw, BErep)
    BEdata = BE_Spectroscopy(BEppw, BErep, type="switching spectroscopy", max=3.5, min=-3.5, start=0, cycles=2, points_per_cycle=96,
                             center_freq=500e3, bandwidth=60e3, wave="chirp", waveform_time=4e-3, BE_smoothing=125, chirp_direction="up",
                             measurement_state="on and off", measurement_state_offset=0)

    # Enable triggering on scope ch1
    # scope.trigger(device_data, enable=True, source=scope.trigger_source.analog,
    #              channel=1, level=0.1, horizontalpos=0.445*BEdata.cantilever_excitation_time)

    # Generate a waveform from data points
    wavegen.generate(device_data, channel=1, function=wavegen.function.play, offset=0, frequency=BEdata.AO_rate,
                     data=BEdata.cantilever_excitation_waveform, run_time=BEdata.cantilever_excitation_time, wait=0, repeat=1)

    # Reset the function generator
    wavegen.close(device_data)

    # Close the device connection
    device.close(device_data)

except error as e:
    print(e)

    # Close the device connection
    device.close(device.data)
