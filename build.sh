#!/bin/bash

set -o errexit  # Exit on any error

# # Directory where your project resides
# PROJECT_DIR=/opt/render/Builderman

# # Ensure the project directory exists and is writable
# mkdir -p $PROJECT_DIR/nginx/conf/sites-available
# mkdir -p $PROJECT_DIR/nginx/conf/sites-enabled

# # Download and extract nginx binaries
# NGINX_VERSION=1.22.0
# wget http://nginx.org/download/nginx-$NGINX_VERSION.tar.gz
# tar -zxvf nginx-$NGINX_VERSION.tar.gz
# cd nginx-$NGINX_VERSION

# # Configure nginx to install under your project directory
# ./configure --prefix=$PROJECT_DIR/nginx --with-http_ssl_module
# make
# make install

# # Add nginx binaries to PATH for convenience
# export PATH=$PROJECT_DIR/nginx/sbin:$PATH

# # Verify nginx installation
# $PROJECT_DIR/nginx/sbin/nginx -v  # Check nginx version

# # Example nginx configuration for your Django application
# cat > $PROJECT_DIR/nginx/conf/nginx.conf <<EOF
# worker_processes 1;

# events {
#     worker_connections 1024;
# }
# http {
#     include mime.types;
#     default_type application/octet-stream;

#     server {
#         listen 10000;
#         server_name builderman.onrender.com;  # Replace with your Render domain or custom domain

#         location / {
#             proxy_pass https://builderman.onrender.com:10000;  # Adjust port if necessary
#             proxy_set_header Host \$host;
#             proxy_set_header X-Real-IP \$remote_addr;
#             proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
#             proxy_set_header X-Forwarded-Proto \$scheme;
#             proxy_redirect off;
#             proxy_http_version 1.1;
#             proxy_set_header Connection "";
#         }

#         # Additional configuration for serving static files directly if needed
#         location /static/ {
#             alias $PROJECT_DIR/static/;
#         }

#         # Additional configuration for serving media files directly if needed
#         location /media/ {
#             alias $PROJECT_DIR/media/;
#         }
#     }
# }
# EOF

# # Start nginx
# echo "Starting Nginx..."
# $PROJECT_DIR/nginx/sbin/nginx -c $PROJECT_DIR/nginx/conf/nginx.conf
# echo "Nginx started successfully"

# # Change directory to your Django project
# cd .. $PROJECT_DIR

# Build the project (install Python dependencies)
echo "Building the project..."
python -m pip install -r requirements.txt

# Apply Django migrations
echo "Applying Django migrations..."
python manage.py migrate --noinput

# Create superuser if not exists
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
email = 'admin@example.com';
password = 'adminpass';
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password)
else:
    print('Superuser already exists')
"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Deployment completed successfully"
