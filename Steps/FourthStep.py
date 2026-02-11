import mne
import numpy as np
import matplotlib.pyplot as plt
from autoreject import AutoReject
from mne.preprocessing import ICA
import glob
import os

input_folder = "C:/Users/Victus 16/PycharmProjects/SignalSystem/subjects/"
output_folder = "Report_Images_Step4_Final"
os.makedirs(output_folder, exist_ok=True)

print(f"Final Comparison Images will be saved in: {os.getcwd()}\\{output_folder}")

all_files = glob.glob(os.path.join(input_folder, "Subject_*.edf"))
all_files.sort()

low_cut = 0.5
high_cut = 45.0
notch_freq = 50.0
epoch_dur = 2.0
n_ica_components = 15


for file_path in all_files:
    subject_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"\n" + "=" * 50)
    print(f"Generating Final Report for: {subject_name}")
    print("=" * 50)

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
            pass

        raw.pick_types(eeg=True, eog=False, stim=False, exclude='bads')

        raw_for_plot = raw.copy()

        raw.notch_filter(notch_freq, verbose=False)
        raw.filter(low_cut, high_cut, verbose=False)

        epochs = mne.make_fixed_length_epochs(raw, duration=epoch_dur, preload=True, verbose=False)

        ar = AutoReject(n_interpolate=[1, 2], consensus=[0.6], random_state=42, verbose=False)
        epochs_clean = ar.fit_transform(epochs)

        ica = ICA(n_components=n_ica_components, max_iter='auto', random_state=97)
        ica.fit(epochs_clean)


        eog_inds, _ = ica.find_bads_eog(epochs_clean, ch_name='Fp1', threshold=2.5)

        if eog_inds:
            ica.exclude = eog_inds
            print(f"   -> Automatically removed blink components: {eog_inds}")
        else:
            print("   -> No blink components found automatically.")

        epochs_final = epochs_clean.copy()
        ica.apply(epochs_final)


        print("   -> Creating Comparison Plots...")

        fig = plt.figure(figsize=(14, 10))

        target_ch = [ch for ch in epochs_final.ch_names if 'Fp1' in ch]
        picked_ch = target_ch[0] if target_ch else epochs_final.ch_names[0]

        raw_data_plot, times_raw = raw_for_plot.get_data(picks=picked_ch, start=0, stop=int(6 * raw.info['sfreq']),
                                                         return_times=True)
        raw_data_plot = raw_data_plot[0]

        clean_data_plot = epochs_final.get_data(picks=picked_ch, copy=True)[0:3, 0, :].flatten()
        times_clean = np.linspace(0, 6, len(clean_data_plot))

        ax1 = fig.add_subplot(3, 1, 1)
        ax1.plot(times_raw, raw_data_plot, color='red', alpha=0.8, linewidth=1)
        ax1.set_title(f"1. Raw Data (Subject: {subject_name} - Ch: {picked_ch})")
        ax1.set_ylabel("Amplitude")
        ax1.grid(True, linestyle='--', alpha=0.5)

        ax2 = fig.add_subplot(3, 1, 2)
        ax2.plot(times_clean, clean_data_plot, color='blue', linewidth=1)
        ax2.set_title("2. Final Clean Data (Filtered + AutoReject + ICA)")
        ax2.set_ylabel("Amplitude")
        ax2.grid(True, linestyle='--', alpha=0.5)

        ax3 = fig.add_subplot(3, 1, 3)

        spect_raw = raw_for_plot.compute_psd(fmax=60, picks='eeg')
        psds_raw, freqs = spect_raw.get_data(return_freqs=True)
        psd_raw_mean = 10 * np.log10(psds_raw.mean(axis=0))

        spect_clean = epochs_final.compute_psd(fmax=60, picks='eeg')
        psds_clean, freqs_c = spect_clean.get_data(return_freqs=True)
        psd_clean_mean = 10 * np.log10(psds_clean.mean(axis=0).mean(axis=0))

        ax3.plot(freqs, psd_raw_mean, color='red', linestyle='--', label='Raw Data', alpha=0.7)
        ax3.plot(freqs_c, psd_clean_mean, color='blue', label='Final Clean Data', linewidth=2)

        ax3.axvline(x=50, color='gray', linestyle=':', label='50Hz Noise')
        ax3.axvline(x=10, color='green', linestyle=':', label='10Hz Alpha')

        ax3.set_title("3. Frequency Domain Comparison (PSD)")
        ax3.set_xlabel("Frequency (Hz)")
        ax3.set_ylabel("Power (dB)")
        ax3.legend()
        ax3.grid(True)
        ax3.set_xlim(0, 60)

        plt.tight_layout()
        save_name = os.path.join(output_folder, f"Report_Step4_{subject_name}.png")
        plt.savefig(save_name, dpi=100)
        plt.close(fig)

        print(f"   -> Saved Report: Report_Step4_{subject_name}.png")

    except Exception as e:
        print(f"   !!! Error processing {subject_name}: {e}")

print("\n" + "=" * 50)
print("All Final Reports Generated Successfully!")
print(f"Check the folder: {output_folder}")