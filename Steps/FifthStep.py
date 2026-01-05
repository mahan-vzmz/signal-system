import mne
import numpy as np
import matplotlib.pyplot as plt
from autoreject import AutoReject
from mne.preprocessing import ICA
import glob
import os
import math

# ==========================================
# تنظیمات اولیه و مسیرها
# ==========================================
input_folder = "C:/Users/Victus 16/PycharmProjects/SignalSystem/subjects/"
output_folder = "Report_Images_Step5_PSD"  # پوشه خروجی عکس‌های گام ۵
os.makedirs(output_folder, exist_ok=True)

print(f"PSD Comparison Images will be saved in: {os.getcwd()}\\{output_folder}")

# پیدا کردن تمام فایل‌های EDF
all_files = glob.glob(os.path.join(input_folder, "Subject_*.edf"))
all_files.sort()

# پارامترهای پردازش
low_cut = 0.5
high_cut = 45.0
notch_freq = 50.0
epoch_dur = 2.0
n_ica_components = 15
fmin, fmax = 0.5, 60.0  # محدوده فرکانسی نمودار PSD

# ==========================================
# شروع حلقه پردازش روی ۱۰ فایل
# ==========================================
for file_path in all_files:
    subject_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"\n" + "=" * 60)
    print(f"Processing Per-Channel PSD for: {subject_name}")
    print("=" * 60)

    try:
        # ---------------------------------------------------------
        # 1. بارگذاری داده و آماده‌سازی اولیه
        # ---------------------------------------------------------
        raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)

        # اصلاح نام کانال‌ها
        mapping = {name: name.replace('-LE', '') for name in raw.ch_names if '-LE' in name}
        raw.rename_channels(mapping)
        if 'Trig' in raw.ch_names: raw.set_channel_types({'Trig': 'stim'})

        try:
            raw.set_montage('standard_1020', match_case=False)
        except:
            pass

        raw.pick_types(eeg=True, eog=False, stim=False, exclude='bads')

        # *** محاسبه PSD برای داده خام (قبل از هر فیلتری) ***
        # این همان خط قرمز (Before) در نمودار خواهد بود
        print("   -> Calculating Raw PSD...")
        psd_raw_inst = raw.compute_psd(method='welch', fmin=fmin, fmax=fmax, picks='eeg',
                                       n_fft=int(raw.info['sfreq'] * 2), verbose=False)
        psds_raw, freqs = psd_raw_inst.get_data(return_freqs=True)
        # psds_raw shape: (n_channels, n_freqs)

        # ---------------------------------------------------------
        # 2. اعمال پایپ‌لاین تمیزسازی (Cleaning Pipeline)
        # ---------------------------------------------------------
        # الف) فیلتر فرکانسی
        raw.notch_filter(notch_freq, verbose=False)
        raw.filter(low_cut, high_cut, verbose=False)

        # ب) اپوک‌بندی
        epochs = mne.make_fixed_length_epochs(raw, duration=epoch_dur, preload=True, verbose=False)

        # ج) AutoReject
        ar = AutoReject(n_interpolate=[1, 2], consensus=[0.6], random_state=42, verbose=False)
        epochs_clean = ar.fit_transform(epochs)

        # د) ICA (حذف پلک)
        ica = ICA(n_components=n_ica_components, max_iter='auto', random_state=97)
        ica.fit(epochs_clean, verbose=False)
        # حذف اتوماتیک با Fp1
        eog_inds, _ = ica.find_bads_eog(epochs_clean, ch_name='Fp1', threshold=2.5)
        if eog_inds:
            ica.exclude = eog_inds

        epochs_final = epochs_clean.copy()
        ica.apply(epochs_final, verbose=False)

        # *** محاسبه PSD برای داده نهایی (بعد از تمیزسازی) ***
        # این همان خط آبی (After) در نمودار خواهد بود
        print("   -> Calculating Clean PSD...")
        psd_clean_inst = epochs_final.compute_psd(method='welch', fmin=fmin, fmax=fmax, picks='eeg',
                                                  n_fft=int(raw.info['sfreq'] * 2), verbose=False)
        psds_clean, _ = psd_clean_inst.get_data(return_freqs=True)
        # میانگین‌گیری روی اپوک‌ها برای رسیدن به (n_channels, n_freqs)
        psds_clean_mean = psds_clean.mean(axis=0)

        # ---------------------------------------------------------
        # 3. رسم نمودار شبکه‌ای (Grid Plot)
        # ---------------------------------------------------------
        print("   -> Generating Plot...")

        n_channels = len(epochs_final.ch_names)
        n_cols = 4
        n_rows = math.ceil(n_channels / n_cols)

        # ابعاد تصویر را بر اساس تعداد ردیف داینامیک می‌کنیم
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 3.5 * n_rows), constrained_layout=True)
        axes = axes.flatten()

        for idx, ch_name in enumerate(epochs_final.ch_names):
            ax = axes[idx]

            # پیدا کردن اندیس کانال در داده Raw (چون ممکن است ترتیب فرق کرده باشد یا کانالی حذف شده باشد)
            if ch_name in raw.ch_names:
                raw_ch_idx = raw.ch_names.index(ch_name)
                # رسم داده خام (قرمز)
                ax.plot(freqs, psds_raw[raw_ch_idx], color='red', alpha=0.6, linewidth=1, label='Before (Raw)')

            # پیدا کردن اندیس در داده Clean
            clean_ch_idx = epochs_final.ch_names.index(ch_name)
            # رسم داده تمیز (آبی)
            ax.plot(freqs, psds_clean_mean[clean_ch_idx], color='blue', alpha=0.8, linewidth=1.5, label='After (Clean)')

            # تنظیمات ظاهری
            ax.set_yscale('log')
            ax.set_title(ch_name, fontsize=11, fontweight='bold')
            ax.grid(True, which="both", ls="-", alpha=0.3)

            # لیبل‌ها فقط در حاشیه
            if idx >= (n_rows - 1) * n_cols:
                ax.set_xlabel('Frequency (Hz)')
            if idx % n_cols == 0:
                # استفاده از r'' برای جلوگیری از وارنینگ لاتک
                ax.set_ylabel(r'PSD (${\mu V^2}/{Hz}$)')

            # خط چین ۵۰ هرتز
            ax.axvline(x=50, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)

        # مخفی کردن محورهای خالی
        for i in range(n_channels, len(axes)):
            axes[i].axis('off')

        # لجند و عنوان کلی
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper center', ncol=2, fontsize=12, bbox_to_anchor=(0.5, 1.02))
        fig.suptitle(f'Per-Channel PSD Analysis: {subject_name}', fontsize=16, y=1.03)

        # ذخیره تصویر
        save_name = os.path.join(output_folder, f"{subject_name}_Channel_PSD.png")
        plt.savefig(save_name, bbox_inches='tight')
        plt.close(fig)  # آزادسازی حافظه

        print(f"   -> Saved: {subject_name}_Channel_PSD.png")

    except Exception as e:
        print(f"   !!! Error processing {subject_name}: {e}")

print("\n" + "=" * 60)
print("Step 5 Processing Complete!")
print(f"Check folder: {output_folder}")