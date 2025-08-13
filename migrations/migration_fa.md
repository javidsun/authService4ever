پیاده‌سازی کنیم مخصوص پروژه‌ی Auth تو.
کافیست این متن را در یک فایل مثل docs/alembic_migrations_guide.md ذخیره کنی.

راهنمای کامل مهاجرت‌های دیتابیس با Alembic (پروژه Auth)
این سند مرحله‌به‌مرحله توضیح می‌دهد چگونه:

Alembic را راه‌اندازی کنیم

مهاجرت (Migration) خودکار/دستی بسازیم

با دیتابیس Docker‌شده (Postgres) کار کنیم

مشکلات رایج را رفع کنیم

بهترین الگوها را رعایت کنیم

1) پیش‌نیازها
Docker Desktop در حال اجرا باشد و کانتینر Postgres بالا باشد:

```bash
    docker compose up -d db
    docker compose ps  

```
# پورت: 5432→5432 یا 5433→5432

در ریشه‌ی پروژه فایل‌های زیر موجود باشد:

alembic.ini

پوشه‌ی migrations/ (با env.py و versions/)

ماژول‌های پروژه (مثلاً app/models.py, app/db_base.py)

URL دیتابیس در دو جا یکسان باشد:

.env → DB_URL=postgresql+psycopg2://auth:authpass@localhost:5432/auth_db

alembic.ini → sqlalchemy.url = postgresql+psycopg2://auth:authpass@localhost:5432/auth_db

اگر در docker-compose.yml پورت را 5433:5432 گذاشته‌ای، هر دو را به localhost:5433 تغییر بده.

2) مفاهیم پایه‌ای Alembic
Migration: فایل Python که تغییرات اسکیمای دیتابیس را (CREATE/ALTER/…) تعریف می‌کند.

Revision: هر مهاجرت یک شناسه (ID) یکتا دارد. زنجیره‌ی Revisionها تاریخچه‌ی تغییرات را می‌سازد.

Upgrade/Downgrade: حرکت به جلو/عقب بین نسخه‌های اسکیمای دیتابیس.

Autogenerate: Alembic با نگاه به target_metadata (متادیتای SQLAlchemy) تغییرات را حدس می‌زند و فایل migration تولید می‌کند.

3) پیکربندی env.py و alembic.ini
3.1 migrations/env.py
مطمئن شو مدل‌ها و Base بارگذاری می‌شوند و target_metadata درست تنظیم شده:

```python
    # migrations/env.py (بخش‌های کلیدی)
import os, sys
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from app.db_base import Base
from app import models              # مهم: مدل‌ها را ایمپورت کن تا شناخته شوند
target_metadata = Base.metadata

```
3.2 alembic.ini


```ini
[alembic]
script_location = migrations
sqlalchemy.url = postgresql+psycopg2://auth:authpass@localhost:5432/auth_db
```

4) سناریوهای اولیه (Baseline)
حالت A) اسکیمای قبلی دستی ساخته شده (بدون Alembic)
اگر قبلاً جدول‌ها را دستی ساختی (مثلاً users) و هنوز Alembic روی DB چیزی ثبت نکرده:

ساخت یک Revision خالی (تنها برای ایجاد رکورد baseline):

```bash
    alembic revision -m "baseline existing schema"
```
مارک کردن دیتابیس به عنوان هم‌تراز با آخرین نسخه (بدون اجرای SQL):

```bash
    alembic stamp head
```

خروجی مثل “Running stamp_revision -> <rev_id>” نشانه موفقیت است.

حالت B) پروژه تازه (همه چیز با Alembic)
مستقیماً برو سراغ ایجاد اولین مهاجرت خودکار (بخش 5

5) مهاجرت خودکار (Autogenerate)
وقتی مدل‌ها را تغییر می‌دهی (مثلاً افزودن is_active به users یا ایجاد جدول‌های refresh_tokens/email_verifications/password_resets):

تولید فایل مهاجرت:

```bash
    alembic revision --autogenerate -m "auth: add is_active + refresh/email_verify/password_resets"
```

بازبینی فایل ایجاد شده در migrations/versions/…:

آیا create_table‌های مورد نظر هست؟

آیا add_column یا alter_column درست است؟

ایندکس/یونیک/فارن‌کی‌ها درستند؟

اعمال مهاجرت:

```bash
    alembic upgrade head
```
بررسی در دیتابیس:

```bash
    docker compose exec -it db psql -U auth -d auth_db -c "\dt"
    docker compose exec -it db psql -U auth -d auth_db -c "\d users"

```

مهاجرت دستی (وقتی Autogenerate کافی نیست)
گاهی لازم است فایل مهاجرت را خودت بنویسی (Data Migration، constraint خاص، …).
نمونه‌ی ساخت فایل:

```bash
    # یک فایل جدید داخل migrations/versions بساز
    touch migrations/versions/20250813_auth_full_schema.py

```

محتوای نمونه (ایده‌ال برای شرایطی که بخشی از اسکیمای قدیمی وجود دارد):

```python
"""auth: full schema"""

from alembic import op
import sqlalchemy as sa

revision = "20250813_auth_full"
down_revision = "REV_ID_قبلی_تو"  # با آخرین revision قبلی جایگزین کن
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # اگر users هست و ستون is_active ندارد، اضافه کن
    if insp.has_table("users"):
        cols = {c["name"] for c in insp.get_columns("users")}
        if "is_active" not in cols:
            op.add_column("users", sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False))
            op.alter_column("users", "is_active", server_default=None)

    # refresh_tokens
    if not insp.has_table("refresh_tokens"):
        op.create_table(
            "refresh_tokens",
            sa.Column("jti", sa.String(), primary_key=True),
            sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("revoked", sa.Boolean(), server_default=sa.false(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.create_unique_constraint("uq_refresh_jti", "refresh_tokens", ["jti"])
        op.create_index("ix_refresh_user_revoked", "refresh_tokens", ["user_id", "revoked"])

    # email_verifications
    if not insp.has_table("email_verifications"):
        op.create_table(
            "email_verifications",
            sa.Column("token", sa.String(), primary_key=True),
            sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("consumed", sa.Boolean(), server_default=sa.false(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )

    # password_resets
    if not insp.has_table("password_resets"):
        op.create_table(
            "password_resets",
            sa.Column("token", sa.String(), primary_key=True),
            sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("consumed", sa.Boolean(), server_default=sa.false(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )

def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if insp.has_table("password_resets"):
        op.drop_table("password_resets")
    if insp.has_table("email_verifications"):
        op.drop_table("email_verifications")
    if insp.has_table("refresh_tokens"):
        try:
            op.drop_index("ix_refresh_user_revoked", table_name="refresh_tokens")
        except Exception:
            pass
        try:
            op.drop_constraint("uq_refresh_jti", "refresh_tokens", type_="unique")
        except Exception:
            pass
        op.drop_table("refresh_tokens")
    if insp.has_table("users"):
        cols = {c["name"] for c in insp.get_columns("users")}
        if "is_active" in cols:
            op.drop_column("users", "is_active")
```

نکته: down_revision باید ID آخرین مهاجرتی باشد که در پروژه‌ات وجود دارد. آن را از alembic history یا نام فایل قبلی داخل versions/ بردار.

 دستورات روزمره
مشاهده تاریخچه:
```bash
      alembic history

```

دیدن نسخه‌ی جاری DB:

```bash
    alembic current
```
ساخت مهاجرت جدید (خودکار):

```bash
    alembic revision --autogenerate -m "message"

```
اعمال تا آخرین نسخه:

```bash
    alembic upgrade head
```
یک نسخه برگشت:

```bash
    alembic downgrade -1

```

برچسب‌گذاری بدون اجرای SQL (baseline):
```bash
    alembic stamp head
```

8) خطاهای رایج و رفع آن‌ها
8.1 connection refused به Postgres
کانتینر DB روشن نیست → docker compose up -d db

پورت اشتباه است → docker compose ps را چک کن و alembic.ini/.env را اصلاح کن.

تست اتصال:

```bash
    PGPASSWORD=authpass psql -h localhost -p 5432 -U auth -d auth_db -c "SELECT 1;"
```
8.2 No 'script_location' key found
alembic.ini باید کنار پروژه باشد و شامل script_location = migrations باشد.

دستور را از ریشه‌ی همان پروژه اجرا کن.

8.3 No changes detected در Autogenerate
در env.py باید:

```python
from app.db_base import Base
from app import models
target_metadata = Base.metadata
```

باشد تا Alembic مدل‌ها را ببیند.

8.4 چند سرشاخه (Multiple heads)
وقتی چند شاخه‌ی migration درست شود:

```bash
    alembic heads
  alembic merge -m "merge heads" <head1> <head2>
  alembic upgrade head

```

8.5 تناقض بین DB و مدل‌ها
اگر قبلاً به صورت دستی جداول ساختی، اول baseline کن (alembic stamp head) سپس تغییرات جدید را به صورت migration بساز.

9) بهترین الگوها (Best Practices)
همیشه بعد از تغییر مدل‌ها یک migration بساز و بازبینی کن.

روی dev/staging اجرا و بررسی کن، بعد روی prod.

Migrationهای دستی را برای Data Migration و تغییرات پیچیده استفاده کن.

down_revision را درست نگه دار (زنجیره باید خطی یا merge شده باشد).

اگر ستون boolean داری، در بیان شرط‌ها در SQLAlchemy 2.x از .is_(True/False) استفاده کن (نه == False).

10) جریان کاری پیشنهادی (Flow)

```mermaid
    flowchart LR
    A[تغییر در مدل‌های SQLAlchemy] --> B[alembic revision --autogenerate]
    B --> C[بازبینی و اصلاح فایل migration]
    C --> D[alembic upgrade head]
    D --> E[بررسی جداول با psql \dt / \d]
    E --> F[اجرای سرویس و تست API]
```

11) نکات مرتبط با Docker
App روی Host و DB داخل Docker: همیشه localhost:<HOST_PORT> را در URL بگذار (نه نام سرویس).

اگر سرویس Auth را هم کانتینری کردی (داخل همان compose)، آن‌وقت URL سرویس به سرویس: postgresql://auth:authpass@db:5432/auth_db.

12) چک‌لیست سریع
 docker compose ps → DB Up

 پورت صحیح در alembic.ini و .env

 env.py → target_metadata = Base.metadata + import models

 alembic stamp head (اگر لازم بود baseline)

 alembic revision --autogenerate -m "..."

 بازبینی فایل migration

 alembic upgrade head

 بررسی با \dt و \d users







