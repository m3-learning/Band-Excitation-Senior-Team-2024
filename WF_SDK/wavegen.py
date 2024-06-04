""" WAVEFORM GENERATOR CONTROL FUNCTIONS: generate, close, enable, disable """
""" Modified by Drew Mangione, 12-22-2023 """


# load the dynamic library, get constants path (the path is OS specific)
from WF_SDK.device import check_error
import dwfconstants as constants
import ctypes                     # import the C compatible data types
from sys import platform, path    # this is needed to check the OS type and get the PATH
from os import sep                # OS specific file path separators
if platform.startswith("win"):
    # on Windows
    dwf = ctypes.cdll.dwf
    constants_path = "C:" + sep + \
        "Program Files (x86)" + sep + "Digilent" + sep + \
        "WaveFormsSDK" + sep + "samples" + sep + "py"
elif platform.startswith("darwin"):
    # on macOS
    lib_path = sep + "Library" + sep + "Frameworks" + \
        sep + "dwf.framework" + sep + "dwf"
    dwf = ctypes.cdll.LoadLibrary(lib_path)
    constants_path = sep + "Applications" + sep + "WaveForms.app" + sep + \
        "Contents" + sep + "Resources" + sep + "SDK" + sep + "samples" + sep + "py"
else:
    # on Linux
    dwf = ctypes.cdll.LoadLibrary("libdwf.so")
    constants_path = sep + "usr" + sep + "share" + sep + \
        "digilent" + sep + "waveforms" + sep + "samples" + sep + "py"

# import constants

"""-----------------------------------------------------------------------"""


class function:
    """ function names """
    custom = constants.funcCustom
    sine = constants.funcSine
    square = constants.funcSquare
    triangle = constants.funcTriangle
    noise = constants.funcNoise
    dc = constants.funcDC
    pulse = constants.funcPulse
    trapezium = constants.funcTrapezium
    sine_power = constants.funcSinePower
    ramp_up = constants.funcRampUp
    ramp_down = constants.funcRampDown
    play = constants.funcPlay


"""-----------------------------------------------------------------------"""


def generate(device_data, channel, function, offset=0, frequency=1e03, amplitude=1, symmetry=50, wait=0, run_time=0, repeat=0, data=[]):
    """
        generate an analog signal

        parameters: - device data
                    - the selected wavegen channel (1-2)
                    - function - possible: custom, play, sine, square, triangle, noise, dc, pulse, trapezium, sine_power, ramp_up, ramp_down
                    - offset voltage in Volts, default is 0V
                    - frequency in Hz, default is 1KHz
                    - amplitude in Volts, default is 1V
                    - signal symmetry in percentage, default is 50%
                    - wait time in seconds, default is 0s
                    - run time in seconds, default is infinite (0)
                    - repeat count, default is infinite (0)
                    - data - list of voltages, used only if custom or play, default is empty
    """
    # enable channel
    channel = ctypes.c_int(channel - 1)
    if dwf.FDwfAnalogOutNodeEnableSet(device_data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.c_bool(True)) == 0:
        check_error()

    # set function type
    if dwf.FDwfAnalogOutNodeFunctionSet(device_data.handle, channel, constants.AnalogOutNodeCarrier, function) == 0:
        check_error()

    # set frequency
    if dwf.FDwfAnalogOutNodeFrequencySet(device_data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.c_double(frequency)) == 0:
        check_error()

    # Set amplitude or DC voltage
    # If function type is custom or play, ignore amplitude and use data amplitude
    if function == constants.funcCustom or function == constants.funcPlay:
        if dwf.FDwfAnalogOutNodeAmplitudeSet(device_data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.c_double(max(data))) == 0:
            check_error()
    else:
        if dwf.FDwfAnalogOutNodeAmplitudeSet(device_data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.c_double(amplitude)) == 0:
            check_error()

    # set offset
    if dwf.FDwfAnalogOutNodeOffsetSet(device_data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.c_double(offset)) == 0:
        check_error()

    # set symmetry
    if dwf.FDwfAnalogOutNodeSymmetrySet(device_data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.c_double(symmetry)) == 0:
        check_error()

    # set running time limit
    if dwf.FDwfAnalogOutRunSet(device_data.handle, channel, ctypes.c_double(run_time)) == 0:
        check_error()

    # set wait time before start
    if dwf.FDwfAnalogOutWaitSet(device_data.handle, channel, ctypes.c_double(wait)) == 0:
        check_error()

    # set number of repeating cycles
    if dwf.FDwfAnalogOutRepeatSet(device_data.handle, channel, ctypes.c_int(repeat)) == 0:
        check_error()

    # Normalize data and set buffer size (Custom or Play only)
    if function == constants.funcCustom or function == constants.funcPlay:
        # Normalize the data to +/- 1
        data_norm = []
        data_max = max(data)
        data_length = len(data)
        for n in range(0, data_length):
            data_norm.append(data[n] / data_max)

        # Check if data is larger than buffer size
        buffer_length = ctypes.c_int(0)
        # Check device buffer size
        if dwf.FDwfAnalogOutNodeDataInfo(device_data.handle, channel, constants.AnalogOutNodeCarrier, 0, ctypes.byref(buffer_length)) == 0:
            check_error()
        if buffer_length.value > data_length:
            buffer_length.value = data_length
        elif buffer_length.value <= data_length and function == constants.funcCustom:
            print("ERROR - Custom data is larger than max buffer size")
            return

    # Custom function
    if function == constants.funcCustom:
        buffer = (ctypes.c_double * data_length)(*data_norm)
        if dwf.FDwfAnalogOutNodeDataSet(device_data.handle, channel, constants.AnalogOutNodeCarrier, buffer, buffer_length) == 0:
            check_error()

    # Play function
    if function == constants.funcPlay:
        # Prime the buffer with the first chunk of data
        buffer = (ctypes.c_double * data_length)(*data_norm)
        if dwf.FDwfAnalogOutNodeDataSet(device_data.handle, channel, constants.AnalogOutNodeCarrier, buffer, buffer_length) == 0:
            check_error()
        iPlay = 0
        iPlay = buffer_length.value
        if dwf.FDwfAnalogOutConfigure(device_data.handle, channel, ctypes.c_bool(True)) == 0:
            check_error()

        # Data integrity variables
        dataLost = ctypes.c_int(0)
        dataFree = ctypes.c_int(0)
        dataCorrupted = ctypes.c_int(0)
        sts = ctypes.c_ubyte(0)
        totalLost = 0
        totalCorrupted = 0

        # Loop until all data is sent
        while True:
            # Fetch Analog Out info for the channel
            if dwf.FDwfAnalogOutStatus(device_data.handle, channel, ctypes.byref(sts)) == 0:
                print("Error")
                szerr = ctypes.create_string_buffer(512)
                dwf.FDwfGetLastErrorMsg(szerr)
                print(szerr.value)
                break

            if sts.value != 3:
                break  # not running !DwfStateRunning

            if iPlay >= data_length:
                continue  # no more data to stream

            # Check playback status
            if dwf.FDwfAnalogOutNodePlayStatus(device_data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.byref(dataFree), ctypes.byref(dataLost), ctypes.byref(dataCorrupted)) == 0:
                check_error()
            totalLost += dataLost.value

            if iPlay + dataFree.value > data_length:  # last chunk might be less than the free buffer size
                dataFree.value = data_length - iPlay
            if dataFree.value == 0:
                continue
            # offset for double is *8 (bytes)
            if dwf.FDwfAnalogOutNodePlayData(device_data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.byref(buffer, iPlay*8), dataFree) == 0:
                check_error()
                break
            iPlay += dataFree.value

        print("Lost: " + str(totalLost))
        print("Corrupted: " + str(totalCorrupted))

    # Start output if not play
    else:
        if dwf.FDwfAnalogOutConfigure(device_data.handle, channel, ctypes.c_bool(True)) == 0:
            check_error()

    return


"""-----------------------------------------------------------------------"""


def close(device_data, channel=0):
    """
        reset a wavegen channel, or all channels (channel=0)
    """
    channel = ctypes.c_int(channel - 1)
    if dwf.FDwfAnalogOutReset(device_data.handle, channel) == 0:
        check_error()
    return


"""-----------------------------------------------------------------------"""


def enable(device_data, channel):
    """ enables an analog output channel """
    channel = ctypes.c_int(channel - 1)
    if dwf.FDwfAnalogOutConfigure(device_data.handle, channel, ctypes.c_bool(True)) == 0:
        check_error()
    return


"""-----------------------------------------------------------------------"""


def disable(device_data, channel):
    """ disables an analog output channel """
    channel = ctypes.c_int(channel - 1)
    if dwf.FDwfAnalogOutConfigure(device_data.handle, channel, ctypes.c_bool(False)) == 0:
        check_error()
    return
