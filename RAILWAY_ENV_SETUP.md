# Railway Environment Variables Setup

## Required Environment Variables for Production

Add these environment variables in your Railway project settings:

### 1. Django Core
```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.railway.app,your-custom-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.railway.app,https://your-custom-domain.com
```

### 2. Database
Railway automatically provides:
```
DATABASE_URL=postgresql://...
```

### 3. Email Configuration (Brevo API)
```
BREVO_API_KEY=xkeysib-your-api-key-here
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
EMAIL_BACKEND=store.brevo_backend.BrevoAPIBackend
```

### 4. Cloudinary (Media Storage)
```
USE_CLOUDINARY=true
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### 5. **Paystack Payment Gateway** (IMPORTANT!)
```
PAYSTACK_PUBLIC_KEY=pk_test_2256ce683d518f8dd2e113f43f6470c61fe70a7c
PAYSTACK_SECRET_KEY=sk_test_981e3a7c43aaa455c65c8f80c6fff8a0af8860b4
```

**For Production (Live Payments):**
```
PAYSTACK_PUBLIC_KEY=pk_live_your_live_public_key
PAYSTACK_SECRET_KEY=sk_live_your_live_secret_key
```

### 6. Redis (Optional - for Celery background tasks)
```
REDIS_URL=redis://default:password@host:port/0
```

## How to Add Variables to Railway:

1. Go to your Railway project dashboard
2. Click on your service (web)
3. Go to "Variables" tab
4. Click "New Variable"
5. Add each variable name and value
6. Click "Deploy" to restart with new variables

## Security Notes:

⚠️ **NEVER commit these values to Git!**
- The `.env` file is in `.gitignore`
- Use `.env.sample` as a template
- All sensitive keys should ONLY exist in:
  - Local `.env` file (for development)
  - Railway environment variables (for production)

## Verifying Setup:

After adding variables:
1. Check Railway logs for any missing environment variable errors
2. Visit your site and test:
   - Email sending (password reset, etc.)
   - Image uploads (should go to Cloudinary)
   - Payment checkout (Paystack modal should appear)
3. Monitor for any 500 errors in Railway logs

## Getting Your Keys:

- **Paystack**: https://dashboard.paystack.com/#/settings/developers
- **Brevo**: https://app.brevo.com/settings/keys/api
- **Cloudinary**: https://console.cloudinary.com/settings
