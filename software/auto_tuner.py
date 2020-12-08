import numpy as np
import small_sample_auto_tuner as ssat
from scipy import signal


def small_sample_slicing(full_track, ss_size, ss_buffer):
    """perform slicing on full track to break it up into small samples of size ss_size, with the last ss_buffer
    components being shared with the next small sample:
    example: full_track of size 1000,
             ss_size of 110,
             ss_buffer of 10
    This gives 10 small sample segments of size 110, with the last segment being right side zero-padded"""
    track_length = np.size(full_track)
    num_slices = int(np.ceil(track_length / (ss_size - ss_buffer)))
    sliced_track = np.zeros((num_slices, ss_size))
    for n in range(num_slices - 1):
        start_index = int(n * (ss_size - ss_buffer))
        end_index = start_index + ss_size
        sliced_track[n, :] = full_track[start_index:end_index]
    # last one do manually to zero pad
    start_index = int((num_slices - 1) * (ss_size - ss_buffer))
    length_to_zero_pad = ss_size - (track_length - start_index)
    sliced_track[num_slices - 1, :] = np.pad(full_track[start_index:], (0, length_to_zero_pad), 'constant')
    return sliced_track


def recombine_track(sliced_track, ss_buffer):
    """takes in a sliced track (that has been autotuned, presumably) and recombines into a single track
    note: overlapping sections have are recombined as averages"""
    num_slices, ss_size = sliced_track.shape
    window = ss_size - ss_buffer
    track_length = num_slices * window
    tuned_track = np.zeros(track_length)
    # handle first case manually
    tuned_track[0:window] = sliced_track[0, 0:window]
    for s in range(1, num_slices):
        tuned_track[s * window:(s + 1) * window] = sliced_track[s, 0:window]
        a = [sliced_track[s - 1, window:ss_size], sliced_track[s, 0:ss_buffer]]
        average = np.sum(a, axis=0)
        tuned_track[s * window:s * window + ss_buffer] = average
    return tuned_track


def convert_to_wav_array(input_signal):
    return np.int16((input_signal) * 32767 / (np.max(input_signal)))


def perform_butterworth_filtering(tuned_track, frequency_list, sampling_rate, min_cutoff, max_cutoff):
    min_tuned_freq = np.min(frequency_list) / 2
    max_tuned_freq = np.max(frequency_list) * 2
    if max_tuned_freq > max_cutoff:
        max_tuned_freq = max_cutoff
    if min_tuned_freq < min_cutoff:
        min_tuned_freq = min_cutoff
    # get butter filter
    sos_filter = signal.butter(10, (min_tuned_freq, max_tuned_freq), btype='bandpass', output='sos', fs=sampling_rate)
    filtered_tuned = signal.sosfilt(sos_filter, tuned_track)
    return filtered_tuned


class AutoTuner:
    frequency_list = []

    def __init__(self, full_track, sampling_frequency, key_center_frequency, ss_size, ss_buffer):
        self.full_track = full_track
        self.sampling_frequency = sampling_frequency
        self.key_center_frequency = key_center_frequency
        self.ss_size = ss_size
        self.ss_buffer = ss_buffer
        self.ss_sliced_track = small_sample_slicing(full_track, ss_size, ss_buffer)
        self.tuned_sliced_track = np.zeros_like(self.ss_sliced_track)
        self.frequency_list = np.zeros(self.ss_sliced_track.shape[0])
        i = 0
        for s in self.ss_sliced_track:
            ss = ssat.SmallSampleAutoTuner(s, self.sampling_frequency, ss_size, 8000, self.key_center_frequency)
            self.tuned_sliced_track[i, :] = ss.out_time_signal_padded[0:ss_size]
            self.frequency_list[i] = ss.corrected_note_freq
            i += 1
        self.tuned_track = recombine_track(self.tuned_sliced_track, self.ss_buffer)
