import abc
import pickle
import numpy as np


class BaseDataSource(abc.ABC):
    """
    Abstract base class defining the strict contract for all EMG data sources.
    The UI layer will program against this interface, remaining entirely blind
    to whether the data is mocked or coming from live hardware.
    """


    @abc.abstractmethod
    def _load_data(self):
        """
        Load the EMG data from the source (e.g., file, hardware stream).
        This method is responsible for preparing the data for chunked access.
        """
        pass


class LiveDataSource(BaseDataSource):
    """"
    Used for live hardware streaming. This class will interface directly with the EMG acquisition hardware,
    fetching real-time data and providing it in the required chunked format to the UI.
        Note: The implementation of this class is currently a placeholder. The actual logic for connecting to
        and streaming from the hardware will depend on the specific EMG device and its SDK/API.
        This class will need to be fleshed out with the appropriate methods for initializing the hardware connection,
        starting/stopping the data stream, and fetching data in real-time.
        For now, it serves as a structural placeholder to ensure that the UI can be developed and tested against
        a consistent interface, regardless of whether the data is coming from live hardware or a mock source.
        
    """

    def __init__(self):
        super().__init__()

    def _load_data(self):
        """
        Initialize the connection to the EMG hardware and prepare for data streaming.
        This method will need to be implemented with the specific logic for the target EMG device.
        """
        pass

    def get_chunk(self) -> np.ndarray:
        """
        Fetch the next chunk of EMG data from the live hardware stream.
        This method will need to be implemented to read data from the hardware buffer,
        ensuring that it returns data in the correct format and chunk size for the UI.
        """
        pass


class FileDataSource(BaseDataSource):
    """
    Used for Review mode with pre-recorded EMG data. This class will load EMG data from a specified .pkl file,
    bypasses streaming entirely, and provides the full, cleaned dataset for offline processing, static rendering and visualization in the UI.
    """

    def __init__(self, file_path: str, sampling_rate: int):
        super().__init__()

        self.file_path = file_path
        self.sampling_rate = sampling_rate
        self.data = self._load_data()
        

    def _load_data(self) -> np.ndarray:
        
        """
        Reads the EMG data from the specified .pkl file, extracts the relevant biosignal,
        and restructures it into a 2D array where each row corresponds to a channel and
        each column corresponds to a sample.
        """
        
        try:
            with open(self.file_path, 'rb') as f:
                raw_data = pickle.load(f)
            
            emg_signal = raw_data["biosignal"]
            if emg_signal.size == 0:
                raise ValueError(f"The file at {self.file_path} contains no data.")
        
            # Restructure the data to have shape (num_channels, total_samples_per_channel)
            channel_data = emg_signal.transpose(2, 1, 0).reshape(-1, emg_signal.shape[0]).T
            return channel_data
        
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not locate the EMG data file at: {self.file_path}")

    def get_data(self) -> np.ndarray:
        """
        Returns the full dataset loaded from the file.
        """
        return self.data







# class MockDataSource(BaseDataSource):
#     """
#     Simulates a continuous hardware stream by loading a static .pkl file
#     and yielding chunks of data, seamlessly looping back to the beginning
#     when the end of the file is reached.
#     """


#     def __init__(self, file_path: str, chunk_size: int = 50):
#         self.file_path = file_path
#         self.chunk_size = chunk_size
#         self.sampling_rate = None

#         # Load and flatten the data into a 1D sequence upon initialization
#         self.data = self._load_data()
#         self.total_samples = self.data.shape[1]

#         # Internal pointer to track our current position in the array
#         self.current_index = 0


#     def _load_data(self) -> np.ndarray:
#         """
#         Reads the EMG data from the specified .pkl file, extracts the relevant biosignal,
#         and restructures it into a 2D array where each row corresponds to a channel and
#         each column corresponds to a sample.
#         """
        
#         try:
#             with open(self.file_path, 'rb') as f:
#                 raw_data = pickle.load(f)
                
#             # data_array = np.array(raw_data).flatten()
#             emg_signal = raw_data["biosignal"]
#             self.sampling_rate = raw_data["device_information"]["sampling_frequency"]

#             if emg_signal.size == 0:
#                 raise ValueError(f"The file at {self.file_path} contains no data.")
            
            

#             # Restructure the data to have shape (num_channels, total_samples_per_channel)
#             channel_data = emg_signal.transpose(2, 1, 0).reshape(-1, emg_signal.shape[0]).T
            
#             # Calculate the peak-to-peak amplitude for each channel to verify that the data is loaded correctly
#             amplitudes = np.ptp(channel_data, axis=1)

#             # Identify active channels based on a simple amplitude threshold (this is just for verification and can be adjusted as needed)
#             active_channel_indices = np.where(amplitudes > 0.001)[0]

#             channel_data = channel_data[active_channel_indices, :]

#             print(f"Data Loaded. Filtered out {emg_signal.shape[0] - len(active_channel_indices)} dead channels.")
#             print(f"Active Channels Remaining: {len(active_channel_indices)}")

#             return channel_data
        
#         except FileNotFoundError:
#             raise FileNotFoundError(f"Could not locate the EMG data file at: {self.file_path}")
    


#     def get_chunk(self) -> np.ndarray:
#         """
#         Slices the next 'chunk_size' of samples from the array.
#         If the slice exceeds the array bounds, it pieces together the end
#         of the array and the beginning of the array to simulate a coninuous loop.
#         """
#         end_index = self.current_index + self.chunk_size

#         # Standard case: The chunk is safely withing the bounds of the data

#         if end_index <= self.total_samples:
#             chunk = self.data[:,self.current_index:end_index]
#             self.current_index = end_index

#             if self.current_index == self.total_samples:
#                 self.current_index = 0

#             return chunk
        

#         # Edge case: Hitting the end of the array mid-chunk and we need to wrap around
#         else:
#             # TODO (DSP): Discontinuity Artifact Warning
#             # Wrapping from the end of the file back to index 0 creates an instantaneous
#             # amplitude jump (step-function). This is an accepted mock artifact for UI testing,
#             # but it will cause filter ringing during digital signal processing later.
#             # This artifact will be handled/ignored when building the DSP Pipeline.


#             # Grab whatever is left at the tail end of the array
#             tail_chunk = self.data[:,self.current_index:self.total_samples]
            
#             # Calculate the deficit
#             remaining_needed = self.chunk_size - (tail_chunk.shape[1])  # Number of samples still needed to complete the chunk

#             # Grab the deficit from the absolute beginning of the array
#             head_chunk = self.data[:,0:remaining_needed]

#             # Stitch them together tp form a complete chunk of exactly 50 samples
#             chunk = np.concatenate((tail_chunk, head_chunk), axis=1)

#             # Update the pointer to reflect where we are now in the new loop
#             self.current_index = remaining_needed

#             return chunk


#     def get_num_channels(self) -> int:
#         """
#         Returns the number of channels in the data.
#         """
#         try:
#             return self.data.shape[0]
#         except IndexError:
#             raise ValueError("The data is empty or has an invalid shape.")