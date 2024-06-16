# Band-Excitation-Senior-Team-2024

This is the repository for Drexel Senior Design Team 68's project "Band-Excitation Piezoresponse Force Microscopy" for the M3 Learning Lab under Dr. Joshua Agar.

"BandExcitation" is the library created by the M3 Learning Lab to generate custom Band Excitation waveforms as lists of points.

"WF_SDK" is based on the Digilent-created library to control the Eclypse Z7 FPGA development board via DLL commands. It has been extensively modified to add function support for all waveform generation types and active data-streaming for generating waveforms larger than the 65536 points allowed by the buffer in normal operation.

Provided with this modified library are some example scripts. "fft.py" utilizes the WF_SDK library to generate an FFT of a recorded waveform. "be_test.py" gives an example of generating a full Band Excitation signal via the BandExcitation library, and then outputting the signal via the play function. Currently commented out, there is also code provided for recording the signal via the scope functions, however due to the limitations of the Ecylpse Z7's streaming bandwidth, it cannot perform both at the same time. It is recommended to connect to the Ecylpse Z7 via Ethernet rather than USB to provide the most stable data streaming performance.
