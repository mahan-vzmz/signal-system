import mne
import numpy as np
import matplotlib.pyplot as plt
from autoreject import AutoReject
from mne.preprocessing import ICA
# ایمپورت صحیح برای نسخه جدید MNE
from mne_connectivity.viz import plot_connectivity_circle
from scipy.signal import hilbert
import glob
import os

# ==========================================
# 1. تنظیمات مسیرها و پارامترها
# ==========================================
input_folder = "C:/Users/Victus 16/PycharmProjects/SignalSystem/subjects/"
output_folder = "Report_Images_Step7_Connectivity"
os.makedirs(output_folder, exist_ok=True)

print(f"Connectivity Images will be saved in: {os.getcwd()}\\{output_folder}")

# پیدا کردن تمام فایل‌های EDF
all_files = glob.glob(os.path.join(input_folder, "Subject_*.edf"))
all_files.sort()

# پارامترهای پردازش سیگنال
low_cut = 0.5
high_cut = 45.0
notch_freq = 50.0
epoch_dur = 2.0
n_ica_components = 15

# پارامترهای اتصال‌پذیری
# آستانه: فقط ارتباطات قوی‌تر از 50 درصد نمایش داده شوند
corr_threshold = 0.4

# باندهای فرکانسی
bands = {
    "Theta": (4, 8),
    "Alpha": (8, 12),
    "Beta": (12, 30)
}

# ==========================================
# شروع حلقه پردازش روی تمام فایل‌ها
# ==========================================
for file_path in all_files:
    subject_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"\n" + "=" * 60)
    print(f"Processing Connectivity for: {subject_name}")
    print("=" * 60)

    try:
        # ---------------------------------------------------------
        # بخش ۱: آماده‌سازی داده (Filter, Epoch, AutoReject, ICA)
        # ---------------------------------------------------------
        raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)

        # اصلاح نام کانال‌ها
        mapping = {name: name.replace('-LE', '') for name in raw.ch_names if '-LE' in name}
        raw.rename_channels(mapping)
        if 'Trig' in raw.ch_names: raw.set_channel_types({'Trig': 'stim'})

        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, match_case=False)
        except:
            print("   Warning: Montage not set (Plots might lack colors).")

        raw.pick_types(eeg=True, eog=False, stim=False, exclude='bads')

        # فیلترها
        raw.notch_filter(notch_freq, verbose=False)
        raw.filter(low_cut, high_cut, verbose=False)

        # اپوک‌بندی
        epochs = mne.make_fixed_length_epochs(raw, duration=epoch_dur, preload=True, verbose=False)

        # تمیزسازی با AutoReject
        ar = AutoReject(n_interpolate=[1, 2], consensus=[0.6], random_state=42, verbose=False)
        epochs_clean = ar.fit_transform(epochs)

        # حذف آرتیفکت با ICA
        ica = ICA(n_components=n_ica_components, max_iter='auto', random_state=97)
        ica.fit(epochs_clean, verbose=False)

        # تشخیص اتوماتیک پلک با کانال Fp1
        eog_inds, _ = ica.find_bads_eog(epochs_clean, ch_name='Fp1', threshold=2.5)
        if eog_inds:
            ica.exclude = eog_inds

        epochs_final = epochs_clean.copy()
        ica.apply(epochs_final, verbose=False)

        # ---------------------------------------------------------
        # بخش ۲: تحلیل اتصال‌پذیری و رسم نمودار
        # ---------------------------------------------------------
        print("   -> Calculating Connectivity & Plotting...")

        node_names = epochs_final.ch_names

        # تنظیم سایز فیگور: (عرض 14، ارتفاع 5) برای فیت شدن سه دایره کنار هم
        fig = plt.figure(figsize=(14, 5), facecolor='black')

        # حلقه روی باندهای فرکانسی (Theta, Alpha, Beta)
        for i, (band_name, (l_freq, h_freq)) in enumerate(bands.items()):

            # الف) فیلتر در باند خاص
            epochs_band = epochs_final.copy().filter(l_freq=l_freq, h_freq=h_freq, verbose=False)

            # ب) محاسبه پوش (Envelope) با تبدیل هیلبرت
            data = epochs_band.get_data(copy=True)  # (n_epochs, n_channels, n_times)
            analytic_signal = hilbert(data)
            envelope = np.abs(analytic_signal)

            # ج) آماده‌سازی برای همبستگی (چسباندن اپوک‌ها)
            n_epochs, n_channels, n_times = envelope.shape
            envelope_concat = envelope.transpose(1, 0, 2).reshape(n_channels, -1)

            # د) ماتریس همبستگی
            con_matrix = np.corrcoef(envelope_concat)
            con_matrix = np.nan_to_num(con_matrix)  # تبدیل NaN به 0 برای جلوگیری از خطا

            # هـ) اعمال آستانه
            np.fill_diagonal(con_matrix, 0)  # حذف قطر اصلی

            # اگر هیچ اتصالی قوی‌تر از آستانه نبود، رسم نکن تا خطا ندهد
            if np.max(np.abs(con_matrix)) < corr_threshold:
                print(f"      [Info] No strong connections in {band_name} band.")
                continue

            con_matrix[np.abs(con_matrix) < corr_threshold] = 0  # صفر کردن مقادیر ضعیف

            # و) رسم دایره در ساب‌لات مربوطه
            # vmin=0, vmax=1 باعث می‌شود طیف رنگی ثابت باشد و ارور تقسیم بر صفر ندهد
            ax, _ = plot_connectivity_circle(
                con_matrix,
                node_names,
                n_lines=300,
                subplot=(1, 3, i + 1),  # (تعداد سطر، تعداد ستون، اندیس فعلی)
                title=band_name,
                fontsize_title=14,
                fontsize_names=10,
                textcolor='white',
                facecolor='black',
                linewidth=1.2,
                vmin=0, vmax=1,  # حیاتی برای جلوگیری از ارور
                show=False
            )

        # ---------------------------------------------------------
        # بخش ۳: تنظیمات نهایی ظاهر (Layout) و ذخیره
        # ---------------------------------------------------------

        # تایتل اصلی حذف شد تا فضا باز شود
        # plt.suptitle(...)

        # فشرده‌سازی المان‌ها برای پر کردن کادر
        plt.tight_layout(pad=0.5, w_pad=1.0, h_pad=1.0)

        save_name = os.path.join(output_folder, f"{subject_name}_Connectivity.png")

        # ذخیره بدون حاشیه اضافه
        plt.savefig(save_name, facecolor='black', bbox_inches='tight', pad_inches=0)
        plt.close(fig)

        print(f"   -> Saved: {subject_name}_Connectivity.png")

    except Exception as e:
        print(f"   !!! Error processing {subject_name}: {e}")

print("\n" + "=" * 60)
print("Step 7 Processing Complete!")
print(f"Check folder: {output_folder}")