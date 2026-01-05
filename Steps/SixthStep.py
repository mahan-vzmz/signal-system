import mne
import numpy as np
import matplotlib.pyplot as plt
from autoreject import AutoReject
from mne.preprocessing import ICA
import glob
import os

# ==========================================
# 1. تنظیمات مسیرها و پوشه خروجی
# ==========================================
input_folder = "C:/Users/Victus 16/PycharmProjects/SignalSystem/subjects/"
output_folder = "Report_Images_Step6_Topomaps"  # پوشه خروجی جدید
os.makedirs(output_folder, exist_ok=True)

print(f"Topomap Images will be saved in: {os.getcwd()}\\{output_folder}")

# پیدا کردن تمام فایل‌های EDF
all_files = glob.glob(os.path.join(input_folder, "Subject_*.edf"))
all_files.sort()

# پارامترهای پردازش
low_cut = 0.5
high_cut = 45.0
notch_freq = 50.0
epoch_dur = 2.0
n_ica_components = 15

# تعریف باندهای فرکانسی
freq_bands = {
    "Theta (4-8 Hz)": (4, 8),
    "Alpha (8-12 Hz)": (8, 12),
    "Beta (12-30 Hz)": (12, 30)
}

# ==========================================
# شروع حلقه پردازش روی تمام فایل‌ها
# ==========================================
for file_path in all_files:
    subject_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"\n" + "=" * 60)
    print(f"Processing Topomaps for: {subject_name}")
    print("=" * 60)

    try:
        # ---------------------------------------------------------
        # 1. بارگذاری و پیش‌پردازش اولیه
        # ---------------------------------------------------------
        raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)

        # اصلاح نام کانال‌ها
        mapping = {name: name.replace('-LE', '') for name in raw.ch_names if '-LE' in name}
        raw.rename_channels(mapping)
        if 'Trig' in raw.ch_names: raw.set_channel_types({'Trig': 'stim'})

        # تنظیم مکان سنسورها
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, match_case=False)
        except ValueError:
            print("   !!! Warning: Standard 10-20 montage not found. Skipping plot.")
            continue

        raw.pick_types(eeg=True, eog=False, stim=False, exclude='bads')

        # ---------------------------------------------------------
        # 2. پایپ‌لاین تمیزسازی
        # ---------------------------------------------------------
        # الف) فیلترها
        raw.notch_filter(notch_freq, verbose=False)
        raw.filter(low_cut, high_cut, verbose=False)

        # ب) اپوک‌بندی
        epochs = mne.make_fixed_length_epochs(raw, duration=epoch_dur, preload=True, verbose=False)

        # ج) AutoReject
        ar = AutoReject(n_interpolate=[1, 2], consensus=[0.6], random_state=42, verbose=False)
        epochs_clean = ar.fit_transform(epochs)

        # د) ICA
        ica = ICA(n_components=n_ica_components, max_iter='auto', random_state=97)
        ica.fit(epochs_clean, verbose=False)

        eog_inds, _ = ica.find_bads_eog(epochs_clean, ch_name='Fp1', threshold=2.5)
        if eog_inds:
            ica.exclude = eog_inds

        epochs_final = epochs_clean.copy()
        ica.apply(epochs_final, verbose=False)

        # ---------------------------------------------------------
        # 3. محاسبات طیفی و رسم نقشه‌ها
        # ---------------------------------------------------------
        print("   -> Calculating PSD and generating Topomaps...")

        # محاسبه PSD
        spectrum = epochs_final.compute_psd(method='welch', fmin=1, fmax=40, n_fft=int(raw.info['sfreq'] * 2),
                                            verbose=False)
        psds, freqs = spectrum.get_data(return_freqs=True)

        # میانگین‌گیری
        psds_mean = psds.mean(axis=0)

        # ایجاد شکل نمودار
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        fig.suptitle(f'Spatial Distribution of Brain Rhythms: {subject_name}', fontsize=16)

        # حلقه روی باندهای فرکانسی
        for ax, (band_name, (fmin, fmax)) in zip(axes, freq_bands.items()):
            freq_indices = np.where((freqs >= fmin) & (freqs <= fmax))[0]
            band_power = psds_mean[:, freq_indices].mean(axis=1)
            band_power_db = 10 * np.log10(band_power)

            # --- بخش اصلاح شده ---
            # پارامتر show_names حذف شد
            im, _ = mne.viz.plot_topomap(
                band_power_db,
                epochs_final.info,
                axes=ax,
                show=False,
                cmap='RdBu_r',
                names=epochs_final.ch_names,
                # نام‌ها پاس داده می‌شوند اما نمایش داده نمی‌شوند مگر اینکه پارامتر دیگری تنظیم شود
                contours=6
            )
            ax.set_title(band_name, fontsize=12)

        # اضافه کردن Colorbar
        cbar_ax = fig.add_axes([0.92, 0.15, 0.015, 0.7])
        clb = fig.colorbar(im, cax=cbar_ax)
        clb.set_label('Power Spectral Density (dB)')

        # ذخیره تصویر
        save_name = os.path.join(output_folder, f"{subject_name}_Topomaps.png")
        plt.savefig(save_name, bbox_inches='tight')
        plt.close(fig)

        print(f"   -> Saved: {subject_name}_Topomaps.png")

    except Exception as e:
        print(f"   !!! Error processing {subject_name}: {e}")

print("\n" + "=" * 60)
print("Step 6 Processing Complete!")
print(f"Check folder: {output_folder}")