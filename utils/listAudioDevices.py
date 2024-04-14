import pyaudio

py_audio = pyaudio.PyAudio()
info = py_audio.get_host_api_info_by_index(0)

# List all devices

# Mics
print("Microphones:")
for i in range(0, info.get('deviceCount')):
    # Check number of input channels
    # (If there is at least 1 input channel, then it is suitable as a microphone)
    if py_audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
        print(str(i) + " " + py_audio.get_device_info_by_host_api_device_index(0, i).get('name'))

# Speakers
print("Speakers:")
for i in range(0, info.get('deviceCount')):
    # Check number of input channels
    # (If there is at least 1 input channel, then it is suitable as a microphone)
    if py_audio.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels') > 0:
        print(str(i) + " " + py_audio.get_device_info_by_host_api_device_index(0, i).get('name'))
