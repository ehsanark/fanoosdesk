# فانوس دسک | Fanoos Desk

کلاینت فارسی و راست‌چین دسترسی از راه دور، مشتق از Khavaran Desk و مبتنی بر RustDesk OSS.

## اتصال

پیش‌فرض کلاینت همان IP و کلید عمومی نسخه خاوران است. برای تغییر روی یک دستگاه، «تنظیمات سرور فانوس» را باز کنید، ID Server و Relay Server و کلید عمومی را وارد و ذخیره کنید. API Server در نسخه OSS خالی می‌ماند. کلید عمومی سرور تازه را با `sudo fanoos-server key` بخوانید.

پیش‌فرض ساخت‌های بعدی را در [server-defaults.json](build/server-defaults.json) تغییر دهید. تنظیمات ذخیره‌شدهٔ کاربر اولویت دارند.

## نصب

بسته‌ها پس از ساخت موفق در [Releases](https://github.com/ehsanark/fanoosdesk/releases) قرار می‌گیرند.

- ویندوز x64 — نصاب FanoosDesk-Client-Windows-x64.exe، بدون امضای دیجیتال.
- جتسون Orin Nano ARM64 — بستهٔ Debian را با `sudo apt install ./FanoosDesk-Client-Jetson-Orin-Nano-arm64.deb` نصب کنید.
- سرور لینوکس x64 یا ARM64 — آرشیو متناسب با معماری را استخراج کنید و از داخل پوشه `sudo ./install.sh` اجرا کنید. [راهنمای سرویس‌ها و پورت‌ها](server/README.md)

سرویس‌های خاوران و فانوس به صورت پیش‌فرض پورت‌های یکسان دارند. نصب تازه مسیر دادهٔ مستقلی دارد و کلید خودش را می‌سازد. پیش از جابه‌جایی، پایگاه داده و کلیدهای سرور فعلی را پشتیبان بگیرید.

## Source

Derived from [Khavaran Desk](https://github.com/ehsanark/khavarandesk) at 43874b252d3019ea86b9ff439525b2725957ccd4. Client builds use pinned RustDesk commit a7f2260203befb7e9c70b585219f0f0b5ca57703. Server packages use official RustDesk Server OSS 1.1.16 binaries. AGPL-3.0. Upstream copyright notices are retained.
