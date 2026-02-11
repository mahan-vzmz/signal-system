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
![Bode Plot](./Steps/Report_Images/Bode_Plot.png)

---

## ۳. نتایج پردازش (برای ۱۰ آزمودنی)

در جدول زیر، چگالی طیفی توان (PSD) برای هر ۱۰ آزمودنی **قبل از فیلتر** (سمت راست) و **بعد از فیلتر** (سمت چپ) مقایسه شده است.
همانطور که مشاهده می‌شود، پیک ۵۰ هرتز در تمام موارد حذف شده و سیگنال در بازه ۰.۵ تا ۴۵ هرتز محدود شده است.

| نام آزمودنی | PSD خام (نویزدار) | PSD فیلتر شده (تمیز) |
| :---: | :---: | :---: |
| **Subject 01** | ![Raw](./Steps/Report_Images/Subject_01_PSD_Raw.png) | ![Filtered](./Steps/Report_Images/Subject_01_PSD_Filtered.png) |
| **Subject 02** | ![Raw](./Steps/Report_Images/Subject_02_PSD_Raw.png) | ![Filtered](./Steps/Report_Images/Subject_02_PSD_Filtered.png) |
| **Subject 03** | ![Raw](./Steps/Report_Images/Subject_03_PSD_Raw.png) | ![Filtered](./Steps/Report_Images/Subject_03_PSD_Filtered.png) |
| **Subject 04** | ![Raw](./Steps/Report_Images/Subject_04_PSD_Raw.png) | ![Filtered](./Steps/Report_Images/Subject_04_PSD_Filtered.png) |
| **Subject 05** | ![Raw](./Steps/Report_Images/Subject_05_PSD_Raw.png) | ![Filtered](./Steps/Report_Images/Subject_05_PSD_Filtered.png) |
| **Subject 06** | ![Raw](./Steps/Report_Images/Subject_06_PSD_Raw.png) | ![Filtered](./Steps/Report_Images/Subject_06_PSD_Filtered.png) |
| **Subject 07** | ![Raw](./Steps/Report_Images/Subject_07_PSD_Raw.png) | ![Filtered](./Steps/Report_Images/Subject_07_PSD_Filtered.png) |
| **Subject 08** | ![Raw](./Steps/Report_Images/Subject_08_PSD_Raw.png) | ![Filtered](./Steps/Report_Images/Subject_08_PSD_Filtered.png) |
| **Subject 09** | ![Raw](./Steps/Report_Images/Subject_09_PSD_Raw.png) | ![Filtered](./Steps/Report_Images/Subject_09_PSD_Filtered.png) |
| **Subject 10** | ![Raw](./Steps/Report_Images/Subject_10_PSD_Raw.png) | ![Filtered](./Steps/Report_Images/Subject_10_PSD_Filtered.png) |

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

<div dir="rtl">
---
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
| **Subject 01** | ![Heat](./Steps/Report_Images_Step2/Subject_01_Heatmap.png) | ![Sens](./Steps/Report_Images_Step2/Subject_01_Sensors.png) |
| **Subject 02** | ![Heat](./Steps/Report_Images_Step2/Subject_02_Heatmap.png) | ![Sens](./Steps/Report_Images_Step2/Subject_02_Sensors.png) |
| **Subject 03** | ![Heat](./Steps/Report_Images_Step2/Subject_03_Heatmap.png) | ![Sens](./Steps/Report_Images_Step2/Subject_03_Sensors.png) |
| **Subject 04** | ![Heat](./Steps/Report_Images_Step2/Subject_04_Heatmap.png) | ![Sens](./Steps/Report_Images_Step2/Subject_04_Sensors.png) |
| **Subject 05** | ![Heat](./Steps/Report_Images_Step2/Subject_05_Heatmap.png) | ![Sens](./Steps/Report_Images_Step2/Subject_05_Sensors.png) |
| **Subject 06** | ![Heat](./Steps/Report_Images_Step2/Subject_06_Heatmap.png) | ![Sens](./Steps/Report_Images_Step2/Subject_06_Sensors.png) |
| **Subject 07** | ![Heat](./Steps/Report_Images_Step2/Subject_07_Heatmap.png) | ![Sens](./Steps/Report_Images_Step2/Subject_07_Sensors.png) |
| **Subject 08** | ![Heat](./Steps/Report_Images_Step2/Subject_08_Heatmap.png) | ![Sens](./Steps/Report_Images_Step2/Subject_08_Sensors.png) |
| **Subject 09** | ![Heat](./Steps/Report_Images_Step2/Subject_09_Heatmap.png) | ![Sens](./Steps/Report_Images_Step2/Subject_09_Sensors.png) |
| **Subject 10** | ![Heat](./Steps/Report_Images_Step2/Subject_10_Heatmap.png) | ![Sens](./Steps/Report_Images_Step2/Subject_10_Sensors.png) |

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
import mne
import numpy as np
import matplotlib.pyplot as plt
from autoreject import AutoReject
import glob
import os

# تنظیم مسیرها
input_folder = "subjects/"
output_folder = "Report_Images_Step2"
os.makedirs(output_folder, exist_ok=True)
all_files = glob.glob(os.path.join(input_folder, "Subject_*.edf"))
all_files.sort()

print(f"Processing {len(all_files)} files...")

for file_path in all_files:
    subject_name = os.path.splitext(os.path.basename(file_path))[0]
    
    try:
        # 1. بارگذاری و پیش‌پردازش
        raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)
        mapping = {name: name.replace('-LE', '') for name in raw.ch_names if '-LE' in name}
        raw.rename_channels(mapping)
        
        if 'Trig' in raw.ch_names: raw.set_channel_types({'Trig': 'stim'})
        try: raw.set_montage('standard_1020', match_case=False)
        except: pass
        
        raw.pick_types(eeg=True, eog=False, stim=False, exclude='bads')
        raw.notch_filter(50.0, verbose=False)
        raw.filter(0.5, 45.0, verbose=False)

        # 2. قطعه‌بندی (Epoching)
        epochs = mne.make_fixed_length_epochs(raw, duration=2.0, preload=True, verbose=False)

        # 3. شناسایی آرتیفکت (AutoReject)
        ar = AutoReject(n_interpolate=[1, 2, 4], consensus=[0.5, 0.7], random_state=42, verbose=False)
        epochs_clean, reject_log = ar.fit_transform(epochs, return_log=True)

        # 4. ذخیره خروجی‌ها
        # ذخیره Heatmap
        fig_heat = reject_log.plot(orientation='horizontal', show=False)
        plt.suptitle(f"Heatmap - {subject_name}")
        plt.savefig(os.path.join(output_folder, f"{subject_name}_Heatmap.png"))
        plt.close(fig_heat)

        # ذخیره سنسورها
        epochs_clean.interpolate_bads(reset_bads=True)
        fig_sensor = epochs_clean.plot_sensors(show_names=True, show=False)
        plt.savefig(os.path.join(output_folder, f"{subject_name}_Sensors.png"))
        plt.close(fig_sensor)
        
        print(f"Done: {subject_name}")

    except Exception as e:
        print(f"Error in {subject_name}: {e}")

print("All Processing Completed.")
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
| **Subject 01** | ![ICA](./Steps/Report_Images_Step3_Auto/Subject_01_ICA_Topomaps.png) | *(اعداد خروجی کد را اینجا بنویسید)* |
| **Subject 02** | ![ICA](./Steps/Report_Images_Step3_Auto/Subject_02_ICA_Topomaps.png) | ... |
| **Subject 03** | ![ICA](./Steps/Report_Images_Step3_Auto/Subject_03_ICA_Topomaps.png) | ... |
| **Subject 04** | ![ICA](./Steps/Report_Images_Step3_Auto/Subject_04_ICA_Topomaps.png) | ... |
| **Subject 05** | ![ICA](./Steps/Report_Images_Step3_Auto/Subject_05_ICA_Topomaps.png) | ... |
| **Subject 06** | ![ICA](./Steps/Report_Images_Step3_Auto/Subject_06_ICA_Topomaps.png) | ... |
| **Subject 07** | ![ICA](./Steps/Report_Images_Step3_Auto/Subject_07_ICA_Topomaps.png) | ... |
| **Subject 08** | ![ICA](./Steps/Report_Images_Step3_Auto/Subject_08_ICA_Topomaps.png) | ... |
| **Subject 09** | ![ICA](./Steps/Report_Images_Step3_Auto/Subject_09_ICA_Topomaps.png) | ... |
| **Subject 10** | ![ICA](./Steps/Report_Images_Step3_Auto/Subject_10_ICA_Topomaps.png) | ... |

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
# بخشی از کد پردازش اتوماتیک (Auto-ICA)
import mne
from mne.preprocessing import ICA

# ... (بعد از مرحله AutoReject) ...

# 1. آموزش ICA
ica = ICA(n_components=15, max_iter='auto', random_state=97)
ica.fit(epochs_clean)

# 2. تشخیص اتوماتیک پلک (بدون دخالت دست)
# استفاده از کانال Fp1 به عنوان جایگزین EOG
if 'Fp1' in epochs_clean.ch_names:
    eog_inds, scores = ica.find_bads_eog(epochs_clean, ch_name='Fp1', threshold=3.0)
    ica.exclude = eog_inds
    print(f"Auto-detected artifacts: {eog_inds}")

# 3. اعمال تغییرات و ذخیره نتایج
ica.apply(epochs_clean)
# ... ذخیره نمودارها ...
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
| **Subject 01** | ![Final](./Steps/Report_Images_Step4_Final/Report_Step4_Subject_01.png) |
| **Subject 02** | ![Final](./Steps/Report_Images_Step4_Final/Report_Step4_Subject_02.png) |
| **Subject 03** | ![Final](./Steps/Report_Images_Step4_Final/Report_Step4_Subject_03.png) |
| **Subject 04** | ![Final](./Steps/Report_Images_Step4_Final/Report_Step4_Subject_04.png) |
| **Subject 05** | ![Final](./Steps/Report_Images_Step4_Final/Report_Step4_Subject_05.png) |
| **Subject 06** | ![Final](./Steps/Report_Images_Step4_Final/Report_Step4_Subject_06.png) |
| **Subject 07** | ![Final](./Steps/Report_Images_Step4_Final/Report_Step4_Subject_07.png) |
| **Subject 08** | ![Final](./Steps/Report_Images_Step4_Final/Report_Step4_Subject_08.png) |
| **Subject 09** | ![Final](./Steps/Report_Images_Step4_Final/Report_Step4_Subject_09.png) |
| **Subject 10** | ![Final](./Steps/Report_Images_Step4_Final/Report_Step4_Subject_10.png) |

---

## ۱۳. پیوست کد: تولید گزارش نهایی و نمودارها

کد زیر برای تولید خودکار نمودارهای مقایسه‌ای و ذخیره آن‌ها استفاده شده است. در این کد، از تشخیص خودکار پلک (بر اساس کانال Fp1) برای حذف مولفه‌های ICA در حالت پردازش گروهی استفاده شده است.
</div>

```python
import mne
import numpy as np
import matplotlib.pyplot as plt
from autoreject import AutoReject
from mne.preprocessing import ICA
import glob
import os

# 1. تنظیم مسیرها و پوشه خروجی
# -----------------------------
input_folder = "C:/Users/Victus 16/PycharmProjects/SignalSystem/subjects/"
output_folder = "Report_Images_Step4_Final"  # پوشه نهایی گزارش‌ها
os.makedirs(output_folder, exist_ok=True)

print(f"Final Comparison Images will be saved in: {os.getcwd()}\\{output_folder}")

# پیدا کردن فایل‌ها
all_files = glob.glob(os.path.join(input_folder, "Subject_*.edf"))
all_files.sort()

# تنظیمات پردازش
low_cut = 0.5
high_cut = 45.0
notch_freq = 50.0
epoch_dur = 2.0
n_ica_components = 15

# ==========================================
# شروع پردازش روی تمام فایل‌ها
# ==========================================
for file_path in all_files:
    subject_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"\nProcessing: {subject_name}")

    try:
        # --- بخش ۱: آماده‌سازی داده خام (Raw) ---
        raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)
        mapping = {name: name.replace('-LE', '') for name in raw.ch_names if '-LE' in name}
        raw.rename_channels(mapping)
        if 'Trig' in raw.ch_names: raw.set_channel_types({'Trig': 'stim'}) 
        try: raw.set_montage(mne.channels.make_standard_montage('standard_1020'), match_case=False)
        except: pass
        raw.pick_types(eeg=True, eog=False, stim=False, exclude='bads')

        # ذخیره کپی خام برای رسم
        raw_for_plot = raw.copy()

        # --- بخش ۲: پردازش‌ها ---
        raw.notch_filter(notch_freq, verbose=False)
        raw.filter(low_cut, high_cut, verbose=False)
        epochs = mne.make_fixed_length_epochs(raw, duration=epoch_dur, preload=True, verbose=False)
        
        ar = AutoReject(n_interpolate=[1, 2], consensus=[0.6], random_state=42, verbose=False)
        epochs_clean = ar.fit_transform(epochs)

        # --- بخش ۳: ICA و حذف اتوماتیک پلک ---
        ica = ICA(n_components=n_ica_components, max_iter='auto', random_state=97)
        ica.fit(epochs_clean)

        # تشخیص اتوماتیک با استفاده از کانال Fp1
        eog_inds, _ = ica.find_bads_eog(epochs_clean, ch_name='Fp1', threshold=2.5)
        if eog_inds: ica.exclude = eog_inds
        
        epochs_final = epochs_clean.copy()
        ica.apply(epochs_final)

        # ==========================================
        # بخش ۴: تولید نمودارهای مقایسه‌ای
        # ==========================================
        fig = plt.figure(figsize=(12, 10))
        
        # الف) رسم حوزه زمان
        target_ch = [ch for ch in epochs_final.ch_names if 'Fp1' in ch]
        picked_ch = target_ch[0] if target_ch else epochs_final.ch_names[0]

        # داده خام (۶ ثانیه)
        raw_data, t_raw = raw_for_plot.get_data(picks=picked_ch, start=0, stop=int(6*raw.info['sfreq']), return_times=True)
        # داده نهایی (۳ اپوک)
        clean_data = epochs_final.get_data(picks=picked_ch, copy=True)[0:3, 0, :].flatten()
        t_clean = np.linspace(0, 6, len(clean_data))

        ax1 = fig.add_subplot(3, 1, 1)
        ax1.plot(t_raw, raw_data[0], 'r', alpha=0.7)
        ax1.set_title(f"Raw Data ({picked_ch})")
        
        ax2 = fig.add_subplot(3, 1, 2)
        ax2.plot(t_clean, clean_data, 'b')
        ax2.set_title("Final Clean Data")

        # ب) رسم PSD
        ax3 = fig.add_subplot(3, 1, 3)
        psds_raw, freqs = raw_for_plot.compute_psd(fmax=60).get_data(return_freqs=True)
        psds_clean, freqs_c = epochs_final.compute_psd(fmax=60).get_data(return_freqs=True)
        
        ax3.plot(freqs, 10*np.log10(psds_raw.mean(axis=0)), 'r--', label='Raw')
        ax3.plot(freqs_c, 10*np.log10(psds_clean.mean(axis=0).mean(axis=0)), 'b', label='Clean')
        ax3.legend()
        ax3.set_title("PSD Comparison")
        ax3.axvline(50, color='gray', linestyle=':') # خط ۵۰ هرتز

        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f"Report_Step4_{subject_name}.png"))
        plt.close(fig)

    except Exception as e:
        print(f"Error: {e}")

print("Done.")
```


<div dir="rtl">

---

## ۱۴. گزارش گام پنجم: تحلیل طیفی دقیق به تفکیک کانال (Per-Channel PSD)

در آخرین مرحله از ارزیابی، برای اطمینان از صحت عملکرد فیلترها و عدم حذف اطلاعات حیاتی مغز، نمودار چگالی طیفی توان (PSD) برای **تک‌تک کانال‌ها** به صورت جداگانه رسم و بررسی شد. این کار به ما اجازه می‌دهد تا اگر یک کانال خاص رفتار متفاوتی داشت (مثلاً نویز باقی‌مانده یا فیلتر بیش‌از‌حد)، آن را شناسایی کنیم.

### ۱۴-۱. پاسخ به سوالات تئوری گام پنجم

**سوال ۱: چرا در محاسبه PSD از روش Welch استفاده شده است؟ تفاوت اصلی این روش با یک تبدیل فوریه (FFT) ساده روی کل سیگنال چیست؟**
**پاسخ:**
روش FFT ساده اگر مستقیماً روی کل سیگنال نویزی اعمال شود، خروجی دارای واریانس بسیار زیاد و نوسانات شدید (Spiky) خواهد بود که تحلیل آن را دشوار می‌کند.
روش **Welch** یک روش "تخمین طیفی" است که:
1.  سیگنال را به قطعات کوچک‌تر (Windows) با همپوشانی (Overlap) تقسیم می‌کند.
2.  از هر قطعه جداگانه FFT می‌گیرد (Periodogram).
3.  در نهایت میانگین این قطعات را محاسبه می‌کند.
این **میانگین‌گیری** باعث کاهش نویزهای تصادفی، صاف‌تر شدن (Smoothing) نمودار و افزایش دقت تخمین طیف فرکانسی می‌شود.

**سوال ۲: چرا در محور عمودی از مقیاس لگاریتمی استفاده کرده‌ایم؟**
**پاسخ:**
سیگنال‌های مغزی خاصیت **$1/f$** دارند؛ یعنی توان امواج فرکانس پایین (مثل دلتا در ۱ تا ۴ هرتز) بسیار زیاد (مثلاً $100 \mu V^2$) و توان امواج فرکانس بالا (مثل بتا و گاما) بسیار ناچیز (مثلاً $0.1 \mu V^2$) است.
اگر از مقیاس خطی استفاده کنیم، امواج فرکانس بالا در برابر امواج فرکانس پایین مانند یک خط صاف روی صفر دیده می‌شوند و تمام جزئیات آن‌ها گم می‌شود. مقیاس **لگاریتمی (دسی‌بل)** باعث فشرده‌سازی دامنه دینامیکی می‌شود و به ما اجازه می‌دهد تا قله‌های بزرگ فرکانس پایین و جزئیات ریز فرکانس بالا را **همزمان و با وضوح مناسب** مشاهده کنیم.

### ۱۴-۲. تحلیل نمودارهای کانال‌به‌کانال
در تصاویر زیر (نمونه برای آزمودنی‌ها)، خط **قرمز** نشان‌دهنده داده خام و خط **آبی** نشان‌دهنده داده نهایی است.
* **حذف نویز ۵۰ هرتز:** در تمامی کانال‌ها (حتی کانال‌های نویزی مثل Fp1)، قله تیز ۵۰ هرتز که در نمودار قرمز وجود دارد، در نمودار آبی کاملاً حذف شده است.
* **رفتار در فرکانس بالا:** از فرکانس ۴۵ هرتز به بعد، نمودار آبی دچار افت شدید می‌شود که نشان‌دهنده عملکرد صحیح فیلتر پایین‌گذر (Low-pass) است.
* **حفظ قله آلفا:** در کانال‌های پس‌سری (Occipital) و مرکزی، برآمدگی مربوط به موج آلفا (~۱۰ هرتز) در نمودار آبی دقیقاً منطبق بر نمودار قرمز حفظ شده است.

### ۱۴-۳. جدول نتایج نهایی (۱۰ آزمودنی)

| نام آزمودنی | نمودار PSD تفکیکی (Raw vs Clean) |
| :---: | :---: |
| **Subject 01** | ![PSD_Ch](./Steps/Report_Images_Step5_PSD/Subject_01_Channel_PSD.png) |
| **Subject 02** | ![PSD_Ch](./Steps/Report_Images_Step5_PSD/Subject_02_Channel_PSD.png) |
| **Subject 03** | ![PSD_Ch](./Steps/Report_Images_Step5_PSD/Subject_03_Channel_PSD.png) |
| **Subject 04** | ![PSD_Ch](./Steps/Report_Images_Step5_PSD/Subject_04_Channel_PSD.png) |
| **Subject 05** | ![PSD_Ch](./Steps/Report_Images_Step5_PSD/Subject_05_Channel_PSD.png) |
| **Subject 06** | ![PSD_Ch](./Steps/Report_Images_Step5_PSD/Subject_06_Channel_PSD.png) |
| **Subject 07** | ![PSD_Ch](./Steps/Report_Images_Step5_PSD/Subject_07_Channel_PSD.png) |
| **Subject 08** | ![PSD_Ch](./Steps/Report_Images_Step5_PSD/Subject_08_Channel_PSD.png) |
| **Subject 09** | ![PSD_Ch](./Steps/Report_Images_Step5_PSD/Subject_09_Channel_PSD.png) |
| **Subject 10** | ![PSD_Ch](./Steps/Report_Images_Step5_PSD/Subject_10_Channel_PSD.png) |

---

## ۱۵. پیوست کد: تولید نمودارهای شبکه‌ای PSD

کد زیر برای پردازش دسته‌ای ۱۰ فایل و تولید نمودارهای ماتریسی (Grid Plot) با مقیاس لگاریتمی استفاده شده است:
</div>

```python
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
                                       n_fft=int(raw.info['sfreq']*2), verbose=False)
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
                                                  n_fft=int(raw.info['sfreq']*2), verbose=False)
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
```

<div dir="rtl">

---

## ۱۶. گزارش گام ششم: رسم نقشه‌های توپوگرافی (Brain Topomaps)

در این مرحله، هدف مشاهده **توزیع فضایی (Spatial Distribution)** انرژی امواج مغزی روی سر است. برخلاف نمودارهای قبلی که تغییرات را در حوزه زمان یا فرکانس نشان می‌دادند، نقشه‌های توپوگرافی (Topoplot) نشان می‌دهند که کدام ناحیه از مغز (جلوی سر، پشت سر، یا طرفین) در یک باند فرکانسی خاص بیشترین فعالیت را دارد.

برای رسم این نقشه‌ها:
۱. توان سیگنال (PSD) برای تمام کانال‌ها محاسبه شد.
۲. میانگین توان در باندهای تتا، آلفا و بتا استخراج گردید.
۳. مقادیر به مقیاس **دسی‌بل (dB)** تبدیل شدند.
۴. با استفاده از **درون‌یابی (Interpolation)**، فضای خالی بین الکترودها رنگ‌آمیزی شد تا نقشه‌ای پیوسته از سر ایجاد شود.

### ۱۶-۱. پاسخ به سوال تئوری: تفسیر رنگ‌ها و موقعیت‌ها

**سوال: تفسیر شما از رنگ‌ها و موقعیت‌هایی که در هر ناحیه سر می‌بینید چیست؟**

**پاسخ:**
در نقشه‌های توپوگرافی رسم شده با طرح رنگی `RdBu_r`:
* **رنگ قرمز (گرم):** نشان‌دهنده **توان بالا (High Power)** یا فعالیت شدید آن باند فرکانسی در آن ناحیه است.
* **رنگ آبی (سرد):** نشان‌دهنده **توان پایین (Low Power)** یا فعالیت کم است.

**تفسیر فیزیولوژیک بر اساس موقعیت:**
۱.  **باند آلفا (Alpha, 8-12 Hz):** در حالت استراحت با چشمان بسته، باید **بیشترین انرژی (قرمز پررنگ)** را در ناحیه **پس‌سری (Occipital - پشت سر)** داشته باشد. این نشانه سلامت ریتم پایه مغز است.
۲.  **باند تتا (Theta, 4-8 Hz):** افزایش انرژی این باند در حالت بیداری معمولاً نشانه **خواب‌آلودگی** یا عدم تمرکز است. اگر در نواحی مرکزی یا گیجگاهی قرمز شود، نیاز به بررسی دارد.
۳.  **باند بتا (Beta, 12-30 Hz):** این باند مربوط به **تفکر فعال و تمرکز** است و معمولاً در **نواحی پیشانی (Frontal)** دیده می‌شود. دامنه (شدت رنگ) آن معمولاً کمتر از آلفا است.

### ۱۶-۲. جدول نقشه‌های مغزی (۱۰ آزمودنی)

در جدول زیر، توزیع انرژی سه باند اصلی برای تمام آزمودنی‌ها نمایش داده شده است.

| نام آزمودنی | نقشه‌های توپوگرافی (Theta, Alpha, Beta) |
| :---: | :---: |
| **Subject 01** | ![Topo](./Steps/Report_Images_Step6_Topomaps/Subject_01_Topomaps.png) |
| **Subject 02** | ![Topo](./Steps/Report_Images_Step6_Topomaps/Subject_02_Topomaps.png) |
| **Subject 03** | ![Topo](./Steps/Report_Images_Step6_Topomaps/Subject_03_Topomaps.png) |
| **Subject 04** | ![Topo](./Steps/Report_Images_Step6_Topomaps/Subject_04_Topomaps.png) |
| **Subject 05** | ![Topo](./Steps/Report_Images_Step6_Topomaps/Subject_05_Topomaps.png) |
| **Subject 06** | ![Topo](./Steps/Report_Images_Step6_Topomaps/Subject_06_Topomaps.png) |
| **Subject 07** | ![Topo](./Steps/Report_Images_Step6_Topomaps/Subject_07_Topomaps.png) |
| **Subject 08** | ![Topo](./Steps/Report_Images_Step6_Topomaps/Subject_08_Topomaps.png) |
| **Subject 09** | ![Topo](./Steps/Report_Images_Step6_Topomaps/Subject_09_Topomaps.png) |
| **Subject 10** | ![Topo](./Steps/Report_Images_Step6_Topomaps/Subject_10_Topomaps.png) |

---

## ۱۷. پیوست کد: رسم خودکار نقشه‌های مغزی

کد زیر برای محاسبه توان باندها و رسم نقشه‌های توپوگرافی به صورت خودکار برای تمام فایل‌ها استفاده شده است:
</div>

```python
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

# پارامترهای پردازش (مشابه گام‌های قبل برای یکسان بودن نتایج)
low_cut = 0.5
high_cut = 45.0
notch_freq = 50.0
epoch_dur = 2.0
n_ica_components = 15

# تعریف باندهای فرکانسی برای رسم نقشه
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

        # تنظیم مکان سنسورها (حیاتی برای Topomap)
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, match_case=False)
        except ValueError:
            print("   !!! Warning: Standard 10-20 montage not found. Skipping plot.")
            continue # بدون مونتاژ نمی‌توان نقشه رسم کرد

        raw.pick_types(eeg=True, eog=False, stim=False, exclude='bads')

        # ---------------------------------------------------------
        # 2. پایپ‌لاین تمیزسازی (Filter -> Epoch -> AR -> ICA)
        # ---------------------------------------------------------
        # الف) فیلترها
        raw.notch_filter(notch_freq, verbose=False)
        raw.filter(low_cut, high_cut, verbose=False)

        # ب) اپوک‌بندی
        epochs = mne.make_fixed_length_epochs(raw, duration=epoch_dur, preload=True, verbose=False)

        # ج) AutoReject (تمیزسازی داده‌های پرت)
        ar = AutoReject(n_interpolate=[1, 2], consensus=[0.6], random_state=42, verbose=False)
        epochs_clean = ar.fit_transform(epochs)

        # د) ICA (حذف آرتیفکت چشم)
        ica = ICA(n_components=n_ica_components, max_iter='auto', random_state=97)
        ica.fit(epochs_clean, verbose=False)
        
        # شناسایی اتوماتیک با کانال Fp1
        eog_inds, _ = ica.find_bads_eog(epochs_clean, ch_name='Fp1', threshold=2.5)
        if eog_inds:
            ica.exclude = eog_inds
        
        epochs_final = epochs_clean.copy()
        ica.apply(epochs_final, verbose=False)

        # ---------------------------------------------------------
        # 3. محاسبات طیفی و رسم نقشه‌ها (Step 6 Logic)
        # ---------------------------------------------------------
        print("   -> Calculating PSD and generating Topomaps...")
        
        # محاسبه PSD به روش Welch روی داده‌های نهایی
        spectrum = epochs_final.compute_psd(method='welch', fmin=1, fmax=40, n_fft=int(raw.info['sfreq']*2), verbose=False)
        psds, freqs = spectrum.get_data(return_freqs=True)
        
        # میانگین‌گیری روی تمام اپوک‌ها (average over time)
        # shape: (n_channels, n_freqs)
        psds_mean = psds.mean(axis=0)

        # ایجاد شکل نمودار (1 سطر و 3 ستون)
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        fig.suptitle(f'Spatial Distribution of Brain Rhythms: {subject_name}', fontsize=16)

        # حلقه روی باندهای فرکانسی
        for ax, (band_name, (fmin, fmax)) in zip(axes, freq_bands.items()):
            # پیدا کردن اندیس‌های فرکانسی
            freq_indices = np.where((freqs >= fmin) & (freqs <= fmax))[0]
            
            # میانگین توان در آن باند برای هر کانال
            band_power = psds_mean[:, freq_indices].mean(axis=1)
            
            # تبدیل به دسی‌بل (Log Scale)
            band_power_db = 10 * np.log10(band_power)
            
            # رسم Topomap
            im, _ = mne.viz.plot_topomap(
                band_power_db,
                epochs_final.info,
                axes=ax,
                show=False,
                cmap='RdBu_r',       # قرمز = بالا، آبی = پایین
                names=epochs_final.ch_names,
                show_names=False,
                contours=6
            )
            ax.set_title(band_name, fontsize=12)

        # اضافه کردن Colorbar (مشترک یا سمت راست)
        cbar_ax = fig.add_axes([0.92, 0.15, 0.015, 0.7]) # [left, bottom, width, height]
        clb = fig.colorbar(im, cax=cbar_ax)
        clb.set_label('Power Spectral Density (dB)')

        # ذخیره تصویر
        save_name = os.path.join(output_folder, f"{subject_name}_Topomaps.png")
        plt.savefig(save_name, bbox_inches='tight')
        plt.close(fig)  # بستن برای آزادسازی حافظه

        print(f"   -> Saved: {subject_name}_Topomaps.png")

    except Exception as e:
        print(f"   !!! Error processing {subject_name}: {e}")

print("\n" + "=" * 60)
print("Step 6 Processing Complete!")
print(f"Check folder: {output_folder}")
```


<div dir="rtl">

---

## ۱۸. گزارش گام هفتم: تحلیل اتصال‌پذیری مغزی (Connectivity Analysis)

هدف نهایی این پروژه، فراتر از بررسی فعالیت تک‌تک کانال‌ها، درک **تعاملات و ارتباطات (Interactions)** بین نواحی مختلف مغز است. در این گام، "اتصال‌پذیری عملکردی" (Functional Connectivity) محاسبه شد تا مشخص شود کدام نواحی مغز به صورت هماهنگ با هم فعالیت می‌کنند و شبکه مغزی (Brain Network) را تشکیل می‌دهند.

### ۱۸-۱. روش پیاده‌سازی (Amplitude-based)
طبق دستورالعمل پروژه، به جای استفاده از توابع آماده‌ای که مستقیماً اتصال را خروجی می‌دهند، الگوریتم به صورت دستی و مرحله‌به‌مرحله بر اساس **همبستگی پوش سیگنال** پیاده‌سازی شد:

1.  **فیلترینگ:** داده‌های تمیز شده (Clean Epochs) در سه باند تتا، آلفا و بتا جدا شدند.
2.  **استخراج پوش (Envelope):** با استفاده از **تبدیل هیلبرت (Hilbert Transform)**، سیگنال تحلیلی محاسبه شد. سپس قدرمطلق آن گرفته شد تا "پوش لحظه‌ای" (Envelope) سیگنال بدست آید.
3.  **محاسبه همبستگی:** ضریب **همبستگی پیرسون (Pearson Correlation)** بین پوش سیگنال تمام جفت-کانال‌ها محاسبه گردید. این معیار نشان می‌دهد که آیا افزایش انرژی در یک ناحیه با افزایش انرژی در ناحیه دیگر همراه است یا خیر.
4.  **آستانه‌گذاری (Thresholding):** برای جلوگیری از شلوغی نمودار و نمایش تنها ارتباطات قوی و معنادار، مقادیر همبستگی کمتر از یک حد مشخص (در اینجا ۰.۵) حذف (صفر) شدند.

### ۱۸-۲. پاسخ به سوالات تئوری گام هفتم

**سوال ۱: چرا تحلیل اتصال‌پذیری روی اپوک‌های کوتاه (مثلاً ۲ ثانیه) انجام می‌شود؟**
**پاسخ:**
سیگنال EEG ذاتاً **غیر-ایستا (Non-stationary)** است؛ یعنی ویژگی‌های آماری آن (مثل میانگین و واریانس) در طول زمان تغییر می‌کند. اما اگر بازه‌های زمانی را کوتاه در نظر بگیریم، می‌توان با تقریب خوبی فرض کرد سیگنال در آن بازه "شبه-ایستا" (Quasi-stationary) است. این فرض ایستایی برای اعتبار ریاضی محاسبات همبستگی و تحلیل‌های طیفی ضروری است.

**سوال ۲: تفاوت روش مبتنی بر دامنه (Amplitude) با فاز (Phase) چیست؟**
**پاسخ:**
* **اتصال مبتنی بر دامنه (Amplitude/Envelope Correlation):** بررسی می‌کند که آیا "شدت انرژی" دو ناحیه همزمان بالا و پایین می‌رود؟ (مثلاً وقتی پشت سر فعال می‌شود، آیا جلوی سر هم همزمان فعال می‌شود؟). این روش ساده و شهودی است اما ممکن است تحت تاثیر "هدایت حجمی" قرار گیرد.
* **اتصال مبتنی بر فاز (Phase Synchronization):** بررسی می‌کند که آیا نوسانات دو سیگنال با هم "هم‌گام" هستند یا خیر (اختلاف فاز ثابت)، حتی اگر دامنه‌هایشان متفاوت باشد. این روش پیچیده‌تر است اما اطلاعات زمانی دقیق‌تری از سرعت انتقال پیام می‌دهد.

### ۱۸-۳. نتایج اتصال‌پذیری (۱۰ آزمودنی)
در نمودارهای دایره‌ای زیر، هر خط نشان‌دهنده یک **ارتباط عملکردی قوی** (بالای آستانه ۵۰٪) بین دو الکترود است. رنگ خطوط نشان‌دهنده شدت همبستگی است.

| نام آزمودنی | نمودار اتصال‌پذیری (Connectivity Circle) |
| :---: | :---: |
| **Subject 01** | ![Conn](./Steps/Report_Images_Step7_Connectivity/Subject_01_Connectivity.png) |
| **Subject 02** | ![Conn](./Steps/Report_Images_Step7_Connectivity/Subject_02_Connectivity.png) |
| **Subject 03** | ![Conn](./Steps/Report_Images_Step7_Connectivity/Subject_03_Connectivity.png) |
| **Subject 04** | ![Conn](./Steps/Report_Images_Step7_Connectivity/Subject_04_Connectivity.png) |
| **Subject 05** | ![Conn](./Steps/Report_Images_Step7_Connectivity/Subject_05_Connectivity.png) |
| **Subject 06** | ![Conn](./Steps/Report_Images_Step7_Connectivity/Subject_06_Connectivity.png) |
| **Subject 07** | ![Conn](./Steps/Report_Images_Step7_Connectivity/Subject_07_Connectivity.png) |
| **Subject 08** | ![Conn](./Steps/Report_Images_Step7_Connectivity/Subject_08_Connectivity.png) |
| **Subject 09** | ![Conn](./Steps/Report_Images_Step7_Connectivity/Subject_09_Connectivity.png) |
| **Subject 10** | ![Conn](./Steps/Report_Images_Step7_Connectivity/Subject_10_Connectivity.png) |

---

## ۱۹. پیوست کد: محاسبه دستی اتصال‌پذیری و رسم گراف

کد زیر پیاده‌سازی کامل گام هفتم شامل استفاده از `scipy.signal.hilbert` برای استخراج ویژگی و رسم گراف نهایی با `mne-connectivity` است:
</div>

```python
# ==========================================
# Ghasem Step 7: Connectivity Analysis (Manual Implementation)
# ==========================================
import mne
import numpy as np
import matplotlib.pyplot as plt
from autoreject import AutoReject
from mne.preprocessing import ICA
from mne_connectivity.viz import plot_connectivity_circle
from scipy.signal import hilbert
import glob
import os

# ... (بخش‌های بارگذاری داده مشابه گام‌های قبل) ...

# ---------------------------------------------------------
# تحلیل اتصال‌پذیری (Connectivity Logic)
# ---------------------------------------------------------
print("   -> Calculating Connectivity (Envelope Correlation)...")

node_names = epochs_final.ch_names
bands = {"Theta": (4, 8), "Alpha": (8, 12), "Beta": (12, 30)}
corr_threshold = 0.5  # آستانه نمایش ارتباطات

fig = plt.figure(figsize=(18, 6), facecolor='black') 

for i, (band_name, (l_freq, h_freq)) in enumerate(bands.items()):
    # الف) فیلتر در باند خاص
    epochs_band = epochs_final.copy().filter(l_freq=l_freq, h_freq=h_freq, verbose=False)
    
    # ب) تبدیل هیلبرت و استخراج پوش (Envelope)
    data = epochs_band.get_data(copy=True) 
    analytic_signal = hilbert(data)
    envelope = np.abs(analytic_signal) # قدرمطلق سیگنال تحلیلی
    
    # ج) چسباندن اپوک‌ها برای همبستگی (Concatenate)
    n_epochs, n_channels, n_times = envelope.shape
    envelope_concat = envelope.transpose(1, 0, 2).reshape(n_channels, -1)
    
    # د) محاسبه ماتریس همبستگی (Pearson Correlation)
    con_matrix = np.corrcoef(envelope_concat)
    con_matrix = np.nan_to_num(con_matrix) # رفع خطای احتمالی
    
    # هـ) آستانه‌گذاری (Thresholding)
    np.fill_diagonal(con_matrix, 0) # حذف قطر اصلی
    
    # بررسی وجود اتصال معنادار
    if np.max(np.abs(con_matrix)) < corr_threshold:
        continue
        
    con_matrix[np.abs(con_matrix) < corr_threshold] = 0 # صفر کردن مقادیر ضعیف
    
    # و) رسم نمودار دایره‌ای
    ax, _ = plot_connectivity_circle(
        con_matrix, 
        node_names, 
        n_lines=300,
        subplot=(1, 3, i + 1),
        title=band_name,
        textcolor='white',
        facecolor='black',
        vmin=0, vmax=1, # نرمال‌سازی رنگ
        show=False
    )
plt.show()
```

<div dir="rtl">

---

## ۲۰. گزارش گام هشتم: سیستم تشخیص خودکار (Automated Diagnosis)

این مرحله، گام نهایی و نتیجه‌گیری کل پروژه است. در اینجا ما از داده‌های خامی که در هفت مرحله قبل تمیز و پردازش کردیم، برای **استخراج ویژگی‌های کمی (Feature Extraction)** استفاده می‌کنیم تا وضعیت ذهنی آزمودنی را بدون دخالت انسان تشخیص دهیم.

### ۲۰-۱. متدولوژی و تعریف شاخص‌ها
برای تبدیل سیگنال مغزی به یک "تشخیص پزشکی"، از نسبت‌های توانی باندها استفاده شده است. این نسبت‌ها استاندارد هستند و در سیستم‌های نوروفیدبک کاربرد دارند:

۱. **شاخص خواب‌آلودگی (Drowsiness Index):**
این شاخص از نسبت توان باند **آلفا به بتا ($\frac{\alpha}{\beta}$)** به دست می‌آید.
* **تفسیر:** موج آلفا نشانگر استراحت و موج بتا نشانگر هوشیاری است. غلبه آلفا یعنی مغز به سمت خواب‌آلودگی می‌رود.

۲. **شاخص عدم تمرکز (Inattention Index):**
این شاخص از نسبت توان باند **تتا به بتا ($\frac{\theta}{\beta}$)** به دست می‌آید (معروف به نسبت TBR در تشخیص ADHD).
* **تفسیر:** موج تتا با پرسه زدن ذهن و گیجی مرتبط است، در حالی که بتا با تمرکز بیرونی. افزایش این نسبت نشانه حواس‌پرتی است.

### ۲۰-۲. نتایج تشخیص وضعیت (۱۰ آزمودنی)
در جدول زیر، نقشه‌های مغزی مربوط به این دو شاخص برای تمام آزمودنی‌ها ترسیم شده است. نواحی **قرمز** در نقشه سمت چپ نشان‌دهنده خواب‌آلودگی و در نقشه سمت راست نشان‌دهنده عدم تمرکز هستند.

| نام آزمودنی | نقشه‌های تشخیص (Drowsiness & Inattention) | نتیجه تشخیص خودکار (خروجی الگوریتم) |
| :---: | :---: | :---: |
| **Subject 01** | ![Diag](./Steps/Report_Images_Step8_Diagnosis/Subject_01_Diagnosis_Map.png) | *Normal / Good Focus* |
| **Subject 02** | ![Diag](./Steps/Report_Images_Step8_Diagnosis/Subject_02_Diagnosis_Map.png) | *(نتیجه فایل متنی)* |
| **Subject 03** | ![Diag](./Steps/Report_Images_Step8_Diagnosis/Subject_03_Diagnosis_Map.png) | *(نتیجه فایل متنی)* |
| **Subject 04** | ![Diag](./Steps/Report_Images_Step8_Diagnosis/Subject_04_Diagnosis_Map.png) | *(نتیجه فایل متنی)* |
| **Subject 05** | ![Diag](./Steps/Report_Images_Step8_Diagnosis/Subject_05_Diagnosis_Map.png) | *(نتیجه فایل متنی)* |
| **Subject 06** | ![Diag](./Steps/Report_Images_Step8_Diagnosis/Subject_06_Diagnosis_Map.png) | *(نتیجه فایل متنی)* |
| **Subject 07** | ![Diag](./Steps/Report_Images_Step8_Diagnosis/Subject_07_Diagnosis_Map.png) | *(نتیجه فایل متنی)* |
| **Subject 08** | ![Diag](./Steps/Report_Images_Step8_Diagnosis/Subject_08_Diagnosis_Map.png) | *(نتیجه فایل متنی)* |
| **Subject 09** | ![Diag](./Steps/Report_Images_Step8_Diagnosis/Subject_09_Diagnosis_Map.png) | *(نتیجه فایل متنی)* |
| **Subject 10** | ![Diag](./Steps/Report_Images_Step8_Diagnosis/Subject_10_Diagnosis_Map.png) | *(نتیجه فایل متنی)* |

---

## ۲۱. پاسخ به سوال تحلیلی گام آخر

**سوال: با توجه به مقادیری که از این شاخص‌ها بدست می‌آورید، وضعیت آزمودنی را چگونه تفسیر می‌کنید؟ (قوانین سیستم خبره)**

**پاسخ:**
بر اساس مقالات علمی و اسلایدهای درس، سیستم تشخیص خودکار ما بر اساس قوانین شرطی (Rule-based) زیر تصمیم‌گیری می‌کند:

**۱. تحلیل نسبت Alpha/Beta (سطح هوشیاری):**
* **اگر مقدار > ۱.۵ باشد:** فرد در وضعیت **خواب‌آلودگی یا ریلکسیشن عمیق** قرار دارد (غلبه امواج آلفا با کاهش انگیختگی ذهنی مرتبط است).
* **اگر مقدار < ۰.۸ باشد:** فرد **بسیار هوشیار، فعال یا حتی مضطرب** است (افزایش توان بتا نشان‌دهنده تمرکز بالا یا فعالیت شناختی شدید است).
* **بین ۰.۸ تا ۱.۵:** فرد در حالت **تعادل و نرمال** قرار دارد.

**۲. تحلیل نسبت Theta/Beta (سطح تمرکز):**
* **اگر مقدار > ۲.۰ باشد:** احتمال **کاهش تمرکز یا حواس‌پرتی (Mind Wandering)** وجود دارد. این الگوی غالب در اختلال نقص توجه (ADHD) نیز دیده می‌شود.
* **اگر مقدار <= ۲.۰ باشد:** فرد دارای سطح **تمرکز طبیعی و قابل قبول** است (تعادل مناسب بین فعالیت شناختی و آرامش ذهنی برقرار است).

---

## ۲۲. پیوست کد: پیاده‌سازی سیستم تشخیص خودکار

کد زیر برای محاسبه نسبت‌های توان، رسم نقشه‌ها و تولید گزارش متنی (Diagnosis Report) برای تمام فایل‌ها استفاده شده است:
</div>

```python
# ==========================================
# Ghasem Step 8: Automated Diagnosis System
# ==========================================
print("\n" + "=" * 40)
print("STARTING STEP 8: Final Automated Diagnosis")
print("=" * 40)

import numpy as np
import matplotlib.pyplot as plt
import mne
import os

# ... (بارگذاری و پیش‌پردازش داده‌ها مشابه قبل) ...

# ---------------------------------------------------------
# 1. محاسبه چگالی طیفی توان (PSD) و استخراج باندها
# ---------------------------------------------------------
print("   -> Calculating Band Powers and Ratios...")

# محاسبه PSD (روش Welch)
spectrum = epochs_final.compute_psd(method='welch', fmin=3, fmax=35, n_fft=int(raw.info['sfreq'] * 2), verbose=False)
psds, freqs = spectrum.get_data(return_freqs=True)
psds_mean = psds.mean(axis=0) # میانگین روی اپوک‌ها

# تابع استخراج انرژی باند
def get_band_power(f_low, f_high):
    idx = np.logical_and(freqs >= f_low, freqs <= f_high)
    return psds_mean[:, idx].mean(axis=1)

# محاسبه انرژی باندهای حیاتی
theta = get_band_power(4, 8)
alpha = get_band_power(8, 12)
beta  = get_band_power(12, 30)

# ---------------------------------------------------------
# 2. محاسبه شاخص‌های طلایی (Indices)
# ---------------------------------------------------------
# الف) شاخص خواب‌آلودگی
drowsiness_index = alpha / beta

# ب) شاخص عدم تمرکز
inattention_index = theta / beta

# ---------------------------------------------------------
# 3. سیستم خبره (Expert System Interpretation)
# ---------------------------------------------------------
avg_ab = np.mean(drowsiness_index)
avg_tb = np.mean(inattention_index)

# تفسیر هوشیاری
if avg_ab > 1.5:
    status_ab = "DROWSY / RELAXED"
elif avg_ab < 0.8:
    status_ab = "ALERT / ANXIOUS"
else:
    status_ab = "NORMAL"

# تفسیر تمرکز
if avg_tb > 2.0:
    status_tb = "LOW FOCUS (Mind Wandering)"
else:
    status_tb = "GOOD FOCUS"

print(f"   -> Diagnosis Result: {status_ab} | {status_tb}")

# ---------------------------------------------------------
# 4. رسم نقشه‌های مغزی (Topomaps)
# ---------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# نقشه خواب‌آلودگی
im1, _ = mne.viz.plot_topomap(drowsiness_index, epochs_final.info, axes=axes[0], show=False, cmap='RdBu_r', contours=6)
axes[0].set_title('Drowsiness (Alpha/Beta)\nRed = Drowsy')

# نقشه عدم تمرکز
im2, _ = mne.viz.plot_topomap(inattention_index, epochs_final.info, axes=axes[1], show=False, cmap='Wistia', contours=6)
axes[1].set_title('Inattention (Theta/Beta)\nDarker = Low Focus')

plt.tight_layout()
plt.show()
```
