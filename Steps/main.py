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

# ==========================================
# Ghasem Step 3 (AUTOMATED): Artifact Removal using ICA
# ==========================================
print("\n" + "=" * 30)
print("STARTING STEP 3: Automated ICA (EOG Removal)")
print("=" * 30)

from mne.preprocessing import ICA

# 1. تنظیم و آموزش ICA
ica = ICA(n_components=15, max_iter='auto', random_state=97)

print("Fitting ICA to cleaned epochs...")
ica.fit(epochs_clean)

# 2. شناسایی اتوماتیک مولفه‌های چشم (EOG)
# استراتژی: استفاده از کانال Fp1 یا Fp2 به عنوان مرجع چشم
target_eog_channel = None
# لیست اولویت برای پیدا کردن کانال چشم
for ch in ['Fp1', 'Fp2', 'Fz', 'Fp1-LE', 'Fp2-LE']:
    if ch in epochs_clean.ch_names:
        target_eog_channel = ch
        break

if target_eog_channel:
    print(f"Using channel '{target_eog_channel}' as EOG reference for auto-detection.")

    # تابع find_bads_eog به صورت خودکار مولفه‌های شبیه پلک را پیدا می‌کند
    # threshold=3.0 معمولا استاندارد است (هر چه کمتر باشد، سخت‌گیرتر است)
    eog_inds, scores = ica.find_bads_eog(epochs_clean, ch_name=target_eog_channel, threshold=3.0)

    print(f"Auto-detected EOG components (Blinks): {eog_inds}")

    # اعمال لیست حذفی
    ica.exclude = eog_inds

    # رسم نمودار امتیازها (اختیاری - برای دیدن دقت الگوریتم)
    ica.plot_scores(scores, exclude=eog_inds, title=f"Component correlation with {target_eog_channel}")
    plt.show()
else:
    print("Warning: No frontal channel (Fp1/Fp2) found! Cannot auto-detect blinks.")

# 3. نمایش مولفه‌ها (برای تایید چشمی شما)
# دور مولفه‌هایی که سیستم حذف کرده، خط قرمز کشیده می‌شود
print("Plotting components (Red title = Marked for removal)...")
ica.plot_components()
plt.show()

# 4. اعمال ICA و بازسازی سیگنال
print("Applying ICA to remove artifacts...")
epochs_final = epochs_clean.copy()
ica.apply(epochs_final)

# 5. مقایسه قبل و بعد (Visual Comparison)
if target_eog_channel:
    print(f"Plotting comparison on channel {target_eog_channel}...")

    # گرفتن داده اولین اپوک برای مقایسه
    original_data = epochs_clean.get_data(picks=target_eog_channel)[0, 0, :]
    cleaned_data = epochs_final.get_data(picks=target_eog_channel)[0, 0, :]

    plt.figure(figsize=(10, 6))
    plt.plot(original_data, label='Original (with Artifacts)', color='red', alpha=0.5)
    plt.plot(cleaned_data, label='Cleaned (ICA Applied)', color='blue', linewidth=1.5)
    plt.title(f'Effect of ICA on Channel {target_eog_channel}')
    plt.xlabel('Time points')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid(True)
    plt.show()

print("Step 3 Complete. 'epochs_final' is your clean data.")

# ==========================================
# Ghasem Step 4: Final Inspection (Time & Frequency)
# ==========================================
print("\n" + "=" * 30)
print("STARTING STEP 4: Time & Frequency Inspection")
print("=" * 30)

import matplotlib.pyplot as plt
import numpy as np

# تنظیمات نمودار برای زیبایی
plt.rcParams.update({'font.size': 10})

# ---------------------------------------------------------
# بخش اول: مقایسه در حوزه زمان (Time-Domain)
# ---------------------------------------------------------
print("Generating Time-Domain Comparison Plot...")

# انتخاب یک کانال برای نمایش
# معمولاً کانال‌های جلوی سر (Frontal) مثل Fp1, Fp2, Fz بیشترین آرتیفکت پلک را دارند
# ما اولین کانال موجود در لیست را انتخاب می‌کنیم یا اگر Fp1 بود آن را برمی‌داریم
target_ch = [ch for ch in epochs_final.ch_names if 'Fp1' in ch]
picked_ch = target_ch[0] if target_ch else epochs_final.ch_names[0]

print(f"Inspecting Channel: {picked_ch}")

# دریافت داده‌های خام (Raw) - برای مقایسه، ۱۰ ثانیه اول را می‌گیریم
# نکته: چون داده خام پیوسته است و داده نهایی اپوک شده، ما سعی می‌کنیم چند اپوک نهایی را به هم بچسبانیم
# تا طولشان برای نمایش بصری یکی شود.

# گرفتن ۳ اپوک اول از داده‌های تمیز شده
clean_data_segment = epochs_final.get_data(picks=picked_ch, copy=True)[0:3, 0, :].flatten()

# گرفتن معادل زمانی آن از داده خام (برای نمایش)
# طول زمانی که می‌خواهیم نمایش دهیم (تعداد نقاط)
n_samples_to_plot = len(clean_data_segment)
raw_data_segment, times = raw.get_data(picks=picked_ch, start=0, stop=n_samples_to_plot, return_times=True)
raw_data_segment = raw_data_segment[0] # حذف بعد کانال

# رسم نمودار زمانی
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=False)

# نمودار داده خام
ax1.plot(times, raw_data_segment, color='red', alpha=0.7, label='Raw Data (Drift + Artifacts)')
ax1.set_title(f'Time Domain: RAW Data ({picked_ch})')
ax1.set_ylabel('Amplitude (Volts)')
ax1.legend(loc="upper right")
ax1.grid(True, linestyle='--', alpha=0.6)

# نمودار داده نهایی
# محور زمان جدید برای داده اپوک شده
times_clean = np.linspace(0, len(clean_data_segment)/raw.info['sfreq'], len(clean_data_segment))
ax2.plot(times_clean, clean_data_segment, color='blue', label='Final Clean Data (Flat Baseline + No Blinks)')
ax2.set_title(f'Time Domain: FINAL Data ({picked_ch}) - After Filter, AutoReject & ICA')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Amplitude (Volts)')
ax2.legend(loc="upper right")
ax2.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()

print("Check point 1: Look at the graphs above.")
print("  - Is the Baseline flat in the blue graph? (Should be yes)")
print("  - Are large blinks (huge spikes) removed in the blue graph? (Should be yes)")


# ---------------------------------------------------------
# بخش دوم: مقایسه در حوزه فرکانس (PSD Comparison)
# ---------------------------------------------------------
print("\nGenerating PSD Comparison Plot...")

# محاسبه PSD برای داده خام
# fmax را تا ۶۰ می‌گذاریم تا هم ۵۰ هرتز (برق) را ببینیم هم آلفا (۱۰ هرتز)
spectrum_raw = raw.compute_psd(fmax=60, picks='eeg')
psds_raw, freqs_raw = spectrum_raw.get_data(return_freqs=True)
# میانگین گیری روی تمام کانال‌ها برای دیدن طیف کلی
psd_raw_mean = 10 * np.log10(psds_raw.mean(axis=0))

# محاسبه PSD برای داده نهایی (Clean)
spectrum_clean = epochs_final.compute_psd(fmax=60, picks='eeg')
psds_clean, freqs_clean = spectrum_clean.get_data(return_freqs=True)
# میانگین گیری روی تمام کانال‌ها و تمام اپوک‌ها
psd_clean_mean = 10 * np.log10(psds_clean.mean(axis=0).mean(axis=0))


# رسم نمودار مقایسه‌ای PSD
plt.figure(figsize=(10, 6))

plt.plot(freqs_raw, psd_raw_mean, color='red', linestyle='--', label='Raw Data', linewidth=1.5)
plt.plot(freqs_clean, psd_clean_mean, color='blue', label='Final Clean Data', linewidth=2)

# اضافه کردن خطوط راهنما برای بررسی چشمی
plt.axvline(x=50, color='gray', linestyle=':', label='50Hz (Line Noise)')
plt.axvline(x=10, color='green', linestyle=':', label='10Hz (Alpha Peak)')

plt.title('Frequency Domain Comparison (PSD)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power Spectral Density (dB)')
plt.legend()
plt.grid(True)
plt.xlim(0, 60)

plt.show()

print("Check point 2: Look at the PSD graph.")
print("  - 50 Hz Check: Is the peak at 50Hz gone in the Blue line?")
print("  - Alpha Check: Do you see a bump around 10Hz (Brain signal)?")
print("  - Shape Check: Does the curve generally go down (1/f shape)?")

print("\nStep 4 Complete.")

# ==========================================
# Ghasem Step 5: Per-Channel PSD Analysis
# ==========================================
print("\n" + "=" * 30)
print("STARTING STEP 5: Per-Channel PSD (Logarithmic)")
print("=" * 30)

import math

# 1. تنظیم پارامترهای طیفی (طبق دستور: 0.5 تا 55 هرتز)
fmin, fmax = 0.5, 60.0  # تا 60 می‌گیریم که حذف شدن 50 هرتز را ببینیم

print("Calculating PSDs for comparison...")

# محاسبه PSD برای داده خام (Raw)
# برای اینکه مقایسه عادلانه باشد، از داده Raw فقط بخش‌های EEG را می‌گیریم
psd_raw_inst = raw.compute_psd(method='welch', fmin=fmin, fmax=fmax, picks='eeg', n_fft=int(sfreq * 2))
psds_raw, freqs = psd_raw_inst.get_data(return_freqs=True)
# تبدیل به میانگین در طول زمان (چون Raw پیوسته است ولی خروجی PSD آرایه است)
# psds_raw shape: (n_channels, n_freqs) - اینجا نیازی به تغییر خاصی نیست چون compute_psd روی Raw خودش میانگین می‌گیرد.

# محاسبه PSD برای داده نهایی (Epochs Final)
psd_clean_inst = epochs_final.compute_psd(method='welch', fmin=fmin, fmax=fmax, picks='eeg', n_fft=int(sfreq * 2))
psds_clean, _ = psd_clean_inst.get_data(return_freqs=True)
# psds_clean shape: (n_epochs, n_channels, n_freqs)
# باید روی اپوک‌ها میانگین بگیریم تا به ابعاد (n_channels, n_freqs) برسیم
psds_clean_mean = psds_clean.mean(axis=0)

# 2. تنظیمات نمودار (Grid Layout)
n_channels = len(epochs_final.ch_names)
n_cols = 4  # تعداد ستون‌ها
n_rows = math.ceil(n_channels / n_cols)  # محاسبه تعداد ردیف‌ها

fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 3 * n_rows), constrained_layout=True)
axes = axes.flatten()  # تبدیل ماتریس محورها به یک لیست ساده

# 3. رسم نمودار برای هر کانال
for idx, ch_name in enumerate(epochs_final.ch_names):
    ax = axes[idx]

    # دریافت داده‌های مربوط به آن کانال خاص
    # نکته: ترتیب کانال‌ها در Raw و Epochs ممکن است متفاوت باشد، با اسم پیدا می‌کنیم
    raw_ch_idx = raw.ch_names.index(ch_name)
    clean_ch_idx = epochs_final.ch_names.index(ch_name)

    # رسم داده خام (قرمز)
    ax.plot(freqs, psds_raw[raw_ch_idx], color='red', alpha=0.6, linewidth=1, label='Before (Raw)')

    # رسم داده تمیز (آبی)
    ax.plot(freqs, psds_clean_mean[clean_ch_idx], color='blue', alpha=0.8, linewidth=1.5, label='After (Clean)')

    # تنظیمات ظاهری (طبق دستور: محور عمودی لگاریتمی)
    ax.set_yscale('log')  # محور عمودی لگاریتمی
    ax.set_title(ch_name, fontsize=10, fontweight='bold')
    ax.grid(True, which="both", ls="-", alpha=0.3)

    # فقط برای نمودارهای ستون اول و ردیف آخر لیبل می‌گذاریم تا شلوغ نشود
    if idx >= (n_rows - 1) * n_cols:
        ax.set_xlabel('Frequency (Hz)')
    if idx % n_cols == 0:
        ax.set_ylabel(r'PSD (${\mu V^2}/{Hz}$)')

    # خط چین برای 50 هرتز (چک کردن ناچ فیلتر)
    ax.axvline(x=50, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)

# خاموش کردن محورهای اضافی (اگر تعداد کانال‌ها مضرب 4 نبود)
for i in range(n_channels, len(axes)):
    axes[i].axis('off')

# اضافه کردن لجند کلی در بالای نمودار
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', ncol=2, fontsize=12)
fig.suptitle('Per-Channel PSD: Before vs After Preprocessing', fontsize=16, y=1.02)

plt.show()

print("Step 5 Complete. Analysis:")
print("1. 50Hz Noise: Check if the sharp spike at 50Hz (in Red) is gone or reduced in Blue.")
print("2. Low Freq Drift: Check if the Red line is very high near 0-1 Hz and Blue is controlled.")
print("3. Signal Preservation: Ensure Blue follows Red shape in Alpha/Beta (8-30 Hz) and isn't zero.")

# ==========================================
# Ghasem Step 6: Topomaps (Spatial Distribution)
# ==========================================
print("\n" + "=" * 30)
print("STARTING STEP 6: Plotting Topomaps (Theta, Alpha, Beta)")
print("=" * 30)

import matplotlib.pyplot as plt
import numpy as np
import mne

# 1. تعریف باندهای فرکانسی
freq_bands = {
    "Theta (4-8 Hz)": (4, 8),
    "Alpha (8-12 Hz)": (8, 12),
    "Beta (12-30 Hz)": (12, 30)
}

# 2. محاسبه طیف کلی (PSD)
print("Calculating Power Spectral Density (Welch)...")
# محاسبه PSD روی داده نهایی
spectrum = epochs_final.compute_psd(method='welch', fmin=1, fmax=40, n_fft=int(sfreq * 2))
psds, freqs = spectrum.get_data(return_freqs=True)
psds_mean = psds.mean(axis=0)

# 3. رسم نمودار
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Spatial Distribution of Brain Rhythms (Power in dB)', fontsize=16)

for ax, (band_name, (fmin, fmax)) in zip(axes, freq_bands.items()):
    # الف) برش فرکانسی
    freq_indices = np.where((freqs >= fmin) & (freqs <= fmax))[0]

    # ب) میانگین‌گیری انرژی
    band_power = psds_mean[:, freq_indices].mean(axis=1)

    # ج) تبدیل به دسی‌بل
    band_power_db = 10 * np.log10(band_power)

    # د) رسم نقشه توپوگرافی (بدون پارامتر show_names)
    im, _ = mne.viz.plot_topomap(
        band_power_db,
        epochs_final.info,
        axes=ax,
        show=False,
        cmap='RdBu_r',
        names=epochs_final.ch_names,  # نام کانال‌ها را نگه می‌داریم
        # show_names=False, <--- این خط حذف شد تا ارور برطرف شود
        contours=6
    )

    ax.set_title(band_name)

# اضافه کردن نوار رنگ
cbar_ax = fig.add_axes([0.92, 0.15, 0.015, 0.7])
clb = fig.colorbar(im, cax=cbar_ax)
clb.set_label('Power Spectral Density (dB)')

print("Plotting complete. Check the new window.")
plt.show()

print("-" * 30)
print("INTERPRETATION GUIDE:")
print("1. Alpha Band: Look at the back of the head. Red means high relaxation.")
print("2. Theta Band: Red spots might indicate drowsiness.")
print("3. Beta Band: Usually lower power compared to Alpha.")
print("-" * 30)