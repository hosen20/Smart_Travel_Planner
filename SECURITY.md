# Security Best Practices

## Authentication & Secrets Management

### Current Implementation
- **JWT Tokens**: User authentication is managed via JWT tokens with configurable expiration
- **Password Hashing**: Passwords are hashed using bcrypt (72-byte limit)
- **Secret Key**: Automatically generated if not provided in `.env` file

### For Production Deployment

#### 1. Secret Key Management
- **DO NOT** store `SECRET_KEY` in `.env` file for production
- Generate a secure secret key using:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- Store the key in a secure secrets manager:
  - AWS Secrets Manager
  - Azure Key Vault
  - HashiCorp Vault
  - Environment variables (managed by deployment platform)

#### 2. Database Credentials
- Store `DATABASE_URL` in a secrets manager, not in `.env`
- Use strong, randomly generated passwords for database users
- Enable SSL/TLS for database connections

#### 3. API Keys
- Store all API keys (`GROQ_API_KEY`, `WEBHOOK_URL`) in secrets manager
- Rotate API keys regularly
- Use least-privilege access for API accounts

#### 4. Token Expiration
- Current default: 30 minutes
- Adjust `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env` based on your security requirements
- Consider implementing refresh tokens for longer sessions

#### 5. CORS Configuration
- Currently allows: `http://localhost:3000`
- For production, update to your frontend domain only in `app/main.py`:
  ```python
  allow_origins=["https://yourdomain.com"]
  ```

#### 6. Database Schema
User authentication data is stored in the `users` table:
- Passwords are hashed using bcrypt
- Each user has a unique email
- `is_active` flag can be used to deactivate accounts
- `is_superuser` flag for admin users

#### 7. User Registration & Login
- **Registration**: Creates a new user with hashed password
- **Login**: Validates credentials and returns JWT token
- **Token Verification**: Validates JWT signature and expiration
- **Password Requirements** (recommended):
  - Minimum 8 characters
  - Mix of uppercase, lowercase, numbers, and symbols
  - Consider implementing password strength meter

#### 8. Migration from Env Secrets to Production Secret Manager

**Step 1: Set up your secrets manager (example: AWS Secrets Manager)**

**Step 2: Update `settings.py` to load from secrets manager:**
```python
import boto3

def get_secret(secret_name, region_name="us-east-1"):
    client = boto3.client('secretsmanager', region_name=region_name)
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

# In Settings class:
secret_key: str = Field(default_factory=lambda: get_secret('travel-planner/secret-key'))
```

**Step 3: Deploy with environment-specific configuration**

### Recommended Enhancements

1. **Rate Limiting**: Add rate limiting to prevent brute force attacks
   ```bash
   pip install slowapi
   ```

2. **HTTPS Enforcement**: Ensure all connections use HTTPS in production

3. **Audit Logging**: Log authentication events for security monitoring

4. **Two-Factor Authentication**: Consider implementing 2FA for sensitive operations

5. **Password Reset Flow**: Implement secure password reset mechanism

6. **Session Management**: Implement session tracking and revocation

7. **Input Validation**: Sanitize all user inputs

8. **SQL Injection Prevention**: Use parameterized queries (already done with SQLAlchemy)

9. **CSRF Protection**: Add CSRF tokens for state-changing operations

10. **Security Headers**: Add security headers to HTTP responses
    ```python
    from fastapi.middleware import Middleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])
    ```

### Testing Authentication

```bash
# Register a new user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "securepassword123"}'

# Login and get token
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=securepassword123"

# Verify token
curl -X GET "http://localhost:8000/api/auth/verify" \
  -H "Authorization: Bearer <your_token_here>"
```

## Regular Security Tasks

- [ ] Update dependencies regularly
- [ ] Rotate API keys quarterly
- [ ] Review access logs for suspicious activity
- [ ] Run security audits
- [ ] Keep database backups secure
- [ ] Test disaster recovery procedures
