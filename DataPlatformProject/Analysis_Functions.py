import pandas as pd
import numpy as np
from scipy.signal import welch, stft, find_peaks, butter, filtfilt
try:
    import pywt
except ImportError:
    pywt = None
    print("PyWavelets (pywt) is not installed. Wavelet functionality will be limited.")

class Analysis_Functions:
    """
    A class for performing basic data analysis tasks.
    """

    def descriptive_statistics(
        self,
        df: pd.DataFrame,
        columns: list = None,
        additional_stats: bool = False
    ) -> pd.DataFrame:
        """
        Computes and returns basic descriptive statistics for a given DataFrame.

        :param df: A pandas DataFrame containing your dataset.
        :param columns: An optional list of columns to focus on. If None, all columns 
                        are included in the analysis.
        :param additional_stats: If True, compute extra statistics (e.g. skew, kurtosis).
        :return: A pandas DataFrame or series with descriptive statistics.
        """

        if columns is not None:
            # Filter DataFrame to specified columns
            data_to_analyze = df[columns]
        else:
            data_to_analyze = df

        # Basic stats from Pandas
        stats_df = data_to_analyze.describe()

        if additional_stats:
            # Example of computing skew & kurtosis. You could easily add more.
            skew_vals = data_to_analyze.skew(numeric_only=True)
            kurt_vals = data_to_analyze.kurt(numeric_only=True)

            # Convert to DataFrame so we can combine easily
            skew_vals = pd.DataFrame(skew_vals, columns=["skew"])
            kurt_vals = pd.DataFrame(kurt_vals, columns=["kurt"])

            # Join existing stats with new stats
            # We'll transpose stats_df to match the shape of skew/kurt, then transpose back
            stats_df_t = stats_df.T
            stats_df_t = stats_df_t.join(skew_vals).join(kurt_vals)
            stats_df = stats_df_t.T

        return stats_df
    
    def analyze_fft(
        self,
        df: pd.DataFrame,
        columns: list,
        sampling_rate: float = 1.0
    ):
        """
        Performs a Fast Fourier Transform (FFT) on selected columns of the DataFrame.

        WHAT IT IS:
            A mathematical transform that converts time-domain data to the frequency domain,
            revealing the signal's frequency components.

        WHAT IT'S GOOD FOR:
            - Identifying dominant frequencies in periodic or quasi-periodic signals.
            - Spotting harmonics or strong noise components at specific frequencies.

        CAVEATS:
            - Assumes the signal is roughly stationary over the entire record.
            - Loses time-localization: you won't see how frequencies evolve over time.

        PARAMETERS:
            df : pd.DataFrame
                The DataFrame containing your data.
            columns : list
                The columns (numeric) you want to transform.
            sampling_rate : float, default 1.0
                The sampling rate in Hz (samples per second). Used to compute frequency axis.

        RETURNS:
            A dictionary where each key is the column name, and the value is a tuple (freq, fft_vals):
                freq : np.ndarray
                    Array of frequency bins corresponding to the FFT result.
                fft_vals : np.ndarray
                    Magnitude of the FFT for each frequency bin.
        """
        results = {}
        for col in columns:
            signal = df[col].values

            # Number of samples
            n = len(signal)
            
            # Frequency bins
            freq = np.fft.rfftfreq(n, d=1.0/sampling_rate)
            
            # Real FFT (assuming real-valued signal)
            fft_vals = np.fft.rfft(signal)
            
            # Convert to magnitude
            fft_magnitude = np.abs(fft_vals)
            
            results[col] = (freq, fft_magnitude)

        return results

    def analyze_psd_welch(
        self,
        df: pd.DataFrame,
        columns: list,
        sampling_rate: float = 1.0,
        nperseg: int = 256
    ):
        """
        Estimates the Power Spectral Density (PSD) using Welch's method.

        WHAT IT IS:
            A method to estimate a signal's power over frequency by splitting it into segments,
            windowing them, and averaging the individual segment FFTs.

        WHAT IT'S GOOD FOR:
            - Getting a smoother, more robust view of the frequency content compared to a single FFT.
            - Handling mildly non-stationary signals better than a single-shot FFT.

        CAVEATS:
            - Loses some time resolution; you see an average across segments.
            - Requires parameter choices like segment size (nperseg).

        PARAMETERS:
            df : pd.DataFrame
                The DataFrame containing your data.
            columns : list
                The columns you want to analyze.
            sampling_rate : float, default 1.0
                Sampling rate in Hz (samples per second).
            nperseg : int, default 256
                Length of each segment for Welch's method.

        RETURNS:
            A dictionary where each key is the column name, and the value is a tuple (freq, psd):
                freq : np.ndarray
                    The frequency bins.
                psd : np.ndarray
                    Power spectral density for each frequency bin.
        """
        results = {}
        for col in columns:
            signal = df[col].dropna().values
            freq, psd = welch(signal, fs=sampling_rate, nperseg=nperseg)
            results[col] = (freq, psd)
        return results

    def analyze_stft(
        self,
        df: pd.DataFrame,
        columns: list,
        sampling_rate: float = 1.0,
        nperseg: int = 256,
        noverlap: int = None
    ):
        """
        Performs Short-Time Fourier Transform (STFT) on selected columns.

        WHAT IT IS:
            A time-frequency analysis that splits the signal into small overlapping segments
            and computes an FFT on each segment, yielding a spectrogram.

        WHAT IT'S GOOD FOR:
            - Non-stationary signals where frequency content changes over time.
            - Locating transient events or spikes in the time-frequency plane.

        CAVEATS:
            - There's a trade-off between time resolution and frequency resolution
              based on the segment size (nperseg).
            - Can be computationally more expensive than a single FFT.

        PARAMETERS:
            df : pd.DataFrame
                The DataFrame containing your data.
            columns : list
                The columns you want to analyze.
            sampling_rate : float, default 1.0
                Sampling rate in Hz (samples per second).
            nperseg : int, default 256
                Length of each segment for STFT.
            noverlap : int, optional
                Number of points to overlap between segments. Defaults to nperseg//2 if not set.

        RETURNS:
            A dictionary where each key is the column name, and the value is a tuple (freq, time, Zxx):
                freq : np.ndarray
                    The frequency bins.
                time : np.ndarray
                    The segment times.
                Zxx : np.ndarray
                    The STFT of the signal. Each column of Zxx is the FFT of one segment.
        """
        results = {}
        for col in columns:
            signal = df[col].dropna().values
            f, t, Zxx = stft(signal, fs=sampling_rate, nperseg=nperseg, noverlap=noverlap)
            results[col] = (f, t, Zxx)
        return results

    def analyze_wavelet(
        self,
        df: pd.DataFrame,
        columns: list,
        wavelet: str = "morl",
        scales: np.ndarray = None
    ):
        """
        Performs a Continuous Wavelet Transform (CWT) on selected columns.

        WHAT IT IS:
            A multi-resolution time-frequency transform that uses scaled and shifted versions
            of a 'mother wavelet' to analyze the signal at different frequencies.

        WHAT IT'S GOOD FOR:
            - Capturing both low-frequency and high-frequency information in signals with
              better resolution at higher frequencies compared to an STFT.
            - Identifying sharp transients or spikes that may be smoothed over by an STFT.

        CAVEATS:
            - Requires choosing an appropriate wavelet and scale range.
            - Interpretation can be more nuanced than a straightforward FFT.

        PARAMETERS:
            df : pd.DataFrame
                The DataFrame containing your data.
            columns : list
                The columns you want to analyze.
            wavelet : str, default 'morl'
                The type of mother wavelet. Examples: 'morl', 'mexh', 'cmor', etc.
            scales : np.ndarray, optional
                The scales at which to compute the CWT. Larger scales correspond to lower frequencies.
                If None, we'll generate a simple range.

        RETURNS:
            A dictionary where each key is the column name, and the value is a tuple (cwt_matrix, frequencies):
                cwt_matrix : np.ndarray
                    The wavelet coefficients for each scale and time position.
                frequencies : np.ndarray
                    Approximate frequencies corresponding to each scale (may be wavelet-dependent).
        """
        if pywt is None:
            print("PyWavelets not installed. Wavelet functionality unavailable.")
            return {}

        results = {}
        for col in columns:
            signal = df[col].dropna().values

            # If no scales are provided, define a basic range
            if scales is None:
                scales = np.arange(1, 128)

            cwt_matrix, _ = pywt.cwt(signal, scales, wavelet)

            # Approximate frequencies: depends on wavelet specifics,
            # but often something like frequency = sampling_rate / scale.
            # For a simple placeholder, we can return the scale array directly as "frequencies".
            results[col] = (cwt_matrix, scales)

        return results

    def detect_peaks(
        self,
        df: pd.DataFrame,
        columns: list,
        height=None,
        threshold=None,
        distance=None
    ):
        """
        Detects peaks (spikes) in the specified columns using scipy's find_peaks.

        WHAT IT IS:
            A method for locating local maxima in a 1D array that exceed certain thresholds,
            or that are sufficiently spaced apart.

        WHAT IT'S GOOD FOR:
            - Identifying sudden spikes or bursts of noise in data.
            - Cleaning or masking outliers before/after frequency analysis.

        CAVEATS:
            - Parameter tuning (height, threshold, distance) can greatly affect results.
            - May need domain-specific logic to classify 'true' peaks vs. noise.

        PARAMETERS:
            df : pd.DataFrame
                The DataFrame containing your data.
            columns : list
                Columns in which to detect peaks.
            height : float or tuple, optional
                Required height of peaks. If a tuple, the first element is the minimum and
                the second is the maximum peak height.
            threshold : float or tuple, optional
                Required threshold of peaks. If a tuple, the first element is the minimum and
                the second is the maximum threshold.
            distance : int, optional
                Required minimum distance between peaks in samples.

        RETURNS:
            A dictionary where each key is the column name, and the value is a dictionary:
                {
                  'peaks': np.ndarray of indices,
                  'properties': dict of peak properties (e.g., 'peak_heights')
                }
        """
        results = {}
        for col in columns:
            signal = df[col].dropna().values
            peaks, properties = find_peaks(signal, height=height, threshold=threshold, distance=distance)
            results[col] = {"peaks": peaks, "properties": properties}
        return results

    def filter_data(
        self,
        df: pd.DataFrame,
        columns: list,
        filter_type: str = "lowpass",
        cutoff_freq: float = 1.0,
        order: int = 4,
        sampling_rate: float = 1.0
    ):
        """
        Applies a Butterworth filter to the selected columns.

        WHAT IT IS:
            A digital filter that passes or attenuates frequencies based on the specified cutoff
            (e.g., lowpass, highpass, bandpass, bandstop).

        WHAT IT'S GOOD FOR:
            - Removing or isolating specific frequency bands (e.g., line noise at 50/60 Hz).
            - Pre-processing before or after frequency analysis to focus on certain bands.

        CAVEATS:
            - Must choose the correct cutoff frequency relative to sampling rate.
            - Improper filtering may remove or distort meaningful parts of the signal.

        PARAMETERS:
            df : pd.DataFrame
                The DataFrame containing your data.
            columns : list
                The columns you want to filter.
            filter_type : str, default 'lowpass'
                One of {'lowpass', 'highpass'}. (Can be extended to bandpass/bandstop.)
            cutoff_freq : float, default 1.0
                The critical frequency or frequencies. If filter_type is 'lowpass' or 'highpass',
                this is a single float in Hz.
            order : int, default 4
                The order of the Butterworth filter. Higher order = steeper roll-off.
            sampling_rate : float, default 1.0
                Sampling rate in Hz.

        RETURNS:
            A new pd.DataFrame with the filtered data for the specified columns.
        """
        nyquist = 0.5 * sampling_rate
        normalized_cutoff = cutoff_freq / nyquist

        # Build filter
        b, a = butter(order, normalized_cutoff, btype=filter_type, analog=False)

        # Create a copy to hold filtered columns
        df_filtered = df.copy()

        for col in columns:
            signal = df[col].dropna().values
            filtered_signal = filtfilt(b, a, signal)
            df_filtered[col].iloc[:len(filtered_signal)] = filtered_signal

        return df_filtered
