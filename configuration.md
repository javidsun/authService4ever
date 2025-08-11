
# 📄 مستند آموزش پیاده‌سازی Login & Register (Mock) با React Native + Expo Router

## 🎯 هدف
پیاده‌سازی سیستم ورود (Login) و ثبت‌نام (Register) در اپ موبایل با React Native و Expo Router.
فعلاً از Mock استفاده شده تا بعداً بتوانیم آن را با API واقعی جایگزین کنیم.

---

## 🗂 ساختار پروژه

```
app/
  _layout.tsx         → Root Layout (RouteGuard + Providerها)
  (auth)/
    _layout.tsx       → Stack صفحات Login/Register
    login.tsx
    register.tsx
  (app)/
    _layout.tsx       → Stack صفحات خصوصی
    index.tsx
src/
  context/
    AuthContext.tsx   → مدیریت وضعیت کاربر
  services/
    authClient.ts     → رابط Auth (الان Mock، بعداً API)
  mock/
    authMock.ts       → بک‌اند جعلی (In-memory)
  ui/
    FormTextInput.tsx → کامپوننت ورودی
    PrimaryButton.tsx → دکمه
```

---

## 🔄 جریان کار (Flow)

![Auth Flow](auth_flow.png)

1. **شروع اپ** → AuthProvider و RouteGuard لود می‌شوند.
2. RouteGuard بررسی می‌کند که کاربر وارد شده یا نه.
3. اگر وارد شده → به `(app)` می‌رود.
4. اگر وارد نشده → به `(auth)/login` می‌رود.
5. کاربر فرم لاگین یا ثبت‌نام را پر می‌کند (Formik + Yup).
6. authClient درخواست را به authMock می‌فرستد.
7. authMock بررسی کاربر و پسورد را انجام می‌دهد و توکن‌های جعلی می‌سازد.
8. توکن‌ها در Storage (SecureStore/AsyncStorage) ذخیره می‌شوند.
9. کاربر به Home Screen خصوصی هدایت می‌شود.
10. با Logout → توکن‌ها پاک شده و کاربر به صفحه لاگین برمی‌گردد.

---

## 🧠 نکات مهم

- در Root Layout نباید `<Stack>` باشد تا خطای EnsureSingleNavigator نیاید.
- هر گروه Route (`(auth)`, `(app)`) باید `_layout.tsx` و Stack خودش را داشته باشد.
- AuthContext وضعیت و متدهای login/register/logout را مدیریت می‌کند.
- authClient رابط بین اپ و منبع Auth است (الان Mock، بعداً API).
- authMock فقط برای تست است، پسوردها را Plain Text نگه می‌دارد.

---

## 🚀 مراحل اجرا

1. نصب پکیج‌ها:
```bash
npm i formik yup axios @react-navigation/native-stack
npx expo install @react-native-async-storage/async-storage expo-secure-store
```

2. ایجاد فایل‌ها طبق ساختار بالا.

3. اجرای پروژه:
```bash
npm start
```

4. تست:
- رفتن به `/(auth)/register` و ثبت‌نام.
- ورود خودکار به `(app)`.
- خروج و بازگشت به لاگین.

---

## ⏭ قدم بعدی
- جایگزین کردن authMock با API واقعی (FastAPI Auth Service).
- اضافه کردن Refresh Token واقعی.
- مدیریت خطاهای API و پیام‌های مناسب برای کاربر.

 Creazione e collegamento del Virtualenv in PyCharm
Perché:

Isolare le librerie del progetto dal sistema operativo

Permettere a PyCharm di usare sempre l’ambiente giusto per il microservizio

Passi eseguiti:

Creazione del virtualenv nella cartella del progetto

bash
Copia
Modifica
cd ~/authService4Ever
python3 -m venv .venv
Questo crea la cartella .venv con l’interprete Python dedicato al progetto.

Apertura del progetto in PyCharm

File → Open... → selezionare authService4Ever

Collegamento del venv in PyCharm

File → Settings (o Preferences su Mac) → Project: authService4Ever → Python Interpreter

Cliccare l’icona dell’ingranaggio ⚙ → Add...

Scegliere Existing Environment

Selezionare:

swift
Copia
Modifica
/Users/javidshams/authService4Ever/.venv/bin/python
Confermare con OK

Verifica

In basso a destra in PyCharm appare:

scss
Copia
Modifica
Python 3.x (.venv)
Nel terminale integrato appare il prompt:

scss
Copia
Modifica
(.venv) javidshams@MAC-3659BB authService4Ever %

