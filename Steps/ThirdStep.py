import mne
import matplotlib.pyplot as plt
from autoreject import AutoReject
from mne.preprocessing import ICA
import glob
import os


input_folder = "C:/Users/Victus 16/PycharmProjects/SignalSystem/subjects/"
output_folder = "Report_Images_Step3_Auto"
os.makedirs(output_folder, exist_ok=True)

print(f"Images will be saved in: {os.getcwd()}\\{output_folder}")

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
    print(f"Processing: {subject_name}")
    print("=" * 50)

    try:
        raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)

        mapping = {name: name.replace('-LE', '') for name in raw.ch_names if '-LE' in name}
        raw.rename_channels(mapping)
        if 'Trig' in raw.ch_names: raw.set_channel_types({'Trig': 'stim'})

        try:
            raw.set_montage('standard_1020', match_case=False)
        except:
            pass

        raw.pick_types(eeg=True, eog=False, stim=False, exclude='bads')
        raw.notch_filter(notch_freq, verbose=False)
        raw.filter(low_cut, high_cut, verbose=False)

        epochs = mne.make_fixed_length_epochs(raw, duration=epoch_dur, preload=True, verbose=False)
        ar = AutoReject(n_interpolate=[1, 2], consensus=[0.6], random_state=42, verbose=False)
        epochs_clean = ar.fit_transform(epochs)

        print("   -> Fitting ICA...")
        ica = ICA(n_components=n_ica_components, max_iter='auto', random_state=97)
        ica.fit(epochs_clean, verbose=False)

        target_eog_channel = None
        for ch in ['Fp1', 'Fp2', 'Fz']:
            if ch in epochs_clean.ch_names:
                target_eog_channel = ch
                break

        if target_eog_channel:
            print(f"   -> Using '{target_eog_channel}' to detect artifacts.")
            eog_inds, scores = ica.find_bads_eog(epochs_clean, ch_name=target_eog_channel, threshold=3.0)

            ica.exclude = eog_inds
            print(f"   -> Components marked for removal: {eog_inds}")

            if eog_inds:
                fig_sc = ica.plot_scores(scores, exclude=eog_inds, show=False)
                fig_sc.savefig(os.path.join(output_folder, f"{subject_name}_ICA_Scores.png"))
                plt.close(fig_sc)
        else:
            print("   -> Warning: No frontal channel found.")

        fig_topo = ica.plot_components(show=False)
        fig_topo.savefig(os.path.join(output_folder, f"{subject_name}_ICA_Topomaps.png"))
        plt.close(fig_topo)
        print(f"   -> Saved Topomaps.")

        epochs_final = epochs_clean.copy()
        ica.apply(epochs_final, verbose=False)

        if target_eog_channel:
            fig_comp = plt.figure(figsize=(10, 5))
            data_orig = epochs_clean.get_data(picks=target_eog_channel)[0, 0, :]
            data_clean = epochs_final.get_data(picks=target_eog_channel)[0, 0, :]

            plt.plot(data_orig, color='red', alpha=0.5, label='Original (Artifact)')
            plt.plot(data_clean, color='blue', label='Cleaned (ICA)')
            plt.title(f"{subject_name}: ICA Effect on {target_eog_channel}")
            plt.legend()
            plt.tight_layout()

            fig_comp.savefig(os.path.join(output_folder, f"{subject_name}_Signal_Comparison.png"))
            plt.close(fig_comp)
            print(f"   -> Saved Signal Comparison.")

    except Exception as e:
        print(f"   !!! Error processing {subject_name}: {e}")

print("\n" + "=" * 50)
print("All Processing Done!")
print(f"Check folder: {output_folder}")