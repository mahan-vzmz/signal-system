import mne
import matplotlib.pyplot as plt
import glob
import os

output_folder = "Report_Images"
os.makedirs(output_folder, exist_ok=True)
print(f"Images will be saved in: {os.getcwd()}\\{output_folder}")

all_files = glob.glob("C:/Users/Victus 16/PycharmProjects/SignalSystem/subjects/Subject_*.edf")
all_files.sort()

low_cut = 0.5
high_cut = 45.0
notch_freq = 50.0

for file_path in all_files:
    subject_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"\nProcessing {subject_name}...")

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
        fig1 = raw.compute_psd(fmax=80).plot(show=False)
        plt.title(f"PSD Before Filter - {subject_name}")
        save_path_raw = os.path.join(output_folder, f"{subject_name}_PSD_Raw.png")
        plt.savefig(save_path_raw)
        plt.close(fig1)
        print(f"   -> Saved: {subject_name}_PSD_Raw.png")

        raw_processed = raw.copy().notch_filter(notch_freq, verbose=False)
        raw_processed.filter(low_cut, high_cut, verbose=False)

        fig2 = raw_processed.compute_psd(fmax=80).plot(show=False)
        plt.title(f"PSD After Filter - {subject_name}")
        save_path_filt = os.path.join(output_folder, f"{subject_name}_PSD_Filtered.png")
        plt.savefig(save_path_filt)
        plt.close(fig2)
        print(f"   -> Saved: {subject_name}_PSD_Filtered.png")

    except Exception as e:
        print(f"   !!! Error processing {subject_name}: {e}")

print("\nAll Done!.")
