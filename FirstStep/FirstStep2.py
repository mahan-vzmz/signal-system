import mne
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import glob  # کتابخانه برای پیدا کردن فایل‌ها
import pandas as pd  # برای نمایش جدول زیبا


# --- تعریف تابع پردازش (پایپ‌لاین) ---
def process_single_subject(file_path):
    """
    این تابع آدرس فایل را می‌گیرد، تمام مراحل گام اول را انجام می‌دهد
    و اطلاعات کلیدی را برمی‌گرداند.
    """
    try:
        # 1. بارگذاری (بدون Preload سنگین، فقط هدر را می‌خوانیم تا سریع باشد، اما برای فیلتر preload لازم است)
        raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)

        # 2. اصلاح نام کانال‌ها و تایپ‌ها
        mapping = {name: name.replace('-LE', '') for name in raw.ch_names if '-LE' in name}
        raw.rename_channels(mapping)

        if 'Trig' in raw.ch_names:
            raw.set_channel_types({'Trig': 'stim'})

        # 3. تنظیم مونتاژ
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, match_case=False)
        except:
            pass  # اگر نشد، فعلا عبور کن

        # 4. انتخاب کانال‌های EEG
        raw.pick_types(eeg=True, eog=False, stim=False, exclude='bads')

        # 5. استخراج اطلاعات
        sfreq = raw.info['sfreq']
        duration = raw.times[-1]
        n_channels = len(raw.ch_names)

        # 6. اعمال فیلترها (فقط برای اطمینان از اینکه روی همه اجرا می‌شود)
        raw_processed = raw.copy().notch_filter(50.0, verbose=False)
        raw_processed.filter(0.5, 45.0, verbose=False)

        # برگرداندن اطلاعات به صورت دیکشنری
        return {
            "File Name": file_path,
            "Sampling Freq (Hz)": sfreq,
            "Duration (s)": duration,
            "Channels": n_channels,
            "Status": "Success"
        }

    except Exception as e:
        return {
            "File Name": file_path,
            "Sampling Freq (Hz)": None,
            "Duration (s)": None,
            "Channels": None,
            "Status": f"Error: {str(e)}"
        }


# --- اجرای حلقه روی تمام فایل‌ها ---

# لیست کردن تمام فایل‌هایی که با Subject شروع می‌شوند و پسوند edf دارند
# اگر فایل‌ها در پوشه دیگری هستند، مسیر را اصلاح کنید. مثلا: "Data/Subject_*.edf"
all_files = glob.glob("C:/Users/Victus 16/PycharmProjects/SignalSystem/subjects/Subject_*.edf")
all_files.sort()  # مرتب‌سازی به ترتیب نام

print(f"Found {len(all_files)} files. Starting Batch Processing...\n")

results = []

for file_path in all_files:
    print(f"Processing {file_path}...")
    # فراخوانی تابع بالا برای هر فایل
    stats = process_single_subject(file_path)
    results.append(stats)

# --- نمایش گزارش کلی ---
print("\n" + "=" * 50)
print("FINAL REPORT FOR ALL SUBJECTS")
print("=" * 50)

# تبدیل به دیتافریم پانداس برای نمایش تمیز جدول
df_results = pd.DataFrame(results)
print(df_results)

# ذخیره گزارش در اکسل یا CSV (اختیاری)
# df_results.to_csv("Step1_Report.csv", index=False)