# PYTHONANYWHERE DEPLOYMENT GUIDE

## Step-by-Step Instructions:

### 1. Go to PythonAnywhere Dashboard
- Login to https://www.pythonanywhere.com/
- Go to **"Web"** tab (left sidebar)

### 2. Create a New Web App
1. Click **"Add a new web app"**
2. Click **"Next"** (Manual Configuration)
3. Select **"Python 3.12"** (or latest 3.x)
4. Click **"Next"**
5. Web app name will be auto-generated (e.g., `yourusername.pythonanywhere.com`)
6. Click **"Create web app"**

### 3. Pull Your Code from GitHub
1. Go to **"Consoles"** tab → **"Bash"**
2. In the bash console, run:
```bash
# Go to your web app directory
cd ~/sites/your-web-app-name

# Clone your repository (replace with your repo URL)
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git sportstore

# Or if you already cloned somewhere else:
# cd ~/sites/your-web-app-name
# git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### 4. Install Dependencies
In the same Bash console:
```bash
cd ~/sites/your-web-app-name/sportstore

# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Django and dependencies
pip install django
pip install Pillow
```

### 5. Configure WSGI File
1. Go to **"Web"** tab
2. Scroll down to **"WSGI configuration file"**
3. Click the link to edit the file
4. Replace the content with:

```python
import os
import sys

# Add the app directory to the Python path
path = '/home/YOUR_USERNAME/sites/YOUR_WEB_APP_NAME/sportstore'
if path not in sys.path:
    sys.path.insert(0, path)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'sportstore.settings'

# Import Django
import django
django.setup()

# Import WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

6. **Save** the file

### 6. Configure Static Files
1. Still in **"Web"** tab
2. Scroll to **"Static files"** section
3. Click **"Enter URL"**: `/static/`
4. Click **"Enter directory"**: `/home/YOUR_USERNAME/sites/YOUR_WEB_APP_NAME/sportstore/static`
5. Click **"Add"** (or "Map" button)
6. Also add media files (if you have user uploads):
   - URL: `/media/`
   - Directory: `/home/YOUR_USERNAME/sites/YOUR_WEB_APP_NAME/sportstore/media`

### 7. Collect Static Files
In the Bash console:
```bash
cd ~/sites/your-web-app-name/sportstore
source venv/bin/activate

# Collect all static files
python manage.py collectstatic --noinput
```

### 8. Run Migrations (Important!)
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate
```

### 9. Create Superuser (for Admin Access)
```bash
python manage.py createsuperuser
```

### 10. Reload Web App
1. Go to **"Web"** tab
2. Scroll up to the top
3. Click **"Reload"** button next to your web app
4. Wait for it to finish (green checkmark)

### 11. Access Your Site!
- Your site will be at: `http://yourusername.pythonanywhere.com/`
- Admin panel: `http://yourusername.pythonanywhere.com/admin/`

---

## Troubleshooting:

### Issue: "ModuleNotFoundError: No module named 'django'"
**Solution**: Make sure you activated the virtual environment and installed Django

### Issue: "Static files not loading"
**Solution**: Make sure you ran `collectstatic` and configured static files URL in Web tab

### Issue: "Database error"
**Solution**: Run `python manage.py migrate` to create/update database tables

### Issue: "404 Error"
**Solution**: Check that your WSGI file path is correct and points to your project folder

---

## Security Warning:

⚠️ **IMPORTANT**: Your `db.sqlite3` file contains:
- All your customer data
- All order information
- All user accounts

**Do NOT commit database files to public repositories!**

Create a `.gitignore` file in your project root:
```bash
cd ~/sportstore  # Your local project
# Create .gitignore file
cat > .gitignore << EOF
*.pyc
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
db.sqlite3
db.sqlite3-journal
media/
staticfiles/
.DS_Store
venv/
env/
ENV/
EOF

# Remove db from git tracking (but keep local copy)
git rm --cached db.sqlite3
git add .gitignore
git commit -m "Remove database from git tracking"
git push
```

---

## Recommended: Switch to PostgreSQL (Free on PythonAnywhere)

SQLite is good for testing, but for production e-commerce, use PostgreSQL:

### Steps:
1. In PythonAnywhere, go to **"Databases"** tab
2. Note your database name, username, password
3. Update `sportstore/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'yourusername$dbname',  # From Databases tab
        'USER': 'yourusername',           # From Databases tab
        'PASSWORD': 'your-password',     # From Databases tab
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

4. In Bash console:
```bash
# Install PostgreSQL adapter
source ~/sites/your-web-app-name/sportstore/venv/bin/activate
pip install psycopg2-binary

# Run migrations to create tables
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

5. Reload web app

---

## Updating Your Site (Future Changes):

After making changes to your code:
```bash
# In Bash console on PythonAnywhere
cd ~/sites/your-web-app-name/sportstore
git pull origin main  # Pull latest changes
source venv/bin/activate
python manage.py migrate  # Apply any new migrations
python manage.py collectstatic --noinput  # Update static files
```

Then go to Web tab and click **"Reload"**

---

## Need Help?

Check PythonAnywhere forums: https://www.pythonanywhere.com/forums/

---

## Quick Reference:

**Web App URL**: `http://yourusername.pythonanywhere.com/`
**Admin Panel**: `http://yourusername.pythonanywhere.com/admin/`
**Console Command**: `cd ~/sites/your-web-app-name/sportstore`
**Reload Web App**: Web tab → Reload button
