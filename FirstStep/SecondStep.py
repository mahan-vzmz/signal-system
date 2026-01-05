import mne
import numpy as np
import matplotlib.pyplot as plt
from autoreject import AutoReject
import glob
import os

# 1. تنظیم مسیرها و پوشه خروجی
# -----------------------------
input_folder = "C:/Users/Victus 16/PycharmProjects/SignalSystem/subjects/"
output_folder = "Report_Images_Step2"  # پوشه جدید برای عکس‌های گام دوم
os.makedirs(output_folder, exist_ok=True)

print(f"Images will be saved in: {os.getcwd()}\\{output_folder}")

# پیدا کردن تمام فایل‌های EDF
all_files = glob.glob(os.path.join(input_folder, "Subject_*.edf"))
all_files.sort()

# تنظیمات ثابت
low_cut = 0.5
high_cut = 45.0
notch_freq = 50.0
epoch_dur = 2.0

# فایل متنی برای ذخیره لیست کانال‌های خراب (برای جدول گزارش کار)
log_file = open(os.path.join(output_folder, "Bad_Channels_Summary.txt"), "w")

# ==========================================
# شروع پردازش روی ۱۰ فایل
# ==========================================
for file_path in all_files:
    subject_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"\n" + "=" * 40)
    print(f"Processing: {subject_name}")
    print("=" * 40)

    try:
        # --- الف) بارگذاری و پیش‌پردازش اولیه (مثل قبل) ---
        raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)

        # اصلاح نام کانال‌ها
        mapping = {name: name.replace('-LE', '') for name in raw.ch_names if '-LE' in name}
        raw.rename_channels(mapping)

        # تنظیم Trig و Montage
        if 'Trig' in raw.ch_names:
            raw.set_channel_types({'Trig': 'stim'})

        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, match_case=False)
        except:
            print("Warning: Montage not set.")

        raw.pick_types(eeg=True, eog=False, stim=False, exclude='bads')

        # اعمال فیلتر (AutoReject نیاز به داده نسبتاً تمیز دارد)
        raw.notch_filter(notch_freq, verbose=False)
        raw.filter(low_cut, high_cut, verbose=False)

        # --- ب) قطعه‌بندی (Epoching) ---
        epochs = mne.make_fixed_length_epochs(raw, duration=epoch_dur, preload=True, verbose=False)
        print(f"   -> Created {len(epochs)} epochs.")

        # --- ج) اجرای AutoReject ---
        print("   -> Running AutoReject...")
        ar = AutoReject(n_interpolate=[1, 2, 4], consensus=[0.5, 0.7], random_state=42, verbose=False)
        epochs_clean, reject_log = ar.fit_transform(epochs, return_log=True)

        # --- د) ذخیره نمودار Heatmap ---
        fig_heat = reject_log.plot(orientation='horizontal', show=False)
        plt.suptitle(f"AutoReject Heatmap - {subject_name}")

        save_path_heat = os.path.join(output_folder, f"{subject_name}_Heatmap.png")
        plt.savefig(save_path_heat)
        plt.close(fig_heat)  # بستن پنجره برای آزاد شدن رم
        print(f"   -> Saved Heatmap: {subject_name}_Heatmap.png")

        # --- هـ) پیدا کردن کانال‌های سراسری خراب (Global Bad Channels) ---
        labels = reject_log.labels
        n_epochs = labels.shape[0]
        bad_channels = []
        threshold = 0.70  # قانون 70 درصد

        for i, ch_name in enumerate(epochs.ch_names):
            # محاسبه درصد خرابی
            bad_count = np.sum((labels[:, i] == 1) | (labels[:, i] == 2))
            if (bad_count / n_epochs) > threshold:
                bad_channels.append(ch_name)

        # اگر لیست خالی بود ولی می‌خواهیم برای تست چیزی نشان دهیم (مثل مثال قبلی)
        # در اینجا فقط واقعیت را ثبت می‌کنیم
        log_msg = f"{subject_name}: {bad_channels if bad_channels else 'None'}"
        print(f"   -> {log_msg}")
        log_file.write(log_msg + "\n")

        # --- و) ذخیره نمودار سنسورها (Topomap) ---
        # نکته: اگر کانال بدی باشد، با رنگ متفاوت نشان داده می‌شود
        epochs_clean.info['bads'] = bad_channels  # ست کردن کانال‌های بد پیدا شده
        fig_sensor = epochs_clean.plot_sensors(show_names=True, title=f"Sensors - {subject_name}", show=False)

        save_path_sensor = os.path.join(output_folder, f"{subject_name}_Sensors.png")
        fig_sensor.savefig(save_path_sensor)
        plt.close(fig_sensor)
        print(f"   -> Saved Sensor Map: {subject_name}_Sensors.png")

    except Exception as e:
        print(f"   !!! Error processing {subject_name}: {e}")

log_file.close()
print("\n" + "=" * 40)
print("All Processing Done!")
print(f"Check folder: {output_folder}")