import numpy as np
from scipy import signal
from scipy.ndimage import uniform_filter1d

class DSPReview:
    """
    A class that encapsulates various digital signal processing (DSP) techniques for EMG data.
    """
    
    @staticmethod
    def bandpass_filter(data: np.ndarray, lowcut: float, highcut: float, fs: float, order: int = 4) -> np.ndarray:
        """
        Applies a Butterworth bandpass filter to the input data.
        
        Parameters:
        - data: The input EMG signal (1D numpy array).
        - lowcut: The lower cutoff frequency of the bandpass filter (in Hz).
        - highcut: The upper cutoff frequency of the bandpass filter (in Hz).
        - fs: The sampling frequency of the signal (in Hz).
        - order: The order of the Butterworth filter (default is 4).
        
        Returns:
        - The filtered EMG signal as a 1D numpy array.
        """
        nyquist = 0.5 * fs
        low = lowcut / nyquist
        high = highcut / nyquist
        
        b, a = signal.butter(order, [low, high], btype='band')
        filtered_data = np.zeros_like(data)
        for i in range(data.shape[0]):
            filtered_data[i, :] = signal.filtfilt(b, a, data[i, :])
        
        return filtered_data
    
    def rms_envelope(self, data: np.ndarray, sampling_rate: float, window_ms: float = 100.0) -> np.ndarray:
        """
        Computes the RMS envelope of the EMG signal using a moving window.
        
        Parameters:
        - data: The input EMG signal (2D numpy array with shape [num_channels, num_samples]).
        - sampling_rate: The sampling frequency of the signal (in Hz).
        - window_ms: The size of the moving window in milliseconds (default is 100 ms).
        
        Returns:
        - The RMS envelope of the EMG signal as a 2D numpy array with the same shape as the input data.
        """
        
        window_size = int((window_ms / 1000.0) * sampling_rate)
        
        squared_signal = data ** 2
        
        # Use uniform_filter1d to compute the moving average of the squared signal efficiently along the time axis for each channel independently 
        mean_signal = uniform_filter1d(squared_signal, size=window_size, axis=-1)
        
        # Ensure that the mean signal is non-negative before taking the square root to avoid NaN values in the RMS envelope
        mean_signal = np.maximum(mean_signal, 0.0)
        
        
        rms_envelope = np.sqrt(mean_signal)
        
        # Alternative implementation using convolution (commented out for performance reasons, as uniform_filter1d is optimized for this purpose)
        # kernel = np.ones(window_size) / window_size
        # rms_envelope = np.zeros_like(data)
        # for i in range(data.shape[0]):
        #     squared_signal = data[i, :] ** 2
            
        #     mean_signal = np.convolve(squared_signal, kernel, mode='same')
        #     rms_envelope[i, :] = np.sqrt(mean_signal)
            
        return rms_envelope
    
    
    
    