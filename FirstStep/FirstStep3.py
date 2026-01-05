import mne
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# 1. بارگذاری داده‌ها
# توجه: فایل شما edf است، پس از read_raw_edf استفاده می‌کنیم
raw = mne.io.read_raw_edf("C:/Users/Victus 16/PycharmProjects/SignalSystem/subjects/Subject_01.edf", preload=True)

mapping = {name: name.replace('-LE', '') for name in raw.ch_names if '-LE' in name}
raw.rename_channels(mapping)
print("New channel names:", raw.ch_names)

# --- رفع مشکل کانال Trig ---
# کانال Trig را به عنوان کانال Stimulus (تحریک) معرفی می‌کنیم تا MNE آن را به عنوان سیگنال مغزی پردازش نکند
# اگر اسم کانال در فایل شما دقیقاً 'Trig' است:
if 'Trig' in raw.ch_names:
    raw.set_channel_types({'Trig': 'stim'})
    print("Channel 'Trig' set to stimulus type.")
else:
    # گاهی اوقات اسمش متفاوت است، لیست کانال‌ها را چاپ می‌کنیم تا ببینیم
    print("Channel names found:", raw.ch_names)

# --- رفع مشکل مکان کانال‌ها (Montage) ---
# تنظیم مونتاژ استاندارد 10-20 (برای اینکه نقشه سر را بشناسد)
# این کار وارنینگ Channel locations را رفع می‌کند
try:
    montage = mne.channels.make_standard_montage('standard_1020')
    raw.set_montage(montage, match_case=False) # match_case=False برای نادیده گرفتن بزرگی/کوچکی حروف
except ValueError:
    print("Warning: Channel names do not match standard 10-20 system. Skipping montage.")

# انتخاب فقط کانال‌های EEG برای پردازش‌های بعدی
raw.pick_types(eeg=True, eog=False, stim=False, exclude='bads')

# 2. استخراج اطلاعات
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

# مشاهده سیگنال در حوزه زمان
# پارامتر block=True باعث می‌شود پنجره باز بماند تا وقتی که شما آن را ببندید
raw.plot(duration=5,              # نمایش بازه‌های ۵ ثانیه‌ای
         n_channels=20,           # تعداد کانال‌هایی که نشان می‌دهد
         scalings='auto',         # تنظیم خودکار مقیاس برای دیده شدن بهتر
         title="Raw EEG Signal",
         block=True)              # این خط برای PyCharm حیاتی است!

# 3. طراحی فیلتر و رسم نمودار بُد (بدون تغییر نسبت به قبل)
low_cut = 0.5
high_cut = 45.0
fs = sfreq

# طراحی فیلتر
numtaps = int(fs)
if numtaps % 2 == 0: numtaps += 1
taps = signal.firwin(numtaps, [low_cut, high_cut], pass_zero=False, fs=fs)
w, h = signal.freqz(taps, 1, worN=2000, fs=fs)

# رسم نمودار بُد
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

# 4. تحلیل طیفی (PSD) و اعمال فیلتر
# نکته مهم: حالا که Trig را از نوع stim کردیم و pick_types زدیم، دیگر در PSD نمی‌آید و ارور نمی‌دهد.

print("Plotting PSD of RAW data (Original)...")
# تذکر: fmax را کمی بالاتر می‌گیریم تا ببینیم نویز کجاست
raw.compute_psd(fmax=80).plot()
plt.show() # برای اطمینان از نمایش در محیط‌های غیر تعاملی

# اعمال فیلترها
# کپی می‌گیریم تا داده اصلی خراب نشود
raw_processed = raw.copy()

# الف) ناچ فیلتر (برق شهر) - معمولا 50 هرتز
raw_processed.notch_filter(freqs=50.0)

# ب) فیلتر میان‌گذر (0.5 تا 45)
raw_processed.filter(l_freq=0.5, h_freq=45.0)

print("Plotting PSD of FILTERED data...")
raw_processed.compute_psd(fmax=80).plot()
plt.show()

# ==========================================
# Ghasem Step 2: Epoching & Artifact Rejection
# ==========================================
print("\n" + "=" * 30)
print("STARTING STEP 2: Epoching & AutoReject")
print("=" * 30)

import matplotlib.pyplot as plt
from autoreject import AutoReject
import pandas as pd  # برای نمایش تمیز آمار

# ---------------------------------------------------------
# 1. قطعه‌بندی سیگنال (Epoching)
# طبق دستور: سیگنال پیوسته را به قطعات مساوی 2 ثانیه‌ای تقسیم کنید.
# ---------------------------------------------------------
epoch_duration = 2.0
epochs = mne.make_fixed_length_epochs(raw_processed, duration=epoch_duration, preload=True)

print(f"\nCreated {len(epochs)} epochs of {epoch_duration} seconds each.")

# ---------------------------------------------------------
# 2. شناسایی هوشمند داده‌های خراب (AutoReject)
# طبق دستور: استفاده از الگوریتم برای تعیین بخش‌های خوب/بد/قابل ترمیم
# ---------------------------------------------------------
print("Running AutoReject (this may take a minute)...")

# ایجاد شیء AutoReject
# n_interpolate: تعداد کانال‌هایی که اجازه داریم در هر اپوک ترمیم کنیم (معمولا مقادیر مختلف تست می‌شود)
# consensus: درصد کانال‌هایی که اگر خراب باشند، کل اپوک دور ریخته می‌شود
ar = AutoReject(n_interpolate=[1, 2, 4], consensus=[0.5, 0.7], random_state=42, verbose=False)

# فیت کردن روی داده‌ها و تمیز کردن آن‌ها
epochs_clean, reject_log = ar.fit_transform(epochs, return_log=True)

# رسم ماتریس وضعیت (Heatmap)
# طبق دستور: سبز (سالم)، قرمز (بد/حذف)، آبی (ترمیم شده)
print("Plotting AutoReject Heatmap...")
reject_log.plot(orientation='horizontal')
plt.suptitle("AutoReject Log (Heatmap)")
plt.show()

# ---------------------------------------------------------
# 3. شناسایی و حذف کانال‌های معیوب (Global Bad Channels)
# طبق دستور: قانون 70 درصد. اگر کانالی در بیش از 70 درصد اپوک‌ها بد بود -> کانال معیوب است.
# ---------------------------------------------------------

# ماتریس برچسب‌ها: (تعداد اپوک‌ها × تعداد کانال‌ها)
# 0: خوب، 1: بد، 2: اینترپوله شده
labels = reject_log.labels
n_epochs, n_channels = labels.shape

bad_channels_detected = []
threshold_percentage = 0.70  # 70%

print("\n--- Channel Statistics ---")
for i, ch_name in enumerate(epochs.ch_names):
    # محاسبه تعداد دفعاتی که این کانال در اپوک‌ها "بد" (1) یا "ترمیم" (2) تشخیص داده شده
    # نکته: معمولا AutoReject خودش کانال‌های خیلی خراب را پیدا می‌کند، اما اینجا دستی چک می‌کنیم
    # در reject_log، عدد 1 یعنی "بد" (Bad) و عدد 2 یعنی "ترمیم شده" (Interpolated)
    # کانالی که کلاً خرابه، معمولاً در اکثر اپوک‌ها وضعیت 1 یا 2 می‌گیره.
    bad_count = np.sum((labels[:, i] == 1) | (labels[:, i] == 2))
    bad_ratio = bad_count / n_epochs

    if bad_ratio > threshold_percentage:
        print(f"Channel {ch_name}: {bad_ratio * 100:.1f}% bad epochs -> MARKED AS BAD")
        bad_channels_detected.append(ch_name)

# اضافه کردن کانال‌های بد شناسایی شده به لیست bads سیگنال
epochs_clean.info['bads'].extend(bad_channels_detected)
# حذف تکراری‌ها
epochs_clean.info['bads'] = list(set(epochs_clean.info['bads']))

print(f"\nFinal list of Bad Channels: {epochs_clean.info['bads']}")

# ---------------------------------------------------------
# 4. درون‌یابی کانال‌ها (Channel Interpolation)
# طبق دستور: کانال‌های معیوب را با استفاده از همسایه‌ها بازسازی کنید.
# ---------------------------------------------------------
print("Interpolating bad channels...")
# این متد تمام کانال‌هایی که در info['bads'] هستند را بازسازی می‌کند
epochs_clean.interpolate_bads(reset_bads=True)

# ---------------------------------------------------------
# 5. مقایسه تصویری (Visual Comparison)
# ---------------------------------------------------------

# الف) رسم Topomap سنسورها (نشان دادن مکان سنسورها)
print("Plotting Sensor Locations...")
epochs_clean.plot_sensors(show_names=True, title="Sensor Locations")
plt.show()

# ب) رسم سیگنال نهایی (تمیز شده)
# برای مشاهده اینکه آیا خطوط صاف (Flat) یا نویزی اصلاح شده‌اند
print("Plotting Final Cleaned Epochs...")
epochs_clean.plot(n_epochs=3, n_channels=len(epochs.ch_names), title="Cleaned EEG Signal", block=True)