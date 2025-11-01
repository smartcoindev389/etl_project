# Cloud MySQL Setup Guide

This guide helps you set up a free or low-cost MySQL database in the cloud.

## Free Tier Options

### 1. **Railway** (Recommended - Easy Setup)
- **Free Tier**: $5 credit/month
- **URL**: https://railway.app
- **Steps**:
  1. Sign up at railway.app
  2. Create new project
  3. Add MySQL service
  4. Get connection credentials
  5. Update `.env` with credentials

### 2. **PlanetScale** (Free Tier Available)
- **Free Tier**: 1 database, 1GB storage
- **URL**: https://planetscale.com
- **Steps**:
  1. Sign up at planetscale.com
  2. Create database
  3. Get connection string
  4. Note: Uses different connection format, update config if needed

### 3. **Aiven** (Free Trial)
- **Free Trial**: 14 days, then pay-as-you-go
- **URL**: https://aiven.io
- **Steps**:
  1. Sign up at aiven.io
  2. Create MySQL service
  3. Get connection details
  4. Update `.env` with credentials

### 4. **AWS RDS** (Free Tier for 12 months)
- **Free Tier**: t2.micro instance
- **URL**: https://aws.amazon.com/rds/
- **Steps**:
  1. Create AWS account
  2. Navigate to RDS console
  3. Create MySQL instance (free tier)
  4. Configure security groups
  5. Get endpoint and credentials

## Setting Up Railway (Easiest)

### Step 1: Create Account
1. Go to https://railway.app
2. Sign up with GitHub or email

### Step 2: Create Project
1. Click "New Project"
2. Select "Deploy from GitHub repo" or "Empty Project"

### Step 3: Add MySQL
1. Click "+ New" → "Database" → "MySQL"
2. Railway will create a MySQL instance
3. Wait for deployment (1-2 minutes)

### Step 4: Get Credentials
1. Click on the MySQL service
2. Go to "Variables" tab
3. You'll see:
   - `MYSQLHOST`
   - `MYSQLPORT`
   - `MYSQLUSER`
   - `MYSQLPASSWORD`
   - `MYSQLDATABASE`

### Step 5: Update .env File

Update your `.env` file:

```env
CLOUD_DB_HOST=<MYSQLHOST value>
CLOUD_DB_PORT=<MYSQLPORT value>
CLOUD_DB_USER=<MYSQLUSER value>
CLOUD_DB_PASSWORD=<MYSQLPASSWORD value>
CLOUD_DB_NAME=<MYSQLDATABASE value>
```

### Step 6: Test Connection

```bash
python test_mysql_connection.py --cloud
```

### Step 7: Initialize Database

```bash
python database/init_database.py --cloud
```

## Cost Considerations

| Provider | Free Tier | Paid Tier (Small) |
|----------|-----------|-------------------|
| Railway  | $5/month credit | ~$5-10/month |
| PlanetScale | 1 DB, 1GB | ~$29/month |
| Aiven    | 14 days trial | ~$15-30/month |
| AWS RDS  | 12 months free | ~$15-30/month |

**Recommendation**: Start with Railway for simplicity, migrate if needed.

## Security Best Practices

1. **Use Environment Variables**: Never hardcode credentials
2. **Use .env File**: Keep it in `.gitignore`
3. **Limit Access**: Use firewall rules if available
4. **Regular Backups**: Set up automated backups
5. **Strong Passwords**: Use complex passwords

## Troubleshooting

### Connection Timeout
- Check firewall rules
- Verify IP whitelist (if required)
- Check if database is public or private

### Authentication Failed
- Verify username and password
- Check if user has proper permissions
- Ensure database name is correct

### SSL Issues
- Some providers require SSL
- Update connection string to include SSL parameters
- Check provider documentation

## Example .env Configuration

```env
# Cloud MySQL (Railway example)
CLOUD_DB_HOST=containers-us-west-xxx.railway.app
CLOUD_DB_PORT=3306
CLOUD_DB_USER=root
CLOUD_DB_PASSWORD=your_password_here
CLOUD_DB_NAME=railway

# Or AWS RDS example
CLOUD_DB_HOST=your-db.xxxxxxxxx.us-east-1.rds.amazonaws.com
CLOUD_DB_PORT=3306
CLOUD_DB_USER=admin
CLOUD_DB_PASSWORD=your_password_here
CLOUD_DB_NAME=etl_project
```

## Next Steps

1. ✅ Choose a cloud provider
2. ✅ Create database instance
3. ✅ Update `.env` file
4. ✅ Test connection
5. ✅ Initialize database schema
6. ✅ Start loading data

