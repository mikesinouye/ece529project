import pytest
import matplotlib.pyplot as plot
import sine_wave_generator as gsw
import small_sample_auto_tuner as ssat
import numpy as np
from scipy.io.wavfile import write, read
import auto_tuner as at


def test_generate_sine():
    inp, out = gsw.generate_sine_wave_sample(464, 4096, 44100)
    plot.plot(inp, out)
    plot.show()
    inp = np.arange(8000)
    #out = np.pad(out, (0, 3904), 'constant')
    my_at = ssat.SmallSampleAutoTuner(out, 44100, 4096, 8000, 261.63)
    plot.plot(inp, my_at.dft_input)
    plot.show()

    plot.plot(inp[0:50], my_at.out_time_signal_padded[0:50])
    plot.plot(inp[0:50], my_at.input_sample_padded[0:50])
    plot.show()
    plot.plot(inp, np.absolute(my_at.dft_input))
    plot.plot(inp,np.absolute(my_at.out_freq_signal))
    plot.show()
    # scale and discretize the output amplitude
    real_sig = my_at.out_time_signal

    scaled_tuned_sample = np.int16((real_sig) * 32767 / (np.max(real_sig)))
    # give more to listen to
    scaled_tuned_extended = np.append(scaled_tuned_sample, (scaled_tuned_sample, scaled_tuned_sample, scaled_tuned_sample, scaled_tuned_sample, scaled_tuned_sample,scaled_tuned_sample, scaled_tuned_sample,scaled_tuned_sample, scaled_tuned_sample))
    write('test.wav', 44100, scaled_tuned_extended)
    out = np.int16(out*32767 / (np.max(out)))
    input = np.append(out, (out,out,out,out,out,out,out,out,out,out,out,out,out,out,out,out,out,out,out,out,out,out,out,out,out,out,out,out,out,out,out))
    write('input.wav', 44100, input)
    c = np.fft.fft(out)
    c = np.fft.ifft(c)
    plot.plot(np.arange(np.size(out)), c)
    plot.show()


def test_at_slicing():
    full_track = np.ones(1000)
    sliced_track = at.small_sample_slicing(full_track, 110, 10)
    full_track = at.recombine_track(sliced_track, 10)


def test_full_at():
    inp, out1 = gsw.generate_sine_wave_sample(464, 16384, 44100)
    _,out2 = gsw.generate_sine_wave_sample(274,16384,44100)
    _,out3 = gsw.generate_sine_wave_sample(970,16384,44100)
    input_signal = np.concatenate((out1, out2, out3))
    my_at = at.AutoTuner(input_signal, 44100, 261.63, 256, 0)
    inp = np.arange(20480)
    plot.plot(inp, input_signal[0:20480])
    plot.plot(inp, my_at.tuned_track[0:20480])
    plot.show()
    wave_out = at.convert_to_wav_array(my_at.tuned_track)
    wave_in = at.convert_to_wav_array(input_signal)
    write('input_signal.wav',44100, wave_in)
    write('output_signal.wav', 44100, wave_out)
    print()


def test_on_real():
    sample_rate, wave_in = read('example0.wav')
    wave_in_filtered = at.perform_butterworth_filtering(wave_in[:,0], np.array([20, 5000]), sample_rate, 20, 5000)
    my_at = at.AutoTuner(wave_in_filtered, sample_rate, 261.63, 2048, 64)
    filtered_track = at.perform_butterworth_filtering(my_at.tuned_track, my_at.frequency_list, my_at.sampling_frequency,
                                                      20, 5000)
    wave_out = at.convert_to_wav_array(filtered_track)
    write('output_example0_filtered2.wav', sample_rate, wave_out)