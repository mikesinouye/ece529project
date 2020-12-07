import argparse
import datetime as dt
import auto_tuner as at
from scipy.io.wavfile import read, write
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, metavar='input_file', help="give the file name of the "
                                                                              "monophonic .wav file to tune")
parser.add_argument('-o', type=str, default="output" + dt.datetime.now().strftime("%d_%b_%Y__%H_%M_%S") + ".wav",
                    help="give the output .wav file name", metavar='output_file')
parser.add_argument('-fc', type=float, default=261.63, help="give the frequency in Hz of the "
                                                            "first note in the ionian mode to "
                                                            "tune the music signal to. "
                                                            "ex: for Gb aeolian, one would pass "
                                                            "440.0, the frequency in Hz for A "
                                                            "ionian. "
                                                            "the default is 261.63 for C ionian",
                    metavar='key_frequency')
parser.add_argument('-fl', type=float, default=40.0, help="give the lower cutoff frequency"
                                                          " for the bp "
                                                          "filter to be applied to music signal."
                                                          " the default is 40.0 Hz", metavar='lower_cutoff_frequency')
parser.add_argument('-fu', type=float, default=5000.0, help="give the upper cutoff frequency"
                                                            " for the bp "
                                                            "filter to be applied to music signal."
                                                            " the default is 5000.0 Hz",
                    metavar='upper_cutoff_frequency')
parser.add_argument('-ss', type=int, default=2048, help="give the segment size for tuning. note: "
                                                        "segments must be large enough for "
                                                        "the lowest frequency to be detectable. "
                                                        "the default is 2048. note: must be "
                                                        "smaller "
                                                        "than 8000", metavar='segment_size')
parser.add_argument('-so', type=int, default=64, help="give the overlap between segments to be "
                                                      "tuned. the default is 64", metavar='segment_overlap')
args = parser.parse_args()

# get input signal
sample_rate, wave_in = read(args.i)
# filter input
wave_in_filtered = at.perform_butterworth_filtering(wave_in[:, 0], np.array([args.fl, args.fu]), sample_rate, args.fl,
                                                    args.fu)
# tune input
my_at = at.AutoTuner(wave_in_filtered, sample_rate, args.fc, args.ss, args.so)
# filter output
filtered_track = at.perform_butterworth_filtering(my_at.tuned_track, my_at.frequency_list, my_at.sampling_frequency,
                                                  args.fl, args.fu)
# ensure output is in correct format for .wav writing
wave_out = at.convert_to_wav_array(filtered_track)
write(args.o, sample_rate, wave_out)
print("tuned monophonic signal file saved to: " + args.o)
