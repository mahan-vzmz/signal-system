import mne
import matplotlib.pyplot as plt
from autoreject import AutoReject
from mne.preprocessing import ICA
import glob
import os

# 1. تنظیم مسیرها
# -----------------------------
input_folder = "C:/Users/Victus 16/PycharmProjects/SignalSystem/subjects/"
output_folder = "Report_Images_Step3_ICA"  # پوشه خروجی جدید
os.makedirs(output_folder, exist_ok=True)

print(f"ICA Images will be saved in: {os.getcwd()}\\{output_folder}")

# پیدا کردن فایل‌ها
all_files = glob.glob(os.path.join(input_folder, "Subject_*.edf"))
all_files.sort()

# تنظیمات
low_cut = 0.5
high_cut = 45.0
notch_freq = 50.0
epoch_dur = 2.0
n_ica_components = 15  # تعداد مولفه‌های ICA

# ==========================================
# شروع حلقه پردازش
# ==========================================
for file_path in all_files:
    subject_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"\n" + "=" * 40)
    print(f"Processing ICA for: {subject_name}")
    print("=" * 40)

    try:
        # --- الف) آماده‌سازی داده (تکرار مراحل قبل) ---
        raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)

        # اصلاح نام کانال‌ها
        mapping = {name: name.replace('-LE', '') for name in raw.ch_names if '-LE' in name}
        raw.rename_channels(mapping)

        # تنظیم Trig/Montage
        if 'Trig' in raw.ch_names:
            raw.set_channel_types({'Trig': 'stim'})

        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, match_case=False)
        except:
            print("   Warning: Montage not set (ICA maps might look weird).")

        raw.pick_types(eeg=True, eog=False, stim=False, exclude='bads')

        # فیلتر
        raw.notch_filter(notch_freq, verbose=False)
        raw.filter(low_cut, high_cut, verbose=False)

        # قطعه‌بندی
        epochs = mne.make_fixed_length_epochs(raw, duration=epoch_dur, preload=True, verbose=False)

        # تمیزسازی با AutoReject (برای اینکه ICA روی داده تمیز یاد بگیرد)
        # نکته: برای سرعت بیشتر، پارامترها را کمی سبک‌تر گرفتیم
        ar = AutoReject(n_interpolate=[1, 2], consensus=[0.6], random_state=42, verbose=False)
        epochs_clean = ar.fit_transform(epochs)

        # --- ب) اجرای ICA ---
        print("   -> Fitting ICA...")
        ica = ICA(n_components=n_ica_components, max_iter='auto', random_state=97)
        ica.fit(epochs_clean)

        # --- ج) ذخیره تصاویر مولفه‌ها (Topomap) ---
        # این مهم‌ترین بخش است: ذخیره عکسی که نشان می‌دهد هر مولفه چه شکلی است
        print("   -> Saving ICA Components Image...")

        # رسم کامپوننت‌ها
        fig_ica = ica.plot_components(show=False)

        # اضافه کردن عنوان
        # (متاسفانه plot_components عنوان کلی ندارد، روی فایل ذخیره شده اسم را می‌زنیم)
        save_path_ica = os.path.join(output_folder, f"{subject_name}_ICA_Components.png")
        fig_ica.savefig(save_path_ica)
        plt.close(fig_ica)

        print(f"   -> Saved: {subject_name}_ICA_Components.png")

        # --- د) (اختیاری) شناسایی اتوماتیک پلک چشم ---
        # اگر بخواهیم هوشمند عمل کنیم و فقط گزارش نگیریم:
        # معمولا کانال Fp1 یا Fp2 نماینده خوبی برای چشم هستند.
        eog_inds, scores = ica.find_bads_eog(epochs_clean, ch_name='Fp1', threshold=2.5)

        if eog_inds:
            print(f"   -> Auto-detected potential blink components: {eog_inds}")
            # ذخیره یک فایل متنی کنار عکس‌ها که بگوید سیستم چه پیشنهادی داده
            with open(os.path.join(output_folder, "Suggested_Bads.txt"), "a") as f:
                f.write(f"{subject_name}: {eog_inds}\n")
        else:
            print("   -> No clear blink artifacts detected automatically.")

    except Exception as e:
        print(f"   !!! Error processing {subject_name}: {e}")

print("\n" + "=" * 40)
print("Done! Now check 'Report_Images_Step3_ICA' folder.")
print("Open the images and look for 'Red/Blue' circles at the very front of the head.")