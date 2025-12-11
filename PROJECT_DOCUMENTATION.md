# Image Electronics — EcomApp

Comprehensive project documentation for the Django-based e-commerce application in this repository.

---

## Quick Summary

- Framework: Django 5.2
- Language: Python 3.11
- Web server: Gunicorn
- Static: WhiteNoise (optionally Cloudinary)
- Database: PostgreSQL (Railway production), sqlite for local development
- Hosting: Railway (project: `profound-surprise`, service: `web`)
- Custom domain: `www.imageelectronics.org` (TLS via Let's Encrypt)

---

## Repository Structure (high level)

- `manage.py` — Django management wrapper
- `my_ecommerce_site/` — Django project settings, middleware, WSGI/ASGI
- `store/` — main app (models, views, templates, static, migrations)
- `services/` — services app (service requests, attachments)
- `static/` and `staticfiles/` — static assets and collected static
- `media/` — local media uploads (Cloudinary used in production)
- `requirements.txt` — Python dependencies
- `Procfile`, `runtime.txt` — deployment helpers
- `create_ppt.py` — script that generates `EcomApp_Project_Documentation.pptx`
- `PROJECT_DOCUMENTATION.md` — (this file)

Files of particular interest (examples):
- `store/views.py` — checkout processing, portal views, TomTom shipping estimate
- `store/models.py` — customer and order-related models and fields
- `store/templates/store/orders_list.html` and `order_detail.html` — staff portal UI
- `store/migrations/0014*` and `0015*` — migrations that add phone and shipping fields

---

## Features Overview

- Checkout flows with:
  - Phone persistence to `Customer` and `ShippingAddress` models
  - Shipping options: pickup vs delivery
  - Shipping speed: standard / express
  - TomTom-based distance estimate endpoint for shipping fees
- Staff portal improvements:
  - Orders list reordering and colored status badges
  - Display of `fulfillment`, `shipping_speed`, and `shipping_fee`
- Analytics:
  - Pageview tracking with session enforcement
  - Traffic Trends dataset (unique sessions)

---

## Local Setup (development)

1. Create a virtual environment and activate it:

```bash
python -m venv env
source env/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables (create `.env` or use `export`):
- `SECRET_KEY` — Django secret key
- `DEBUG=true` for local development
- Optional: `DATABASE_URL` to use Postgres locally

4. Run migrations and start server:

```bash
python manage.py migrate
python manage.py runserver
```

5. Visit `http://localhost:8000/`.

---

## Production / Deployment Notes

- Railway is used for hosting:
  - Service name: `web`
  - Environment variables are set via Railway `variables`.
  - Use `railway redeploy --service web --yes` to trigger a redeploy after env changes.
- Ensure these env vars are set in Railway (non-exhaustive):
  - `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `USE_CLOUDINARY`, `CLOUDINARY_URL` or respective keys.
- Static files: built and collected to `staticfiles` (WhiteNoise). Optionally use Cloudinary for media.

---

## Critical Production Issues & Fixes (history)

- DisallowedHost (HTTP 400) errors occurred after adding `www.imageelectronics.org` as a Railway custom domain.
  - Fix: add `www.imageelectronics.org` and `imageelectronics.org` to `ALLOWED_HOSTS` (via env or `settings.py`).
- CSRF 403 on login due to missing origin trust for the custom domain.
  - Fix: include `https://www.imageelectronics.org` and `https://imageelectronics.org` in `CSRF_TRUSTED_ORIGINS`.
- Database schema drift (ProgrammingError 500s) because new fields were deployed before migrations ran.
  - Approach used: applied migrations in production (secure temporary endpoint used once), then removed defensive fallbacks and cleaned code.

---

## Environment Variables (important keys)

- `SECRET_KEY` — Django secret key (required)
- `DEBUG` — `false` in production
- `DATABASE_URL` — production Postgres DB
- `ALLOWED_HOSTS` — comma-separated hosts (include `www.imageelectronics.org`)
- `CSRF_TRUSTED_ORIGINS` — comma-separated origins for CSRF
- `USE_CLOUDINARY`, `CLOUDINARY_URL` / `CLOUDINARY_*` — cloudinary config
- `TOMTOM_API_KEY` — API key for TomTom distance/route calls
- `BREVO_API_KEY` or SMTP credentials for email sending

Note: Do NOT commit secrets to the repository. Use Railway env vars or `.env` local files.

---

## Database & Migrations

- Migrations live under `store/migrations/` and `services/migrations/`.
- Important migrations:
  - `0014_add_phone_fields.py` — adds `Customer.phone` and `ShippingAddress.phone`
  - `0015_order_fulfillment_and_speed.py` — adds `Order.shipping_fee`, `Order.fulfillment`, `Order.shipping_speed`
- Best practice: run `python manage.py makemigrations` locally, test, commit, push, then run `python manage.py migrate` in production via the platform's one-off/run options.

---

## Domain & DNS Guidance

- `www.imageelectronics.org` — configured as a CNAME to Railway's required target (set in Namecheap).
- `imageelectronics.org` (apex) — Namecheap does not allow direct CNAME for the apex; either:
  - Use Namecheap URL Redirect (HTTP redirect) from the apex to `https://www.imageelectronics.org`, or
  - Use an ALIAS/ANAME record if your DNS provider supports it.
- After DNS propagation, Railway will issue a Let's Encrypt certificate for the custom domain.

---

## Troubleshooting Checklist

- If you see `DisallowedHost` / HTTP 400: confirm `ALLOWED_HOSTS` includes the Host header value (add via Railway env).
- If you see `Forbidden (Origin checking failed)` / CSRF 403 on POST forms: add the site origin (`https://www.imageelectronics.org`) to `CSRF_TRUSTED_ORIGINS`.
- If static assets 404: ensure `collectstatic` has run and `STATIC_ROOT` is correctly set for production; verify WhiteNoise settings.
- If migrations cause errors: inspect production DB schema and apply migrations carefully; avoid adding incompatible code that expects new columns before migrations run.

---

## How to Push Changes (notes about current local state)

- Remote `origin` is `https://github.com/tokyoCitagh/CapstoneProject_group4.git`.
- If `git push` fails with HTTP 403, use one of the following:
  - Authenticate with `gh auth login --web` then `gh auth setup-git`.
  - Use SSH: create an SSH key and add it to the target GitHub account, then `git remote set-url origin git@github.com:tokyoCitagh/CapstoneProject_group4.git`.

---

## Next Recommended Improvements

- Harden production cookies:
  - `SESSION_COOKIE_SECURE = True`
  - `CSRF_COOKIE_SECURE = True`
  - `SECURE_SSL_REDIRECT = True` (if sole TLS termination at Railway)
- Move ship-fee calculation entirely server-side to prevent client tampering.
- Add end-to-end tests for checkout and portal staff flows.
- Add monitoring and alerts for deployment health and 5xx rates.

---

## Contacts & Ownership

- Repository: `CapstoneProject_group4` (owner: `tokyoCitagh`)
- Railway project: `profound-surprise` (production environment used for deployment)
- For production secrets and config: use Railway project variables and Cloudinary dashboard.

---

## Where to find more

- Code: `store/`, `services/`, `my_ecommerce_site/`
- Templates: `templates/` and `store/templates/`.
- Static: `static/` and `staticfiles/`.
- PPT summary: `EcomApp_Project_Documentation.pptx` (generated by `create_ppt.py`).


*Generated by the dev session assistant on 2025-12-02.*
