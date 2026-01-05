<div dir="rtl">

# گزارش فاز اول پروژه: پیش‌پردازش سیگنال‌های مغزی (EEG)

**نام دانشجو:** [ماهان ورمزیار-محمدمهدی صفری]  
**درس:** سیگنال‌ها و سیستم‌ها  
**موضوع:** آشنایی با ساختار EEG، تحلیل طیفی (PSD) و طراحی فیلترهای FIR

---

## ۱. مقدمه و اهداف
هدف از این فاز پروژه، ایجاد یک پایپ‌لاین (Pipeline) پردازشی برای سیگنال‌های واقعی مغزی است. این مراحل شامل بارگذاری داده‌ها، اصلاح مشخصات کانال‌ها، تحلیل فرکانسی و طراحی فیلترهای دیجیتال جهت حذف نویز برق شهر و آرتیفکت‌های فرکانسی می‌باشد.

---

## ۲. مشخصات سیگنال و طراحی فیلتر

داده‌های ۱۰ آزمودنی با فرمت `.edf` بارگذاری و بررسی شدند. مشخصات کلی به شرح زیر است:

- **فرکانس نمونه‌برداری ($f_s$):** [عدد fs] هرتز
- **فرکانس نایکوئیست:** [عدد nyquist] هرتز
- **تعداد کانال‌ها:** [تعداد] کانال (پس از حذف کانال‌های اضافی)

### طراحی فیلتر (Filter Design)
یک فیلتر میان‌گذر (Band-pass) با مشخصات زیر طراحی شد:
- **فرکانس قطع پایین:** 0.5 هرتز (حذف دریفت DC)
- **فرکانس قطع بالا:** 45 هرتز (حذف نویزهای فرکانس بالا)
- **فیلتر Notch:** فرکانس 50 هرتز (حذف برق شهر)

**نمودار پاسخ فرکانسی (Bode Plot):**
![Bode Plot](./Report_Images/Bode_Plot.png)
*(لطفاً تصویر نمودار Bode که جداگانه ذخیره کردید را در پوشه تصاویر قرار دهید و نامش را اینجا اصلاح کنید)*

---

## ۳. نتایج پردازش (برای ۱۰ آزمودنی)

در جدول زیر، چگالی طیفی توان (PSD) برای هر ۱۰ آزمودنی **قبل از فیلتر** (سمت راست) و **بعد از فیلتر** (سمت چپ) مقایسه شده است.
همانطور که مشاهده می‌شود، پیک ۵۰ هرتز در تمام موارد حذف شده و سیگنال در بازه ۰.۵ تا ۴۵ هرتز محدود شده است.

| نام آزمودنی | PSD خام (نویزدار) | PSD فیلتر شده (تمیز) |
| :---: | :---: | :---: |
| **Subject 01** | ![Raw](./Report_Images/Subject_01_PSD_Raw.png) | ![Filtered](./Report_Images/Subject_01_PSD_Filtered.png) |
| **Subject 02** | ![Raw](./Report_Images/Subject_02_PSD_Raw.png) | ![Filtered](./Report_Images/Subject_02_PSD_Filtered.png) |
| **Subject 03** | ![Raw](./Report_Images/Subject_03_PSD_Raw.png) | ![Filtered](./Report_Images/Subject_03_PSD_Filtered.png) |
| **Subject 04** | ![Raw](./Report_Images/Subject_04_PSD_Raw.png) | ![Filtered](./Report_Images/Subject_04_PSD_Filtered.png) |
| **Subject 05** | ![Raw](./Report_Images/Subject_05_PSD_Raw.png) | ![Filtered](./Report_Images/Subject_05_PSD_Filtered.png) |
| **Subject 06** | ![Raw](./Report_Images/Subject_06_PSD_Raw.png) | ![Filtered](./Report_Images/Subject_06_PSD_Filtered.png) |
| **Subject 07** | ![Raw](./Report_Images/Subject_07_PSD_Raw.png) | ![Filtered](./Report_Images/Subject_07_PSD_Filtered.png) |
| **Subject 08** | ![Raw](./Report_Images/Subject_08_PSD_Raw.png) | ![Filtered](./Report_Images/Subject_08_PSD_Filtered.png) |
| **Subject 09** | ![Raw](./Report_Images/Subject_09_PSD_Raw.png) | ![Filtered](./Report_Images/Subject_09_PSD_Filtered.png) |
| **Subject 10** | ![Raw](./Report_Images/Subject_10_PSD_Raw.png) | ![Filtered](./Report_Images/Subject_10_PSD_Filtered.png) |

---

## ۴. پاسخ به سوال تئوری: پدیده الایزینگ (Aliasing)

**سوال:** اگر سیگنال مغز دارای مولفه‌های فرکانسی بالاتر از حد نایکوئیست می‌بود و ما با این نرخ نمونه‌برداری می‌کردیم، چه پدیده‌ای رخ می‌داد؟

**پاسخ:**
در این صورت پدیده **دگرنامی یا الایزینگ (Aliasing)** رخ می‌داد.
طبق قضیه نمونه‌برداری نایکوئیست-شانون، فرکانس نمونه‌برداری ($f_s$) باید حداقل دو برابر بیشترین فرکانس موجود در سیگنال ($f_{max}$) باشد ($f_s \ge 2f_{max}$).
اگر سیگنال حاوی فرکانس‌هایی بالاتر از حد نایکوئیست ($f_s/2$) باشد، هنگام نمونه‌برداری، این فرکانس‌های بالا به اشتباه به عنوان فرکانس‌های پایین‌تر تفسیر می‌شوند و روی طیف اصلی سیگنال «تا» می‌خورند (Fold back). این تداخل باعث از دست رفتن اطلاعات و اعوجاج سیگنال می‌شود که پس از نمونه‌برداری قابل بازگشت نیست.

---

## ۵. پیاده‌سازی کد (Python & MNE)

بخشی از کد پیاده‌سازی شده برای پردازش دسته‌ای داده‌ها:
</div>

```python
import mne
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# 1. بارگذاری داده‌ها
# توجه: فایل شما edf است، پس از read_raw_edf استفاده می‌کنیم
raw = mne.io.read_raw_edf("C:/Users/Victus 16/PycharmProjects/signal&system/subjects/Subject_01.edf", preload=True)

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
```

---
<div dir="rtl">
## ۶. گزارش فاز دوم: قطعه‌بندی، حذف آرتیفکت و ترمیم سیگنال

در این فاز، پس از پیش‌پردازش اولیه (فیلترینگ)، هدف آماده‌سازی داده‌ها برای تحلیل‌های دقیق‌تر است. این مراحل شامل اصلاح موقعیت مکانی سنسورها، خرد کردن سیگنال به قطعات کوچک (Epoching)، شناسایی هوشمند نویز با الگوریتم AutoReject و ترمیم کانال‌های خراب است.

### ۶-۱. روش کار و الگوریتم‌ها
۱. **اصلاح مونتاژ:** استاندارد مکانی **10-20** روی داده‌ها اعمال شد.
۲. **قطعه‌بندی (Epoching):** سیگنال پیوسته به قطعات مساوی **۲ ثانیه‌ای** تقسیم شد. این کار باعث تولید حدود ۱۸۳ اپوک برای هر آزمودنی گردید.
۳. **الگوریتم AutoReject:** از این کتابخانه برای تمیزکاری خودکار استفاده شد. این الگوریتم با بررسی آماری، اپوک‌ها را به سه دسته تقسیم می‌کند:
    * **خوب (Good):** داده سالم (رنگ سبز در نمودار).
    * **بد (Bad):** داده غیرقابل استفاده که حذف می‌شود (رنگ قرمز).
    * **ترمیم‌ شده (Interpolated):** داده‌ای که با استفاده از کانال‌های همسایه اصلاح شده است (رنگ آبی).

### ۶-۲. نتایج پردازش ۱۰ آزمودنی
در جدول زیر، خروجی ماتریس وضعیت (Heatmap) و وضعیت نهایی سنسورها پس از ترمیم (Topomap) برای تمام ۱۰ آزمودنی آورده شده است.

| نام فایل | ماتریس وضعیت (Heatmap) | وضعیت سنسورها (Topomap) |
| :---: | :---: | :---: |
| **Subject 01** | ![Heat](./Report_Images_Step2/Subject_01_Heatmap.png) | ![Sens](./Report_Images_Step2/Subject_01_Sensors.png) |
| **Subject 02** | ![Heat](./Report_Images_Step2/Subject_02_Heatmap.png) | ![Sens](./Report_Images_Step2/Subject_02_Sensors.png) |
| **Subject 03** | ![Heat](./Report_Images_Step2/Subject_03_Heatmap.png) | ![Sens](./Report_Images_Step2/Subject_03_Sensors.png) |
| **Subject 04** | ![Heat](./Report_Images_Step2/Subject_04_Heatmap.png) | ![Sens](./Report_Images_Step2/Subject_04_Sensors.png) |
| **Subject 05** | ![Heat](./Report_Images_Step2/Subject_05_Heatmap.png) | ![Sens](./Report_Images_Step2/Subject_05_Sensors.png) |
| **Subject 06** | ![Heat](./Report_Images_Step2/Subject_06_Heatmap.png) | ![Sens](./Report_Images_Step2/Subject_06_Sensors.png) |
| **Subject 07** | ![Heat](./Report_Images_Step2/Subject_07_Heatmap.png) | ![Sens](./Report_Images_Step2/Subject_07_Sensors.png) |
| **Subject 08** | ![Heat](./Report_Images_Step2/Subject_08_Heatmap.png) | ![Sens](./Report_Images_Step2/Subject_08_Sensors.png) |
| **Subject 09** | ![Heat](./Report_Images_Step2/Subject_09_Heatmap.png) | ![Sens](./Report_Images_Step2/Subject_09_Sensors.png) |
| **Subject 10** | ![Heat](./Report_Images_Step2/Subject_10_Heatmap.png) | ![Sens](./Report_Images_Step2/Subject_10_Sensors.png) |

---

## ۷. پاسخ به سوالات تئوری فاز دوم

### سوال ۱: چرا سیگنال مغزی را به قطعات کوچک (مثلاً ۲ ثانیه) تقسیم می‌کنیم؟
**پاسخ:**
۱. **ایستایی (Stationarity):** سیگنال مغزی ماهیت غیر-ایستا دارد (خواص آماری آن در طول زمان تغییر می‌کند). اما در بازه‌های کوتاه (مثل ۲ ثانیه) می‌توان آن را «شبه-ایستا» فرض کرد که پیش‌نیاز بسیاری از تحلیل‌های فرکانسی است.
۲. **مدیریت آرتیفکت:** اگر کل سیگنال یکپارچه باشد، یک حرکت ناگهانی بیمار می‌تواند میانگین کل داده را خراب کند. با قطعه‌بندی، می‌توانیم فقط آن قطعه‌ی ۲ ثانیه‌ای خراب را دور بریزیم و مابقی داده را حفظ کنیم.

### سوال ۲: تفاوت سطر و ستون قرمز در ماتریس Heatmap چیست؟
**پاسخ:**
* **ستون قرمز (یا بخش عمده‌ای از یک ستون):** نشان‌دهنده **خرابی سنسور (Bad Channel)** است. یعنی یک الکترود خاص (مثلاً Fz) قطع شده یا تماس خوبی با پوست ندارد و در تمام طول آزمایش نویز ضبط کرده است.
* **سطر قرمز:** نشان‌دهنده **آرتیفکت لحظه‌ای (Time Artifact)** است. یعنی در آن لحظه خاص (آن اپوک)، بیمار حرکتی مثل پلک زدن شدید یا فشردن دندان‌ها انجام داده که باعث شده تمام کانال‌ها به صورت همزمان نویز بگیرند.

### سوال ۳: فرآیند درون‌یابی (Interpolation) چگونه کار می‌کند؟
**پاسخ:**
درون‌یابی روشی ریاضی برای بازسازی داده‌های از دست رفته است. وقتی یک کانال به عنوان "خراب" شناسایی می‌شود (مثلاً بیش از ۷۰٪ مواقع نویز دارد)، داده‌های آن حذف می‌شود.
سپس الگوریتم (معمولاً روش *Spherical Spline*) به کانال‌های سالم اطراف نگاه می‌کند. هرچه یک کانال سالم به کانال خراب نزدیک‌تر باشد، وزن (تأثیر) بیشتری دارد. مقدار جدید کانال خراب، حاصل **میانگین وزنی** کانال‌های همسایه است.
* **چرا کانال‌های ۱۰٪ خراب را ترمیم می‌کنیم اما ۷۰٪ را دور می‌ریزیم؟**
اگر کانالی ۷۰٪ مواقع خراب باشد، یعنی داده‌ی واقعی مغزی در آن بسیار ناچیز است، پس بهتر است کلاً با تخمین جایگزین شود. اما اگر کانالی فقط ۱۰٪ خرابی دارد، یعنی ۹۰٪ اطلاعاتش ارزشمند است؛ پس حیف است حذف شود و فقط تکه‌های کوچک خراب را اصلاح می‌کنیم.

---

## ۸. پیوست: کد پایتون استفاده شده (Batch Processing)

کد زیر برای پردازش خودکار ۱۰ فایل، تولید Heatmap و تشخیص کانال‌های معیوب استفاده شده است:
</div>

```python
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
```

<div dir="rtl">

---

## ۹. گزارش گام سوم: حذف آرتیفکت با تحلیل مؤلفه‌های مستقل (ICA)

در این گام، از روش پیشرفته **ICA** برای جدا کردن سیگنال‌های مغزی از نویزهای بیولوژیکی استفاده شده است. با توجه به تعدد فایل‌ها و نیاز به دقت بالا، به جای بررسی دستی، از **روش تشخیص اتوماتیک بر اساس همبستگی (Automated Correlation-based Detection)** استفاده شده است.

### ۹-۱. روش اجرای اتوماتیک
۱. **آموزش مدل (Fit):** الگوریتم FastICA روی اپوک‌های تمیز شده آموزش داده شد و ۱۵ مؤلفه مستقل استخراج گردید.
۲. **الگوریتم تشخیص هوشمند:** از آنجا که کانال اختصاصی EOG ثبت نشده بود، کانال‌های پیشانی (**Fp1 یا Fp2**) به عنوان مرجع فعالیت چشم در نظر گرفته شدند.
۳. **معیار حذف:** با استفاده از تابع `find_bads_eog` در کتابخانه MNE، همبستگی (Correlation) میان تمام مؤلفه‌های ICA و کانال پیشانی محاسبه شد. مؤلفه‌هایی که امتیاز **Z-Score آن‌ها بالاتر از ۳.۰** بود (یعنی شباهت بسیار زیادی به الگوی پلک زدن داشتند)، به صورت خودکار به عنوان نویز شناسایی و حذف شدند.

### ۹-۲. نتایج جداسازی منابع
در جدول زیر، نقشه‌های توپوگرافی استخراج شده و لیست مؤلفه‌هایی که الگوریتم به صورت خودکار حذف کرده است، نمایش داده شده‌اند.

| نام آزمودنی | نقشه‌های ICA (Topomap) | مؤلفه‌های حذف شده (Auto-Detected) |
| :---: | :---: | :---: |
| **Subject 01** | ![ICA](./Report_Images_Step3_Auto/Subject_01_ICA_Topomaps.png) | *(اعداد خروجی کد را اینجا بنویسید)* |
| **Subject 02** | ![ICA](./Report_Images_Step3_Auto/Subject_02_ICA_Topomaps.png) | ... |
| **Subject 03** | ![ICA](./Report_Images_Step3_Auto/Subject_03_ICA_Topomaps.png) | ... |
| **Subject 04** | ![ICA](./Report_Images_Step3_Auto/Subject_04_ICA_Topomaps.png) | ... |
| **Subject 05** | ![ICA](./Report_Images_Step3_Auto/Subject_05_ICA_Topomaps.png) | ... |
| **Subject 06** | ![ICA](./Report_Images_Step3_Auto/Subject_06_ICA_Topomaps.png) | ... |
| **Subject 07** | ![ICA](./Report_Images_Step3_Auto/Subject_07_ICA_Topomaps.png) | ... |
| **Subject 08** | ![ICA](./Report_Images_Step3_Auto/Subject_08_ICA_Topomaps.png) | ... |
| **Subject 09** | ![ICA](./Report_Images_Step3_Auto/Subject_09_ICA_Topomaps.png) | ... |
| **Subject 10** | ![ICA](./Report_Images_Step3_Auto/Subject_10_ICA_Topomaps.png) | ... |

*(نکته: تصاویر مربوط به امتیازدهی الگوریتم (Scores) و مقایسه سیگنال قبل و بعد از حذف نویز نیز در پوشه خروجی ذخیره شده‌اند).*

---

## ۱۰. پاسخ به سوالات تئوری گام سوم

### سوال ۱: چرا برای حذف پلک چشم از فیلتر پایین‌گذر یا بالاگذر استفاده نکردیم؟
**پاسخ:**
زیرا طیف فرکانسی سیگنال ناشی از پلک زدن (که معمولاً فرکانس پایینی در حدود < ۴ هرتز دارد) با طیف فرکانسی امواج اصلی و حیاتی مغز (مانند امواج **دلتا** و **تتا**) **هم‌پوشانی (Overlap)** دارد.
اگر بخواهیم با یک فیلتر بالاگذر (مثلاً با فرکانس قطع ۳ هرتز) اثر پلک را حذف کنیم، تمام اطلاعات ارزشمند امواج دلتا (۱ تا ۴ هرتز) را نیز از دست خواهیم داد و داده‌های مغزی تحریف می‌شوند. اما ICA چون بر مبنای شکل موج و استقلال آماری کار می‌کند، می‌تواند بدون دستکاری فرکانس‌های مغزی، فقط نویز پلک را جدا کند.

### سوال ۲: در نقشه توپوگرافی، مؤلفه مربوط به پلک زدن معمولاً چه شکلی است؟ چرا انرژی آن در جلوی سر متمرکز است؟
**پاسخ:**
در نقشه‌های ICA، مؤلفه پلک زدن معمولاً به صورت دو لکه بزرگ **قرمز یا آبی پررنگ** دیده می‌شود که کاملاً در قسمت **جلویی سر (Frontal)** قرار دارند (مشابه تصویر دو چشم در بالای دایره).
**دلیل تمرکز انرژی در جلو:** چشم‌ها دقیقاً در زیر لوب پیشانی مغز و نزدیک‌ترین فاصله به الکترودهای **Fp1 و Fp2** قرار دارند. کره چشم انسان مانند یک دو‌قطبی الکتریکی (Dipole) عمل می‌کند (قرنیه مثبت و شبکیه منفی است). حرکت پلک روی کره چشم باعث تغییرات پتانسیل شدیدی می‌شود که به دلیل نزدیکی فیزیکی، بیشترین دامنه را روی الکترودهای جلوی پیشانی ایجاد می‌کند و با دور شدن از جلوی سر، شدت آن به سرعت کاهش می‌یابد.

---

## ۱۱. پیوست کد: اجرای خودکار ICA

کد پایتون استفاده شده برای پردازش دسته‌ای و حذف هوشمند آرتیفکت‌ها:
</div>

```python
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
```

<div dir="rtl">

## ۱۲. گزارش گام چهارم: ارزیابی نهایی و کنترل کیفیت (Final Inspection)

پس از اعمال تمامی مراحل پردازشی (فیلترهای فرکانسی، قطعه‌بندی، حذف اپوک‌های بد و ICA)، لازم است خروجی نهایی را با داده خام اولیه مقایسه کنیم تا از صحت عملکرد پایپ‌لاین (Pipeline) اطمینان حاصل شود. این مقایسه در دو حوزه زمان و فرکانس انجام شده است.

### ۱۲-۱. تحلیل نتایج (Interpretation)
برای هر ۱۰ آزمودنی، نمودار مقایسه‌ای تولید شد. تحلیل نتایج نشان‌دهنده موفقیت پردازش است:

1.  **در حوزه زمان (Time Domain):**
    * **داده خام (قرمز):** دارای نوسانات شدید خط پایه (Drift) و پرش‌های ناگهانی است.
    * **داده نهایی (آبی):** سیگنال کاملاً حول محور صفر (Zero-centered) نوسان می‌کند که نشان‌دهنده حذف دریفت DC است. همچنین پرش‌های بزرگ ناشی از پلک حذف شده‌اند.
2.  **در حوزه فرکانس (PSD):**
    * **نویز ۵۰ هرتز:** در نمودار قرمز یک قله تیز در ۵۰ هرتز وجود دارد، اما در نمودار آبی (به دلیل اعمال Notch Filter) این قله کاملاً حذف شده و یک فرورفتگی V شکل ایجاد شده است.
    * **حفظ امواج مغزی:** قله مربوط به **موج آلفا (~۱۰ هرتز)** که در داده خام وجود داشت، در داده تمیز نیز حفظ شده است. این مهم‌ترین نشانه است که ثابت می‌کند پردازش ما فقط نویز را حذف کرده و اطلاعات مغزی را از بین نبرده است.
    * **شیب نمودار:** نمودار نهایی شکل استاندارد $1/f$ را دارد و نویزهای فرکانس بالا (>45Hz) در آن تضعیف شده‌اند.

### ۱۲-۲. جدول نتایج نهایی (۱۰ آزمودنی)

| نام آزمودنی | نمودار جامع (زمان + فرکانس) |
| :---: | :---: |
| **Subject 01** | ![Final](./Report_Images_Step4_Final/Report_Step4_Subject_01.png) |
| **Subject 02** | ![Final](./Report_Images_Step4_Final/Report_Step4_Subject_02.png) |
| **Subject 03** | ![Final](./Report_Images_Step4_Final/Report_Step4_Subject_03.png) |
| **Subject 04** | ![Final](./Report_Images_Step4_Final/Report_Step4_Subject_04.png) |
| **Subject 05** | ![Final](./Report_Images_Step4_Final/Report_Step4_Subject_05.png) |
| **Subject 06** | ![Final](./Report_Images_Step4_Final/Report_Step4_Subject_06.png) |
| **Subject 07** | ![Final](./Report_Images_Step4_Final/Report_Step4_Subject_07.png) |
| **Subject 08** | ![Final](./Report_Images_Step4_Final/Report_Step4_Subject_08.png) |
| **Subject 09** | ![Final](./Report_Images_Step4_Final/Report_Step4_Subject_09.png) |
| **Subject 10** | ![Final](./Report_Images_Step4_Final/Report_Step4_Subject_10.png) |

---

## ۱۳. پیوست کد: تولید گزارش نهایی و نمودارها

کد زیر برای تولید خودکار نمودارهای مقایسه‌ای و ذخیره آن‌ها استفاده شده است. در این کد، از تشخیص خودکار پلک (بر اساس کانال Fp1) برای حذف مولفه‌های ICA در حالت پردازش گروهی استفاده شده است.
</div>

```python
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
```
