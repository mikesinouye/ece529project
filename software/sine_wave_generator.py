import numpy as np


def generate_sine_wave_sample(freq, num_samples, sample_rate):
     #mimic general audio, set sample_rate = 44100
    n = np.arange(num_samples)
    x = np.sin((freq/sample_rate)*2*np.pi*n)
    return n, x
