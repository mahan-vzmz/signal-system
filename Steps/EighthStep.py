import mne
import numpy as np
import matplotlib.pyplot as plt
from autoreject import AutoReject
from mne.preprocessing import ICA
import glob
import os

input_folder = "C:/Users/Victus 16/PycharmProjects/SignalSystem/subjects/"
output_folder = "Report_Images_Step8_Diagnosis"
os.makedirs(output_folder, exist_ok=True)
print(f"Diagnosis Reports will be saved in: {os.getcwd()}\\{output_folder}")
report_file_path = os.path.join(output_folder, "Final_Diagnosis_Report.txt")
report_file = open(report_file_path, "w", encoding="utf-8")
report_file.write("=" * 50 + "\n")
report_file.write("   AUTOMATED BRAIN STATE DIAGNOSIS REPORT\n")
report_file.write("=" * 50 + "\n\n")
all_files = glob.glob(os.path.join(input_folder, "Subject_*.edf"))
all_files.sort()
low_cut = 0.5
high_cut = 45.0
notch_freq = 50.0
epoch_dur = 2.0
n_ica_components = 15

for file_path in all_files:
    subject_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"\n" + "=" * 60)
    print(f"Diagnosing Subject: {subject_name}")
    print("=" * 60)

    try:
        raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)
        mapping = {name: name.replace('-LE', '') for name in raw.ch_names if '-LE' in name}
        raw.rename_channels(mapping)
        if 'Trig' in raw.ch_names:
            raw.set_channel_types({'Trig': 'stim'})
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, match_case=False)
        except:
            print("   Warning: Standard montage not found. Skipping.")
            continue

        raw.pick_types(eeg=True, eog=False, stim=False, exclude='bads')
        raw.notch_filter(notch_freq, verbose=False)
        raw.filter(low_cut, high_cut, verbose=False)
        epochs = mne.make_fixed_length_epochs(raw, duration=epoch_dur, preload=True, verbose=False)
        ar = AutoReject(n_interpolate=[1, 2], consensus=[0.6], random_state=42, verbose=False)
        epochs_clean = ar.fit_transform(epochs)
        ica = ICA(n_components=n_ica_components, max_iter='auto', random_state=97)
        ica.fit(epochs_clean, verbose=False)
        eog_ch = 'Fp1' if 'Fp1' in epochs_clean.ch_names else epochs_clean.ch_names[0]
        try:
            eog_inds, _ = ica.find_bads_eog(epochs_clean, ch_name=eog_ch, threshold=2.5)
            if eog_inds:
                ica.exclude = eog_inds
        except:
            print(f"   Note: Could not auto-detect blinks with {eog_ch}")

        epochs_final = epochs_clean.copy()
        ica.apply(epochs_final, verbose=False)

        print("   -> Calculating Band Powers and Ratios...")

        spectrum = epochs_final.compute_psd(method='welch', fmin=3, fmax=35,
                                           n_fft=int(raw.info['sfreq'] * 2), verbose=False)
        psds, freqs = spectrum.get_data(return_freqs=True)
        psds_mean = psds.mean(axis=0)

        def get_band_power(f_low, f_high):
            idx = np.logical_and(freqs >= f_low, freqs <= f_high)
            return psds_mean[:, idx].mean(axis=1)

        theta = get_band_power(4, 8)
        alpha = get_band_power(8, 12)
        beta = get_band_power(12, 30)
        drowsiness_index = alpha / beta
        inattention_index = theta / beta
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle(f'Diagnostic Maps: {subject_name}', fontsize=16, fontweight='bold')
        im1, _ = mne.viz.plot_topomap(
            drowsiness_index,
            epochs_final.info,
            axes=axes[0],
            show=False,
            cmap='RdBu_r',
            names=epochs_final.ch_names,
            contours=6
        )
        axes[0].set_title('Drowsiness (Alpha/Beta)\nRed = Drowsy', fontsize=11)
        plt.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)
        im2, _ = mne.viz.plot_topomap(
            inattention_index,
            epochs_final.info,
            axes=axes[1],
            show=False,
            cmap='Wistia',
            names=epochs_final.ch_names,
            contours=6
        )
        axes[1].set_title('Inattention (Theta/Beta)\nDarker = Low Focus', fontsize=11)
        plt.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04)
        save_name = os.path.join(output_folder, f"{subject_name}_Diagnosis_Map.png")
        plt.savefig(save_name, bbox_inches='tight')
        plt.close(fig)
        print(f"   -> Saved Image: {subject_name}_Diagnosis_Map.png")
        avg_ab = np.mean(drowsiness_index)
        avg_tb = np.mean(inattention_index)
        report_text = f"Subject: {subject_name}\n"
        report_text += "-" * 30 + "\n"
        report_text += f"1. Drowsiness Index (Alpha/Beta): {avg_ab:.2f} -> "
        if avg_ab > 1.5:
            status_ab = "DROWSY / RELAXED (High Alpha)"
        elif avg_ab < 0.8:
            status_ab = "ALERT / ANXIOUS (High Beta)"
        else:
            status_ab = "NORMAL STATE"
        report_text += f"[{status_ab}]\n"

        report_text += f"2. Inattention Index (Theta/Beta): {avg_tb:.2f} -> "
        if avg_tb > 2.0:
            status_tb = "ATTENTION DEFICIT / MIND WANDERING (High Theta)"
        else:
            status_tb = "GOOD FOCUS (Normal)"
        report_text += f"[{status_tb}]\n\n"

        report_file.write(report_text)
        print(f"   -> Diagnosis: {status_ab} | {status_tb}")

    except Exception as e:
        print(f"   !!! Error processing {subject_name}: {e}")
        report_file.write(f"Subject: {subject_name}\nError: {e}\n\n")

report_file.close()

print("\n" + "=" * 60)
print("Step 8 Complete!")
print(f"1. Check images in: {output_folder}")
print(f"2. Read the full report: {report_file_path}")
