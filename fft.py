import matplotlib.pyplot as plt
from WF_SDK import device, scope, wavegen, tools, error  # WaveForms SDK Libraries
import numpy as np

# Load the binary file
file_path = 'C:/Users/DrewT/Downloads/5-16-24-Test7.bin'  # Update with your file path
with open(file_path, 'rb') as f:
    # Assuming the data in the binary file is int16
    data = np.fromfile(f, dtype=np.int16)

# Define the sampling frequency
Fs = 4e6  # Update with your actual sampling frequency in Hz

# Time domain data
time = np.arange(len(data)) / Fs

# Plot time domain data
plt.figure(figsize=(6, 4.5))  # 4:3 aspect ratio, half the previous size
plt.plot(time, data)
plt.title("Time Domain Signal")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.grid(True)
plt.gca().set_aspect('auto')  # Automatic aspect ratio for data
plt.show()

# Calculate and plot spectrum
spectrum = tools.spectrum(data, tools.window.rectangular, Fs, 290e3, 410e3)

# Calculate frequency domain data
frequency = []
spectrum_length = len(spectrum)
step = (410e3 - 290e3) / (spectrum_length - 1)
for n in range(spectrum_length):
    # convert frequency to kHz
    frequency.append((290e3 + n * step) / 1e03)

# Plot spectrum
plt.figure(figsize=(6, 4.5))  # 4:3 aspect ratio, half the previous size
plt.plot(frequency, spectrum)
plt.title("Spectrum Analysis")
plt.xlabel("Frequency [kHz]")
plt.ylabel("Magnitude [dBV]")
plt.grid(True)
plt.gca().set_aspect('auto')  # Automatic aspect ratio for data
plt.show()
