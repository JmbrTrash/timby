# PYTHON
cd bot
docker build . -t jimber/python_timby:test

cd ..

# NGINX
cd ui
docker build . -t jimber/nginx_timby:test

cd ..