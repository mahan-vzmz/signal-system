import mne
import matplotlib.pyplot as plt
from scipy import signal
import glob
import os

# 1. ساخت پوشه برای ذخیره عکس‌ها
output_folder = "Report_Images"
os.makedirs(output_folder, exist_ok=True)
print(f"Images will be saved in: {os.getcwd()}\\{output_folder}")

# 2. پیدا کردن تمام فایل‌های داده
all_files = glob.glob("C:/Users/Victus 16/PycharmProjects/signal&system/subjects/Subject_*.edf")
all_files.sort()

# تنظیمات فیلتر (ثابت برای همه)
low_cut = 0.5
high_cut = 45.0
notch_freq = 50.0

for file_path in all_files:
    # استخراج نام فایل بدون پسوند (مثلاً Subject_01)
    subject_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"\nProcessing {subject_name}...")

    try:
        # --- الف) بارگذاری و اصلاح ---
        raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)

        # اصلاح نام کانال‌ها (حذف -LE)
        mapping = {name: name.replace('-LE', '') for name in raw.ch_names if '-LE' in name}
        raw.rename_channels(mapping)

        # تنظیم Trig
        if 'Trig' in raw.ch_names:
            raw.set_channel_types({'Trig': 'stim'})

        # تنظیم مونتاژ
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, match_case=False)
        except:
            pass

        # انتخاب کانال‌های EEG
        raw.pick_types(eeg=True, eog=False, stim=False, exclude='bads')

        # --- ب) رسم و ذخیره PSD خام ---
        fig1 = raw.compute_psd(fmax=80).plot(show=False)  # show=False یعنی پنجره باز نشود
        plt.title(f"PSD Before Filter - {subject_name}")
        # ذخیره عکس
        save_path_raw = os.path.join(output_folder, f"{subject_name}_PSD_Raw.png")
        plt.savefig(save_path_raw)
        plt.close(fig1)  # بستن نمودار برای آزادسازی حافظه
        print(f"   -> Saved: {subject_name}_PSD_Raw.png")

        # --- ج) اعمال فیلتر ---
        raw_processed = raw.copy().notch_filter(notch_freq, verbose=False)
        raw_processed.filter(low_cut, high_cut, verbose=False)

        # --- د) رسم و ذخیره PSD فیلتر شده ---
        fig2 = raw_processed.compute_psd(fmax=80).plot(show=False)
        plt.title(f"PSD After Filter - {subject_name}")
        # ذخیره عکس
        save_path_filt = os.path.join(output_folder, f"{subject_name}_PSD_Filtered.png")
        plt.savefig(save_path_filt)
        plt.close(fig2)
        print(f"   -> Saved: {subject_name}_PSD_Filtered.png")

    except Exception as e:
        print(f"   !!! Error processing {subject_name}: {e}")

print("\nAll Done! Check the 'Report_Images' folder.")