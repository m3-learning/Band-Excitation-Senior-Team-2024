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
    BEppw = 2**13
    BErep = 1
    # BEdata = BEWaveform(BEppw, BErep)
    BEdata = BE_Spectroscopy(BEppw, BErep, type="switching spectroscopy", max=4, min=-4, start=0, cycles=2, points_per_cycle=96,
                             center_freq=800e3, bandwidth=10e3, wave="chirp", waveform_time=4e-3, BE_smoothing=125, chirp_direction="up",
                             measurement_state="on and off", measurement_state_offset=0)

    '''
    plt.plot(BEdata.BE_wave)
    plt.title("Input Signal (Band Excitation)")
    plt.xlabel("Points")
    plt.ylabel("Voltage [V]")
    plt.show()
    plt.plot(BEdata.cantilever_excitation_waveform)
    plt.title("Input Signal (Cantilever Excitation Waveform)")
    plt.xlabel("Points")
    plt.ylabel("Voltage [V]")
    plt.show()

    # Initialize oscilloscope with default settings
    samplefreq = 4e6
    numberofperiods = 1
    # waveform time * sampling period * number of periods
    buffersize = int(BEdata.cantilever_excitation_time *
                     samplefreq * numberofperiods)
    scope.open(device_data, sampling_frequency=samplefreq,
               buffer_size=buffersize)

    # Enable triggering on scope ch1
    # scope.trigger(device_data, enable=True, source=scope.trigger_source.analog,
    #              channel=1, level=0.1, horizontalpos=0.445*BEdata.cantilever_excitation_time)
    '''
    # Generate a waveform from data points
    wavegen.generate(device_data, channel=1, function=wavegen.function.play, offset=0, frequency=BEdata.AO_rate,
                     data=BEdata.cantilever_excitation_waveform, run_time=BEdata.cantilever_excitation_time, wait=0, repeat=1)
    '''
    # Record data on ch1
    buffer = scope.record(device_data, channel=1)

    # Create array for time scale
    timescale = []
    for n in range(len(buffer)):
        # convert time in ms
        timescale.append((n * 1e3) / scope.data.sampling_frequency)

    # Plot recorded data
    plt.plot(timescale, buffer)
    plt.title("Output Signal")
    plt.xlabel("Time [ms]")
    plt.ylabel("Voltage [V]")
    plt.show()
    '''
    '''
    # Compute the spectrum
    start_frequency = BEdata.center_freq - (BEdata.bandwidth * 1.5)
    stop_frequency = BEdata.center_freq + (BEdata.bandwidth * 1.5)
    spectrum = tools.spectrum(buffer, tools.window.rectangular, scope.data.sampling_frequency, start_frequency, stop_frequency)

    # Calculate frequency domain data
    frequency = []
    spectrumlength = len(spectrum)
    step = (stop_frequency - start_frequency) / (spectrumlength - 1)
    for n in range(spectrumlength):
        frequency.append((start_frequency + n * step) / 1e03) # convert frequency in kHz
        
    # Plot spectrum
    plt.plot(frequency, spectrum)
    plt.title("Spectrum Analysis")
    plt.xlabel("Frequency [kHz]")
    plt.ylabel("Magnitude [dBV]")
    plt.show()
    '''

    # Viz = BE_Viz(BEdata)
    # Viz.plot_fft(x_range=[400e3, 600e3])

    # Reset the oscilloscope
    # scope.close(device_data)

    # Reset the function generator
    wavegen.close(device_data)

    # Close the device connection
    device.close(device_data)

except error as e:
    print(e)

    # Close the device connection
    device.close(device.data)
