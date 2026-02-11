"""
EEG Signal Processing Pipeline
Analysis steps: Preprocessing, ICA, Spectral Analysis, and Automated Diagnosis.
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import hilbert

import mne
from mne.preprocessing import ICA
from mne_connectivity.viz import plot_connectivity_circle
from autoreject import AutoReject

# === CONFIGURATION ===
# Path to the dataset (Update this path for your local machine)
FILE_PATH = "subjects/Subject_01.edf"
MONTAGE_TYPE = 'standard_1020'

# ==========================================
# STEP 1: Load and Preprocess Data
# ==========================================
print("-" * 30)
print("STEP 1: Load and Preprocess Data")
print("-" * 30)

# Load raw data
raw = mne.io.read_raw_edf(FILE_PATH, preload=True)

# Rename channels to remove unnecessary suffixes (e.g., '-LE')
mapping = {name: name.replace('-LE', '') for name in raw.ch_names if '-LE' in name}
raw.rename_channels(mapping)

# Set channel types and montage
if 'Trig' in raw.ch_names:
    raw.set_channel_types({'Trig': 'stim'})

try:
    montage = mne.channels.make_standard_montage(MONTAGE_TYPE)
    raw.set_montage(montage, match_case=False)
except ValueError:
    print("Warning: Standard montage could not be applied.")

# Select EEG channels only
raw.pick_types(eeg=True, eog=False, stim=False, exclude='bads')

# Display signal metadata
sfreq = raw.info['sfreq']
n_channels = len(raw.ch_names)
duration = raw.times[-1]

print(f"Sampling Frequency: {sfreq} Hz")
print(f"Nyquist Frequency: {sfreq / 2} Hz")
print(f"Duration: {duration:.2f} seconds")
print(f"Number of Channels: {n_channels}")

# Filter Design (FIR)
low_cut, high_cut = 0.5, 45.0
numtaps = int(sfreq) + 1 if int(sfreq) % 2 == 0 else int(sfreq)
taps = signal.firwin(numtaps, [low_cut, high_cut], pass_zero=False, fs=sfreq)

# Plot Filter Response (Bode Plot)
w, h = signal.freqz(taps, 1, worN=2000, fs=sfreq)
plt.figure(figsize=(10, 5))
plt.plot(w, 20 * np.log10(abs(h)), 'b')
plt.title('Filter Frequency Response (Bode Plot)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude (dB)')
plt.grid(True)
plt.xlim(0, 60)
plt.show()

# Apply Filters: Notch (50Hz) + Bandpass (0.5-45 Hz)
raw_processed = raw.copy()
raw_processed.notch_filter(freqs=50.0, verbose=False)
raw_processed.filter(l_freq=low_cut, h_freq=high_cut, verbose=False)

# Compare PSD before and after filtering
raw.compute_psd(fmax=80).plot()
raw_processed.compute_psd(fmax=80).plot()
plt.show()

# ==========================================
# STEP 2: Epoching & AutoReject
# ==========================================
print("\n" + "=" * 30)
print("STEP 2: Epoching & AutoReject")
print("=" * 30)

# Create fixed-length epochs (2 seconds)
epoch_duration = 2.0
epochs = mne.make_fixed_length_epochs(raw_processed, duration=epoch_duration, preload=True)

# Apply AutoReject to clean artifacts
ar = AutoReject(n_interpolate=[1, 2, 4], consensus=[0.5, 0.7], random_state=42, verbose=False)
epochs_clean, reject_log = ar.fit_transform(epochs, return_log=True)

# Visualize rejection log
reject_log.plot(orientation='horizontal')
plt.suptitle("AutoReject Log")
plt.show()

# Detect and interpolate bad channels (>70% bad epochs)
labels = reject_log.labels
bad_channels_detected = []
threshold_percentage = 0.70

for i, ch_name in enumerate(epochs.ch_names):
    bad_ratio = np.sum((labels[:, i] == 1) | (labels[:, i] == 2)) / len(labels)
    if bad_ratio > threshold_percentage:
        bad_channels_detected.append(ch_name)

epochs_clean.info['bads'].extend(bad_channels_detected)
epochs_clean.interpolate_bads(reset_bads=True, verbose=False)

# Visualize cleaned epochs
epochs_clean.plot(n_epochs=3, title="Cleaned EEG Signal", block=True)

# ==========================================
# STEP 3: ICA (EOG Artifact Removal)
# ==========================================
print("\n" + "=" * 30)
print("STEP 3: ICA (EOG Removal)")
print("=" * 30)

ica = ICA(n_components=15, max_iter='auto', random_state=97)
ica.fit(epochs_clean, verbose=False)

# Identify EOG-related components automatically
target_eog_channel = next((ch for ch in ['Fp1', 'Fp2', 'Fz'] if ch in epochs_clean.ch_names), None)

if target_eog_channel:
    eog_inds, scores = ica.find_bads_eog(epochs_clean, ch_name=target_eog_channel, threshold=3.0)
    ica.exclude = eog_inds
    ica.plot_scores(scores, exclude=eog_inds, title=f"Component correlation with {target_eog_channel}")
    plt.show()

ica.plot_components()
plt.show()

# Apply ICA
epochs_final = epochs_clean.copy()
ica.apply(epochs_final, verbose=False)

# ==========================================
# STEP 4: Time & Frequency Inspection
# ==========================================
print("\n" + "=" * 30)
print("STEP 4: Time & Frequency Inspection")
print("=" * 30)

# Select a frontal channel for comparison
picked_ch = target_eog_channel if target_eog_channel else epochs_final.ch_names[0]

# Prepare data for plotting
clean_data_segment = epochs_final.get_data(picks=picked_ch, copy=True)[0:3, 0, :].flatten()
raw_data_segment, times = raw.get_data(picks=picked_ch, start=0, stop=len(clean_data_segment), return_times=True)

# Plot Time Domain Comparison
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
ax1.plot(times, raw_data_segment[0], color='red', alpha=0.7, label='Raw Data')
ax1.set_title(f'Time Domain: RAW ({picked_ch})')
ax1.legend()

times_clean = np.linspace(0, len(clean_data_segment) / sfreq, len(clean_data_segment))
ax2.plot(times_clean, clean_data_segment, color='blue', label='Final Clean Data')
ax2.set_title(f'Time Domain: FINAL ({picked_ch})')
ax2.legend()
plt.tight_layout()
plt.show()

# Plot Frequency Domain Comparison (PSD)
psds_raw, freqs_raw = raw.compute_psd(fmax=60, picks='eeg').get_data(return_freqs=True)
psds_clean, freqs_clean = epochs_final.compute_psd(fmax=60, picks='eeg').get_data(return_freqs=True)

plt.figure(figsize=(10, 6))
plt.plot(freqs_raw, 10 * np.log10(psds_raw.mean(axis=0)), 'r--', label='Raw Data')
plt.plot(freqs_clean, 10 * np.log10(psds_clean.mean(axis=0).mean(axis=0)), 'b', label='Clean Data')
plt.title('PSD Comparison: Raw vs Clean')
plt.legend()
plt.show()

# ==========================================
# STEP 5: Per-Channel PSD
# ==========================================
print("\n" + "=" * 30)
print("STEP 5: Per-Channel PSD")
print("=" * 30)

# Calculate PSD using Welch method
psds_raw, freqs = raw.compute_psd(method='welch', fmin=0.5, fmax=60, picks='eeg').get_data(return_freqs=True)
psds_clean, _ = epochs_final.compute_psd(method='welch', fmin=0.5, fmax=60, picks='eeg').get_data(return_freqs=True)
psds_clean_mean = psds_clean.mean(axis=0)

# Plot grid of channels
n_cols = 4
n_rows = math.ceil(n_channels / n_cols)
fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 3 * n_rows), constrained_layout=True)
axes = axes.flatten()

for idx, ch_name in enumerate(epochs_final.ch_names):
    ax = axes[idx]
    ax.plot(freqs, psds_raw[raw.ch_names.index(ch_name)], 'r', alpha=0.6, label='Before')
    ax.plot(freqs, psds_clean_mean[idx], 'b', alpha=0.8, label='After')
    ax.set_title(ch_name)
    ax.set_yscale('log')
    if idx == 0: ax.legend()

plt.suptitle('Per-Channel PSD: Before vs After')
plt.show()

# ==========================================
# STEP 6: Topomaps (Brain Rhythms)
# ==========================================
print("\n" + "=" * 30)
print("STEP 6: Topomaps")
print("=" * 30)

freq_bands = {"Theta": (4, 8), "Alpha": (8, 12), "Beta": (12, 30)}
spectrum = epochs_final.compute_psd(method='welch', fmin=1, fmax=40)
psds, freqs = spectrum.get_data(return_freqs=True)
psds_mean = psds.mean(axis=0)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, (band, (fmin, fmax)) in zip(axes, freq_bands.items()):
    idx = np.where((freqs >= fmin) & (freqs <= fmax))[0]
    mne.viz.plot_topomap(10 * np.log10(psds_mean[:, idx].mean(axis=1)), epochs_final.info, axes=ax, show=False,
                         cmap='RdBu_r')
    ax.set_title(f"{band} ({fmin}-{fmax} Hz)")
plt.show()

# ==========================================
# STEP 7: Connectivity Analysis
# ==========================================
print("\n" + "=" * 30)
print("STEP 7: Connectivity Analysis")
print("=" * 30)

for band, (l_freq, h_freq) in freq_bands.items():
    epochs_band = epochs_final.copy().filter(l_freq, h_freq, verbose=False)
    data = epochs_band.get_data()

    # Envelope correlation via Hilbert transform
    envelope = np.abs(hilbert(data)).transpose(1, 0, 2).reshape(n_channels, -1)
    con_matrix = np.corrcoef(envelope)
    np.fill_diagonal(con_matrix, 0)

    # Thresholding
    con_matrix[np.abs(con_matrix) < 0.4] = 0

    if np.any(con_matrix):
        plt.figure(figsize=(6, 6))
        plot_connectivity_circle(con_matrix, epochs_final.ch_names, title=f'{band} Connectivity')
        plt.show()

# ==========================================
# STEP 8: Automated Diagnosis
# ==========================================
print("\n" + "=" * 30)
print("STEP 8: Automated Diagnosis")
print("=" * 30)


def get_band_power(psds, freqs, fmin, fmax):
    idx = np.logical_and(freqs >= fmin, freqs <= fmax)
    return psds[:, idx].mean(axis=1)


theta_p = get_band_power(psds_mean, freqs, 4, 8)
alpha_p = get_band_power(psds_mean, freqs, 8, 12)
beta_p = get_band_power(psds_mean, freqs, 12, 30)

drowsiness_idx = alpha_p / beta_p
inattention_idx = theta_p / beta_p

# Print Final Report
print("\n" + "=" * 50)
print("FINAL DIAGNOSIS REPORT")
print("=" * 50)

avg_ab = np.mean(drowsiness_idx)
print(f"\nDrowsiness Index (Alpha/Beta): {avg_ab:.2f}")
print("Result: " + (
    "Drowsy / Deeply Relaxed" if avg_ab > 1.5 else "Highly Alert / Anxious" if avg_ab < 0.8 else "Normal State"))

avg_tb = np.mean(inattention_idx)
print(f"\nInattention Index (Theta/Beta): {avg_tb:.2f}")
print("Result: " + ("Attention Deficit / Mind Wandering" if avg_tb > 2.0 else "Good Focus / Normal Attention"))
print("=" * 50)