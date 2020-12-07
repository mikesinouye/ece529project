import numpy as np


def perform_dft(input_size, input_sample):
    dft_input = np.zeros(input_size)
    # dft manually
    for k in range(input_size):
        # generate dft exponential
        n = np.arange(input_size)
        dft_exp = np.exp(-2 * np.pi * 1j * k * n / input_size)
        summand = np.multiply(input_sample, dft_exp)
        dft_input[k] = (1 / input_size) * np.sum(summand)

    return dft_input


def find_freq(dft_input, num_samples, sampling_freq):
    # compute frequency by multiplying by bin number by the resolution = sampling_freq / num_samples
    freq = np.argmax(np.absolute(dft_input)) * sampling_freq / num_samples
    # check if freq is larger than nyquist
    if freq > sampling_freq / 2:
        freq = sampling_freq - freq + (sampling_freq / num_samples)
    return freq


def compute_corrected_note(note_freq, relative_frequency):
    # compare notes as they are in relation to middle A = 440Hz
    note = 12 * np.log2(note_freq / relative_frequency)
    # corrected_note = np.round(note) # use for tuning to any note within half-steps
    corrected_note = tune_to_key(note)
    # convert corrected note back to frequency
    corrected_note_freq = np.exp2(corrected_note / 12) * relative_frequency
    return corrected_note_freq


def tune_to_key(note):
    # passes in a "note" which is an integer telling the relation in half steps to the key center

    # get more digits of the note then convert to integer
    note = round(note * 1000)
    # start by finding the octave relation
    octave = int(np.floor(note / 12000))
    # find position in octave
    pos = note % 12000
    # check if position is greater than 450--sequence of notes in a scale (relative) is 0 2 4 5 7 9 11, check if its
    # greater than 450 to determine if we need to assert evenness or oddness
    if pos >= 4500:
        fixed_pos = 2 * round((pos - 5000) / 2000.0) + 5
    else:
        fixed_pos = 2 * round(pos / 2000.0)
    # return the note that has been assigned a value in the key
    return fixed_pos + 12 * octave


def pad_input(input_signal, input_samples, target_samples):
    return np.pad(input_signal, (0, target_samples - input_samples), 'constant')


# def perform_frequency_offset(offset_freq, time_input, sampling_freq, num_samples):
#     # discretize frequency offset
#     discrete_shift = np.round(offset_freq / (sampling_freq / num_samples))
#     n = np.arange(num_samples)
#     shifting_exp = np.exp(-2 * np.pi * 1j * discrete_shift * n / num_samples)
#     new_time_output = np.multiply(time_input, shifting_exp)
#     return new_time_output

def get_new_sample_count(num_samples, note_freq, corrected_note_freq):
    # find out how many samples to get the portion of output at new frequency
    return round(num_samples * (note_freq / corrected_note_freq))


def inverse_dft(input_size, freq_signal):
    time_signal = np.zeros(input_size)
    for n in range(input_size):
        k = np.arange(input_size)
        idft_exp = np.exp(-2 * np.pi * 1j * k * n / input_size)
        summand = np.multiply(freq_signal, idft_exp)
        time_signal[n] = (1 / input_size) * np.sum(summand)
    return time_signal


def resampling(time_signal, num_samples, new_num_samples):
    # 2 point linear resampling: calc the weighted mean between the points that the new point should be sampled at
    # get new sampling rate relative to num samples
    sampling_rate_rel = num_samples / new_num_samples
    new_time_signal = np.zeros(new_num_samples)
    new_time_signal[0] = time_signal[0]
    new_time_signal[-1] = time_signal[num_samples - 1]
    for i in range(1, new_num_samples - 1):
        curr_sample_index = i * sampling_rate_rel
        # calculate weighted mean
        floor = int(np.floor(curr_sample_index))
        ceil = int(np.ceil(curr_sample_index))
        weight = curr_sample_index - floor
        new_time_signal[i] = (1 - weight) * time_signal[floor] + weight * time_signal[ceil]
    return new_time_signal


class SmallSampleAutoTuner:
    input_size = 128
    padded_size = 8000
    sampling_rate = 0
    input_sample = np.zeros(input_size)
    dft_input = np.zeros(input_size)
    output_sample = np.zeros(input_size)
    note_freq = 0
    corrected_note_freq = 0
    inverse = np.zeros(input_size)
    offset_frequency = 0
    freq_output = np.zeros(input_size)

    def __init__(self, input_sample, sampling_rate, input_size, padded_size, relative_frequency):
        """Takes in input paramters to the autotuner and performs autotuning"""
        self.relative_frequency = relative_frequency
        self.input_size = input_size
        self.padded_size = padded_size
        self.input_sample = input_sample
        self.sampling_rate = sampling_rate
        self.input_sample_padded = pad_input(input_sample, self.input_size, self.padded_size)
        self.dft_input = np.fft.fft(self.input_sample_padded)
        self.note_freq = find_freq(self.dft_input, self.padded_size, self.sampling_rate)
        self.corrected_note_freq = compute_corrected_note(self.note_freq, self.relative_frequency)
        self.new_sample_count = get_new_sample_count(self.input_size, self.note_freq, self.corrected_note_freq)
        self.out_time_signal = resampling(input_sample, self.input_size, self.new_sample_count)
        self.out_time_signal_padded = pad_input(self.out_time_signal, self.new_sample_count, self.padded_size)
        self.out_freq_signal = np.fft.fft(self.out_time_signal_padded)
        self.new_freq = find_freq(self.out_freq_signal, self.padded_size, self.sampling_rate)
        print()
