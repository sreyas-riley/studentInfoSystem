# Vercel Deployment Guide

## Prerequisites
1. Install Vercel CLI: `npm i -g vercel`
2. Make sure you have a Vercel account (sign up at https://vercel.com)

## Deployment Steps

### 1. Navigate to your project directory
```bash
cd student_info_app
```

### 2. Login to Vercel (if not already logged in)
```bash
vercel login
```

### 3. Deploy your application
```bash
vercel
```

### 4. Follow the prompts:
- Set up and deploy? → Yes
- Which scope? → Select your account
- Link to existing project? → No
- What's your project's name? → student-info-app (or your preferred name)
- In which directory is your code located? → ./ (current directory)
- Want to override the settings? → No

### 5. Environment Variables
After deployment, you'll need to set up environment variables in the Vercel dashboard:
1. Go to your project dashboard on Vercel
2. Navigate to Settings → Environment Variables
3. Add the following variables from your `.env` file:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - Any other environment variables your app needs

### 6. Redeploy after setting environment variables
```bash
vercel --prod
```

## Important Notes

1. **Database**: Your app uses Supabase, so make sure your Supabase project is properly configured and accessible from Vercel's servers.

2. **File Storage**: Since Vercel is serverless, any file uploads or temporary storage will need to be handled through Supabase storage or another cloud service.

3. **Sessions**: Flask sessions may not work as expected on Vercel due to serverless architecture. Consider using JWT tokens or database-based sessions.

4. **Dependencies**: All required packages are listed in `requirements-vercel.txt` and will be installed automatically.

5. **Lightweight Version**: This deployment uses `app-vercel.py` which is a lightweight version without OpenCV dependencies to stay within Vercel's 250MB function size limit.

## Size Optimization

The deployment uses a lightweight version of the application (`app-vercel.py`) that:
- Removes OpenCV dependencies (saves ~200MB)
- Uses simplified image verification (demo mode)
- Maintains all core functionality
- Stays well under Vercel's 250MB limit

### Full Version vs Lightweight Version

| Feature | Full Version (app.py) | Lightweight Version (app-vercel.py) |
|---------|----------------------|-------------------------------------|
| AI Face Recognition | ✅ Full OpenCV | ❌ Demo mode only |
| Image Processing | ✅ Advanced | ❌ Basic validation |
| File Size | ~250MB+ | ~50MB |
| Deployment | ❌ Too large for Vercel | ✅ Compatible |
| Core Features | ✅ All features | ✅ All features |

## Troubleshooting

- If you encounter issues with OpenCV or other heavy dependencies, consider using lighter alternatives or moving those features to a separate service.
- Check the Vercel function logs in the dashboard for any deployment errors.
- Make sure all environment variables are properly set in the Vercel dashboard.

## Custom Domain (Optional)
After deployment, you can add a custom domain in the Vercel dashboard under Settings → Domains.

## Upgrading to Full Version

If you need the full AI features, consider:
1. Using a different hosting platform (Heroku, Railway, DigitalOcean)
2. Splitting the application into microservices
3. Using external AI services (AWS Rekognition, Google Vision API)
4. Implementing the AI features as separate serverless functions
