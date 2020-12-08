# Automatic Tuning of Monophonic Digital Music Signals

Project source code for our ECE 529: Digital Signal Processing semester project

Team Members: Michael Bullock and Michael Inouye

## Software: 
To run, call monophonic_tuner.py with the following arguments: 
#### required: 
* -i input_file  
  * give the file name of the monophonic .wav file to tune
#### optional:
* -o output_file     
  * give the output .wav file name
* -fc key_frequency    
  * give the frequency in Hz of the first note in the ionian mode to tune the music signal to. ex: for Gb aeolian, one would pass 440.0, the frequency in Hz for A ionian. the default is 261.63 for C ionian
* -fl lower_cutoff_frequency  
  * give the lower cutoff frequency for the bp filter to be applied to music signal. the default is 40.0 Hz
* -fu upper_cutoff_frequency  
  * give the upper cutoff frequency for the bp filter to be applied to music signal. the default is 5000.0 Hz
* -ss segment_size     
  * give the segment size for tuning. note: segments must be large enough for the lowest frequency to be detectable. the default is 2048. note: must be smaller than 8000
* -so segment_overlap   
  * give the overlap between segments to be tuned. the default is 64
  
  #### Example Execution
  `python monophonic_tuner.py -i example0.wav -oexample0_output.wav -fc 440 -fl 20 -fu 5000 -ss 2048 -so 64`
