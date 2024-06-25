import pyaudio

class AudioHandling:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 10
    def __init__(self, profile):
        self.p = None
        self.stream_input = None 
        self.stream_output = None
        self.profile = profile
    def init_channels(self):

        self.p = pyaudio.PyAudio()
        self.stream_input = self.p.open(format=AudioHandling.FORMAT,
                                        channels=AudioHandling.CHANNELS,
                                        rate=AudioHandling.RATE,
                                        input=True,
                                        input_device_index=self.profile.my_mic,
                                        frames_per_buffer=AudioHandling.CHUNK)
        self.stream_output = self.p.open(format=AudioHandling.FORMAT,
                                         channels=AudioHandling.CHANNELS,
                                         rate=AudioHandling.RATE,
                                         output=True,  # for speaker
                                         input_device_index=self.profile.my_speaker,
                                         frames_per_buffer=AudioHandling.CHUNK)

    def destroy_channels(self):
        # Stop audio streams 
        if self.stream_input:
            self.stream_input.stop_stream()
            self.stream_input.close()
            self.stream_input = None
        if self.stream_output:
            self.stream_output.stop_stream()
            self.stream_output.close()
            self.stream_output = None

        # Close PyAudio instance
        if self.p:
            self.p.terminate()
            self.p = None

    def get_frame(self):
        data = self.stream_input.read(AudioHandling.CHUNK)
        return data

    def put_frame(self, data):
        self.stream_output.write(data)
