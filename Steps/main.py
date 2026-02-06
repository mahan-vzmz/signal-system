import mne
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

raw = mne.io.read_raw_edf("C:/Users/Victus 16/PycharmProjects/SignalSystem/subjects/Subject_01.edf", preload=True)

mapping = {name: name.replace('-LE', '') for name in raw.ch_names if '-LE' in name}
raw.rename_channels(mapping)
print("New channel names:", raw.ch_names)

if 'Trig' in raw.ch_names:
    raw.set_channel_types({'Trig': 'stim'})
    print("Channel 'Trig' set to stimulus type.")
else:
    print("Channel names found:", raw.ch_names)


try:
    montage = mne.channels.make_standard_montage('standard_1020')
    raw.set_montage(montage, match_case=False)
except ValueError:
    print("Warning: Channel names do not match standard 10-20 system. Skipping montage.")

raw.pick_types(eeg=True, eog=False, stim=False, exclude='bads')

sfreq = raw.info['sfreq']
nyquist_freq = sfreq / 2
n_channels = len(raw.ch_names)
duration = raw.times[-1]

print("-" * 30)
print(f"Sampling Frequency (fs): {sfreq} Hz")
print(f"Nyquist Frequency: {nyquist_freq} Hz")
print(f"Signal Duration: {duration:.2f} seconds")
print(f"Number of EEG Channels: {n_channels}")
print("-" * 30)

raw.plot(duration=5,
         n_channels=20,
         scalings='auto',
         title="Raw EEG Signal",
         block=True)

low_cut = 0.5
high_cut = 45.0
fs = sfreq

numtaps = int(fs)
if numtaps % 2 == 0: numtaps += 1
taps = signal.firwin(numtaps, [low_cut, high_cut], pass_zero=False, fs=fs)
w, h = signal.freqz(taps, 1, worN=2000, fs=fs)

plt.figure(figsize=(10, 5))
plt.plot(w, 20 * np.log10(abs(h)), 'b')
plt.title('Bode Plot (Filter Response)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude (dB)')
plt.axvline(low_cut, color='g', linestyle='--', label='0.5 Hz')
plt.axvline(high_cut, color='r', linestyle='--', label='45 Hz')
plt.grid(True)
plt.legend()
plt.xlim(0, 60)
plt.ylim(-60, 5)
plt.show()



print("Plotting PSD of RAW data (Original)...")
raw.compute_psd(fmax=80).plot()
plt.show()

raw_processed = raw.copy()

raw_processed.notch_filter(freqs=50.0)

raw_processed.filter(l_freq=0.5, h_freq=45.0)

print("Plotting PSD of FILTERED data...")
raw_processed.compute_psd(fmax=80).plot()
plt.show()


print("\n" + "=" * 30)
print("STARTING STEP 2: Epoching & AutoReject")
print("=" * 30)

import matplotlib.pyplot as plt
from autoreject import AutoReject

epoch_duration = 2.0
epochs = mne.make_fixed_length_epochs(raw_processed, duration=epoch_duration, preload=True)

print(f"\nCreated {len(epochs)} epochs of {epoch_duration} seconds each.")


print("Running AutoReject (this may take a minute)...")


ar = AutoReject(n_interpolate=[1, 2, 4], consensus=[0.5, 0.7], random_state=42, verbose=False)

epochs_clean, reject_log = ar.fit_transform(epochs, return_log=True)


print("Plotting AutoReject Heatmap...")
reject_log.plot(orientation='horizontal')
plt.suptitle("AutoReject Log (Heatmap)")
plt.show()

labels = reject_log.labels
n_epochs, n_channels = labels.shape

bad_channels_detected = []
threshold_percentage = 0.70  # 70%

print("\n--- Channel Statistics ---")
for i, ch_name in enumerate(epochs.ch_names):
    bad_count = np.sum((labels[:, i] == 1) | (labels[:, i] == 2))
    bad_ratio = bad_count / n_epochs

    if bad_ratio > threshold_percentage:
        print(f"Channel {ch_name}: {bad_ratio * 100:.1f}% bad epochs -> MARKED AS BAD")
        bad_channels_detected.append(ch_name)

epochs_clean.info['bads'].extend(bad_channels_detected)
epochs_clean.info['bads'] = list(set(epochs_clean.info['bads']))

print(f"\nFinal list of Bad Channels: {epochs_clean.info['bads']}")


print("Interpolating bad channels...")
epochs_clean.interpolate_bads(reset_bads=True)


print("Plotting Sensor Locations...")
epochs_clean.plot_sensors(show_names=True, title="Sensor Locations")
plt.show()


print("Plotting Final Cleaned Epochs...")
epochs_clean.plot(n_epochs=3, n_channels=len(epochs.ch_names), title="Cleaned EEG Signal", block=True)

print("\n" + "=" * 30)
print("STARTING STEP 3: Automated ICA (EOG Removal)")
print("=" * 30)

from mne.preprocessing import ICA

ica = ICA(n_components=15, max_iter='auto', random_state=97)

print("Fitting ICA to cleaned epochs...")
ica.fit(epochs_clean)

target_eog_channel = None
for ch in ['Fp1', 'Fp2', 'Fz', 'Fp1-LE', 'Fp2-LE']:
    if ch in epochs_clean.ch_names:
        target_eog_channel = ch
        break

if target_eog_channel:
    print(f"Using channel '{target_eog_channel}' as EOG reference for auto-detection.")

    eog_inds, scores = ica.find_bads_eog(epochs_clean, ch_name=target_eog_channel, threshold=3.0)

    print(f"Auto-detected EOG components (Blinks): {eog_inds}")

    ica.exclude = eog_inds

    ica.plot_scores(scores, exclude=eog_inds, title=f"Component correlation with {target_eog_channel}")
    plt.show()
else:
    print("Warning: No frontal channel (Fp1/Fp2) found! Cannot auto-detect blinks.")

print("Plotting components (Red title = Marked for removal)...")
ica.plot_components()
plt.show()

print("Applying ICA to remove artifacts...")
epochs_final = epochs_clean.copy()
ica.apply(epochs_final)

if target_eog_channel:
    print(f"Plotting comparison on channel {target_eog_channel}...")

    original_data = epochs_clean.get_data(picks=target_eog_channel)[0, 0, :]
    cleaned_data = epochs_final.get_data(picks=target_eog_channel)[0, 0, :]

    plt.figure(figsize=(10, 6))
    plt.plot(original_data, label='Original (with Artifacts)', color='red', alpha=0.5)
    plt.plot(cleaned_data, label='Cleaned (ICA Applied)', color='blue', linewidth=1.5)
    plt.title(f'Effect of ICA on Channel {target_eog_channel}')
    plt.xlabel('Time points')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid(True)
    plt.show()

print("Step 3 Complete. 'epochs_final' is your clean data.")
print("\n" + "=" * 30)
print("STARTING STEP 4: Time & Frequency Inspection")
print("=" * 30)

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'font.size': 10})


print("Generating Time-Domain Comparison Plot...")

target_ch = [ch for ch in epochs_final.ch_names if 'Fp1' in ch]
picked_ch = target_ch[0] if target_ch else epochs_final.ch_names[0]

print(f"Inspecting Channel: {picked_ch}")


clean_data_segment = epochs_final.get_data(picks=picked_ch, copy=True)[0:3, 0, :].flatten()

n_samples_to_plot = len(clean_data_segment)
raw_data_segment, times = raw.get_data(picks=picked_ch, start=0, stop=n_samples_to_plot, return_times=True)
raw_data_segment = raw_data_segment[0]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=False)

ax1.plot(times, raw_data_segment, color='red', alpha=0.7, label='Raw Data (Drift + Artifacts)')
ax1.set_title(f'Time Domain: RAW Data ({picked_ch})')
ax1.set_ylabel('Amplitude (Volts)')
ax1.legend(loc="upper right")
ax1.grid(True, linestyle='--', alpha=0.6)


times_clean = np.linspace(0, len(clean_data_segment)/raw.info['sfreq'], len(clean_data_segment))
ax2.plot(times_clean, clean_data_segment, color='blue', label='Final Clean Data (Flat Baseline + No Blinks)')
ax2.set_title(f'Time Domain: FINAL Data ({picked_ch}) - After Filter, AutoReject & ICA')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Amplitude (Volts)')
ax2.legend(loc="upper right")
ax2.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()

print("Check point 1: Look at the graphs above.")
print("  - Is the Baseline flat in the blue graph? (Should be yes)")
print("  - Are large blinks (huge spikes) removed in the blue graph? (Should be yes)")
print("\nGenerating PSD Comparison Plot...")


spectrum_raw = raw.compute_psd(fmax=60, picks='eeg')
psds_raw, freqs_raw = spectrum_raw.get_data(return_freqs=True)
psd_raw_mean = 10 * np.log10(psds_raw.mean(axis=0))

spectrum_clean = epochs_final.compute_psd(fmax=60, picks='eeg')
psds_clean, freqs_clean = spectrum_clean.get_data(return_freqs=True)
psd_clean_mean = 10 * np.log10(psds_clean.mean(axis=0).mean(axis=0))

plt.figure(figsize=(10, 6))

plt.plot(freqs_raw, psd_raw_mean, color='red', linestyle='--', label='Raw Data', linewidth=1.5)
plt.plot(freqs_clean, psd_clean_mean, color='blue', label='Final Clean Data', linewidth=2)

plt.axvline(x=50, color='gray', linestyle=':', label='50Hz (Line Noise)')
plt.axvline(x=10, color='green', linestyle=':', label='10Hz (Alpha Peak)')
plt.title('Frequency Domain Comparison (PSD)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power Spectral Density (dB)')
plt.legend()
plt.grid(True)
plt.xlim(0, 60)

plt.show()
print("Check point 2: Look at the PSD graph.")
print("  - 50 Hz Check: Is the peak at 50Hz gone in the Blue line?")
print("  - Alpha Check: Do you see a bump around 10Hz (Brain signal)?")
print("  - Shape Check: Does the curve generally go down (1/f shape)?")

print("\nStep 4 Complete.")
print("\n" + "=" * 30)
print("STARTING STEP 5: Per-Channel PSD (Logarithmic)")
print("=" * 30)

import math

fmin, fmax = 0.5, 60.0

print("Calculating PSDs for comparison...")

psd_raw_inst = raw.compute_psd(method='welch', fmin=fmin, fmax=fmax, picks='eeg', n_fft=int(sfreq * 2))
psds_raw, freqs = psd_raw_inst.get_data(return_freqs=True)


psd_clean_inst = epochs_final.compute_psd(method='welch', fmin=fmin, fmax=fmax, picks='eeg', n_fft=int(sfreq * 2))
psds_clean, _ = psd_clean_inst.get_data(return_freqs=True)
psds_clean_mean = psds_clean.mean(axis=0)

n_channels = len(epochs_final.ch_names)
n_cols = 4
n_rows = math.ceil(n_channels / n_cols)

fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 3 * n_rows), constrained_layout=True)
axes = axes.flatten()

for idx, ch_name in enumerate(epochs_final.ch_names):
    ax = axes[idx]

    raw_ch_idx = raw.ch_names.index(ch_name)
    clean_ch_idx = epochs_final.ch_names.index(ch_name)

    ax.plot(freqs, psds_raw[raw_ch_idx], color='red', alpha=0.6, linewidth=1, label='Before (Raw)')

    ax.plot(freqs, psds_clean_mean[clean_ch_idx], color='blue', alpha=0.8, linewidth=1.5, label='After (Clean)')

    ax.set_yscale('log')
    ax.set_title(ch_name, fontsize=10, fontweight='bold')
    ax.grid(True, which="both", ls="-", alpha=0.3)

    if idx >= (n_rows - 1) * n_cols:
        ax.set_xlabel('Frequency (Hz)')
    if idx % n_cols == 0:
        ax.set_ylabel(r'PSD (${\mu V^2}/{Hz}$)')

    ax.axvline(x=50, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)

for i in range(n_channels, len(axes)):
    axes[i].axis('off')

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', ncol=2, fontsize=12)
fig.suptitle('Per-Channel PSD: Before vs After Preprocessing', fontsize=16, y=1.02)

plt.show()

print("Step 5 Complete. Analysis:")
print("1. 50Hz Noise: Check if the sharp spike at 50Hz (in Red) is gone or reduced in Blue.")
print("2. Low Freq Drift: Check if the Red line is very high near 0-1 Hz and Blue is controlled.")
print("3. Signal Preservation: Ensure Blue follows Red shape in Alpha/Beta (8-30 Hz) and isn't zero.")


print("\n" + "=" * 30)
print("STARTING STEP 6: Plotting Topomaps (Theta, Alpha, Beta)")
print("=" * 30)

import matplotlib.pyplot as plt
import numpy as np
import mne

freq_bands = {
    "Theta (4-8 Hz)": (4, 8),
    "Alpha (8-12 Hz)": (8, 12),
    "Beta (12-30 Hz)": (12, 30)
}

print("Calculating Power Spectral Density (Welch)...")
spectrum = epochs_final.compute_psd(method='welch', fmin=1, fmax=40, n_fft=int(sfreq * 2))
psds, freqs = spectrum.get_data(return_freqs=True)
psds_mean = psds.mean(axis=0)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Spatial Distribution of Brain Rhythms (Power in dB)', fontsize=16)

for ax, (band_name, (fmin, fmax)) in zip(axes, freq_bands.items()):
    freq_indices = np.where((freqs >= fmin) & (freqs <= fmax))[0]
    band_power = psds_mean[:, freq_indices].mean(axis=1)

    band_power_db = 10 * np.log10(band_power)

    im, _ = mne.viz.plot_topomap(
        band_power_db,
        epochs_final.info,
        axes=ax,
        show=False,
        cmap='RdBu_r',
        names=epochs_final.ch_names,
        contours=6
    )

    ax.set_title(band_name)

cbar_ax = fig.add_axes([0.92, 0.15, 0.015, 0.7])
clb = fig.colorbar(im, cax=cbar_ax)
clb.set_label('Power Spectral Density (dB)')

print("Plotting complete. Check the new window.")
plt.show()

print("-" * 30)
print("INTERPRETATION GUIDE:")
print("1. Alpha Band: Look at the back of the head. Red means high relaxation.")
print("2. Theta Band: Red spots might indicate drowsiness.")
print("3. Beta Band: Usually lower power compared to Alpha.")
print("-" * 30)


print("\n" + "=" * 30)
print("STARTING STEP 7: Connectivity Analysis & Visualization")
print("=" * 30)

from mne_connectivity.viz import plot_connectivity_circle
from scipy.signal import hilbert

bands = {
    "Theta": (4, 8),
    "Alpha": (8, 12),
    "Beta": (12, 30)
}

node_names = epochs_final.ch_names

print("Why analyze connectivity on short epochs?")
print("  > Because EEG signals are non-stationary (change over time).")
print("  > Short epochs (e.g., 2s) can be considered 'quasi-stationary', making spectral analysis valid.\n")

for band_name, (l_freq, h_freq) in bands.items():
    print(f"--- Processing {band_name} Band ({l_freq}-{h_freq} Hz) ---")


    epochs_band = epochs_final.copy().filter(l_freq=l_freq, h_freq=h_freq, verbose=False)

    data = epochs_band.get_data()
    n_epochs, n_channels, n_times = data.shape

    analytic_signal = hilbert(data)
    envelope = np.abs(analytic_signal)

    envelope_concat = envelope.transpose(1, 0, 2).reshape(n_channels, -1)

    con_matrix = np.corrcoef(envelope_concat)

    np.fill_diagonal(con_matrix, 0)

    threshold = 0.4
    con_matrix_thresh = con_matrix.copy()
    con_matrix_thresh[np.abs(con_matrix_thresh) < threshold] = 0

    if np.all(con_matrix_thresh == 0):
        print(f"Warning: No connections found above threshold {threshold} for {band_name}.")
    else:
        print(f"Plotting Circle Plot for {band_name}...")

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        plot_connectivity_circle(
            con_matrix_thresh,
            node_names,
            n_lines=300,
            node_angles=None,
            node_colors=None,
            title=f'{band_name} Band Connectivity (Corr > {threshold})',
            fontsize_names=12,
            linewidth=1.5,
            show=False
        )
        plt.show()

print("\nStep 7 Complete.")
print("-" * 30)
print("INTERPRETATION GUIDE (تفسیر نتایج):")
print("1. Lines: Each line represents a strong functional connection between two brain regions.")
print("2. Clustering: If many lines connect to one point (e.g., 'Fz' or 'Oz'), that region is a 'Hub'.")
print("3. Comparison: Compare Alpha vs Beta.")
print("   - Alpha often shows strong posterior (back of head) connectivity during rest.")
print("   - Beta might show more frontal/central connections related to alertness.")
print("-" * 30)



print("\n" + "=" * 40)
print("STARTING STEP 8: Final Automated Diagnosis")
print("=" * 40)

import numpy as np
import matplotlib.pyplot as plt
import mne

print("Calculating Band Powers...")


spectrum = epochs_final.compute_psd(method='welch', fmin=3, fmax=35, n_fft=int(sfreq * 2))
psds, freqs = spectrum.get_data(return_freqs=True)


psds_mean = psds.mean(axis=0)


def get_band_power(psds, freqs, fmin, fmax):
    idx = np.logical_and(freqs >= fmin, freqs <= fmax)
    return psds_mean[:, idx].mean(axis=1)

theta_power = get_band_power(psds_mean, freqs, 4, 8)   # Theta (4-8 Hz)
alpha_power = get_band_power(psds_mean, freqs, 8, 12)  # Alpha (8-12 Hz)
beta_power  = get_band_power(psds_mean, freqs, 12, 30) # Beta (12-30 Hz)

drowsiness_index = alpha_power / beta_power

inattention_index = theta_power / beta_power

print("Indices calculated successfully.")


fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle('Automated Diagnostic Maps', fontsize=16, fontweight='bold')

im1, _ = mne.viz.plot_topomap(
    drowsiness_index,
    epochs_final.info,
    axes=axes[0],
    show=False,
    cmap='RdBu_r',
    names=epochs_final.ch_names,
    show_names=True,
    contours=6
)
axes[0].set_title('Drowsiness Index (Alpha/Beta)\nRed = Drowsy/Relaxed', fontsize=12)
plt.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)

im2, _ = mne.viz.plot_topomap(
    inattention_index,
    epochs_final.info,
    axes=axes[1],
    show=False,
    cmap='Wistia',
    names=epochs_final.ch_names,
    show_names=True,
    contours=6
)
axes[1].set_title('Inattention Index (Theta/Beta)\nDarker = Mind Wandering', fontsize=12)
plt.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04)

plt.tight_layout()
plt.show()


avg_ab_ratio = np.mean(drowsiness_index)
avg_tb_ratio = np.mean(inattention_index)

print("\n" + "*" * 50)
print("FINAL DIAGNOSIS REPORT")
print("*" * 50)

print(f"\n1. Drowsiness Index (Alpha/Beta): {avg_ab_ratio:.2f}")
if avg_ab_ratio > 1.5:
    print("   >> RESULT: Drowsy / Deeply Relaxed")
    print("   >> Explanation: Alpha waves constitute the dominant rhythm. Low alertness.")
elif avg_ab_ratio < 0.8:
    print("   >> RESULT: Highly Alert / Anxious")
    print("   >> Explanation: Beta waves are dominant. High mental activity or stress.")
else:
    print("   >> RESULT: Normal State")
    print("   >> Explanation: Balanced mental activity.")

print(f"\n2. Inattention Index (Theta/Beta): {avg_tb_ratio:.2f}")
if avg_tb_ratio > 2.0:
    print("   >> RESULT: Attention Deficit / Mind Wandering")
    print("   >> Explanation: High Theta indicates lack of focus or daydreaming.")
else:
    print("   >> RESULT: Good Focus / Normal Attention")
    print("   >> Explanation: Suitable balance between cognitive activity and rest.")

print("\n" + "*" * 50)