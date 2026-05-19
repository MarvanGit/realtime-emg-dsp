import numpy as np
from scipy import signal

class DSPLive:
    """
    A class that encapsulates various digital signal processing (DSP) techniques for EMG data.
    This class is designed to be used in a live processing context, where data is continuously streamed in real-time. The methods in this class are optimized for low-latency processing to ensure that the DSP operations can be applied to incoming data chunks without introducing significant delays.
    
    The DSP techniques implemented in this class include:
    - Bandpass filtering: To isolate the relevant frequency components of the EMG signal while attenuating noise and artifacts.
    - RMS envelope extraction: To compute the root mean square (RMS) envelope of the EMG signal, which provides a smoothed representation of the signal's amplitude over time.
        
    The methods in this class can be applied to each incoming chunk of data from the live stream, allowing for real-time analysis and visualization of the EMG signal in the UI.
    
    """
    
    
    def __init__(self, num_channels: int, sampling_rate: float, lowcut: float, highcut: float, filter_order: int = 4, rms_window_ms: float = 100.0):
        self.num_channels = num_channels
        self.sampling_rate = sampling_rate
        self.lowcut = lowcut
        self.highcut = highcut
        
        # Design the bandpass filter coefficients once during initialization to optimize performance for live processing
        self.filter_order = filter_order
        self.bp_b, self.bp_a = self._design_bandpass_filter()
        
        # RMS envelope parameters
        self.rms_window_ms = rms_window_ms
        self.rms_window_size = int((rms_window_ms / 1000.0) * sampling_rate)
        
        # Those coefficients are present in this equation: y[n] = (1/N) * (x[n] + x[n-1] + ... + x[n-N+1])
        # Where N is the window size for the moving average filter used in the RMS envelope calculation. 
        # The coefficients are set to 1/N to compute the average of the squared signal over the specified window size.
        self.ma_b = np.ones(self.rms_window_size) / self.rms_window_size  # Moving average filter coefficients for RMS envelope
        self.ma_a = np.array([1.0])  # Denominator coefficients for moving average filter (FIR filter). 
        
        self.reset_states()  # Initialize filter states to ensure clean processing when starting a new live stream.
    
    def reset_states(self):
        """
        Clears the mathematical memory. 
        Call this when starting a brand new live stream to avoid glitches 
        from old data bleeding into the new recording.
        """
        # Calculate the initial state conditions for a single 1D channel
        bp_zi_1d = signal.lfilter_zi(self.bp_b, self.bp_a)
        # Tile it to match our 2D array shape: (num_channels, zi_length)
        self.bp_state = np.tile(bp_zi_1d, (self.num_channels, 1))
        
        ma_zi_1d = signal.lfilter_zi(self.ma_b, self.ma_a)
        self.ma_state = np.tile(ma_zi_1d, (self.num_channels, 1))
        
        
    def _design_bandpass_filter(self):
        nyquist = 0.5 * self.sampling_rate
        low = self.lowcut / nyquist
        high = self.highcut / nyquist
        b, a = signal.butter(self.filter_order, [low, high], btype='band')
        return b, a
    
    def process_chunk(self, data: np.ndarray) -> np.ndarray:
        """
        Applies the pre-designed Butterworth bandpass filter to the input data.
        """
        
        # Use lfilter with the current state to ensure continuity between chunks in the live stream. The state is updated after each call to maintain the filter's memory across chunks.
        filtered_chunk, self.bp_state = signal.lfilter(self.bp_b, self.bp_a, data, axis=-1, zi=self.bp_state)
        
        squared_chunk = filtered_chunk ** 2
        
        # Mean (Moving average) filter for RMS envelope extraction, applied to the squared signal. The state is updated to maintain continuity across chunks.
        mean_chunk, self.ma_state = signal.lfilter(self.ma_b, self.ma_a, squared_chunk, axis=-1, zi=self.ma_state)
    
        mean_chunk = np.maximum(mean_chunk, 0.0)
        rms_chunk = np.sqrt(mean_chunk)
        
        return rms_chunk