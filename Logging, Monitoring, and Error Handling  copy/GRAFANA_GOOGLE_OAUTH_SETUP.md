# Setting Up Google OAuth for Grafana

This document explains how to set up Google OAuth for Grafana to enable automatic login without showing the login screen.

## Step 1: Create OAuth Credentials in Google Cloud Console

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" and select "OAuth client ID"
5. Select "Web application" as the application type
6. Set a name for your OAuth client (e.g., "Grafana OAuth")
7. Add the following authorized redirect URIs:
   - `http://localhost:3000/login/google`
   - `http://your-grafana-domain.com/login/google` (if you have a custom domain)
8. Click "Create"
9. Note down the Client ID and Client Secret

## Step 2: Update Docker Compose Configuration

Add the following environment variables to the Grafana service in your docker-compose.yml file:

```yaml
- GF_AUTH_GOOGLE_ENABLED=true
- GF_AUTH_GOOGLE_CLIENT_ID=your-client-id
- GF_AUTH_GOOGLE_CLIENT_SECRET=your-client-secret
- GF_AUTH_GOOGLE_SCOPES=openid email profile
- GF_AUTH_GOOGLE_AUTH_URL=https://accounts.google.com/o/oauth2/auth
- GF_AUTH_GOOGLE_TOKEN_URL=https://accounts.google.com/o/oauth2/token
- GF_AUTH_GOOGLE_ALLOWED_DOMAINS=your-domain.com
- GF_AUTH_GOOGLE_ALLOW_SIGN_UP=true
- GF_AUTH_OAUTH_AUTO_LOGIN=true
- GF_AUTH_DISABLE_LOGIN_FORM=true
- GF_AUTH_DISABLE_SIGNOUT_MENU=true
```

Replace:
- `your-client-id` with the Client ID from Google Cloud Console
- `your-client-secret` with the Client Secret from Google Cloud Console
- `your-domain.com` with your domain (optional, remove this line to allow any domain)

## Step 3: Restart Grafana

Restart the Grafana container to apply the changes:

```bash
docker-compose restart grafana
```

## Step 4: Test the Configuration

1. Open Grafana in your browser: http://localhost:3000
2. You should be automatically redirected to Google's login page
3. After logging in with your Google account, you should be automatically redirected back to Grafana without seeing the Grafana login screen

## Troubleshooting

If you encounter any issues:

1. Check the Grafana logs:
   ```bash
   docker-compose logs grafana
   ```

2. Verify that your OAuth client is configured correctly in Google Cloud Console
3. Ensure that the redirect URI matches exactly what's configured in Google Cloud Console
4. Check that your Google account email matches the allowed domains (if configured)

## Security Considerations

This configuration:
- Automatically logs users in via Google OAuth
- Disables the Grafana login form
- Hides the sign-out menu

For production environments, consider:
- Restricting access to specific Google domains or users
- Implementing proper role-based access control in Grafana
- Using HTTPS for all communications
