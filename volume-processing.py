import sys
import wave
import numpy as np
import scipy.signal as sps
from pathlib import Path
import matplotlib.pyplot as plt 

DEFAULT_SAMPLERATE = 44100
DEFAULT_LENGTH = 90
OUTPUT_SAMPLERATE = 10

def to_mono(signal, nchannels):
    return np.mean([signal[i::nchannels] for i in range(nchannels)], axis=0)

def read_signal(fp):
    spf = wave.open(str(fp.resolve()), 'r')
    signal = spf.readframes(-1)
    signal = np.frombuffer(signal, np.int16)
    return (signal, spf.getparams())

def stretch(signal, seconds, samplerate):
    samples = int(seconds * samplerate)
    return sps.resample(signal, samples)

def window_mean(signal, window_size):
    signal = signal[:signal.shape[0] - signal.shape[0] % window_size]    
    signal = np.mean(signal.reshape(-1, window_size), axis=1)
    return signal

def plot_signal(signal):
    plt.plot(np.arange(signal.shape[0]), signal)
    plt.show()

def get_volume_graph(signal):
    window_size = int(DEFAULT_SAMPLERATE / OUTPUT_SAMPLERATE)
    signal = window_mean(np.abs(signal), window_size)
    return signal

def autocorrelation(signal):
    return sps.convolve(signal, signal)

def main():
    input_fn = sys.argv[1]
    signal, params = read_signal(Path(input_fn))
    signal = to_mono(signal, params.nchannels)
    signal = stretch(signal, DEFAULT_LENGTH, DEFAULT_SAMPLERATE)
    volume = get_volume_graph(signal)
    # plot_signal(volume)
    plot_signal(autocorrelation(signal))

if __name__ == '__main__':
    main()