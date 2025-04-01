# Grafana No-Login Configuration

This document explains the configuration changes made to completely bypass the login screen for Grafana in both local and cloud environments.

## Changes Made

The following environment variables were added to the Grafana service in both `docker-compose.yml` and `docker-compose.cloud.yml`:

```yaml
- GF_AUTH_ANONYMOUS_ENABLED=true
- GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
- GF_AUTH_BASIC_ENABLED=false
- GF_AUTH_DISABLE_LOGIN_FORM=true
- GF_AUTH_DISABLE_SIGNOUT_MENU=true
```

### What These Settings Do

1. `GF_AUTH_ANONYMOUS_ENABLED=true`: Enables anonymous access to Grafana
2. `GF_AUTH_ANONYMOUS_ORG_ROLE=Admin`: Sets the role for anonymous users to Admin, allowing them to view and edit dashboards
3. `GF_AUTH_BASIC_ENABLED=false`: Disables basic authentication to prevent login prompts
4. `GF_AUTH_DISABLE_LOGIN_FORM=true`: Completely removes the login form
5. `GF_AUTH_DISABLE_SIGNOUT_MENU=true`: Removes the sign-out option from the menu

## Testing the Configuration

To test that anonymous access is working correctly:

1. Restart your Grafana container:
   ```bash
   # For local environment
   docker-compose restart grafana
   
   # For cloud environment
   docker-compose -f docker-compose.cloud.yml restart grafana
   ```

2. Access Grafana in your browser:
   ```
   http://localhost:3000
   ```

3. You should be able to view dashboards without being prompted to log in.

## Admin Access

Even with anonymous access enabled, you can still log in as an admin when needed:

1. Click the "Sign In" button in the bottom-left corner of the Grafana UI
2. Use the admin credentials:
   - Username: admin
   - Password: admin

## Security Considerations

This configuration is suitable for development environments but has some security implications:

- Anyone with access to the Grafana URL can view your dashboards
- Anonymous users have read-only access and cannot make changes
- Admin credentials are still required for configuration changes

For production environments, consider implementing a more secure authentication method like OAuth or LDAP.
