all: python nginx

python:
	cd bot && docker build . -t jimber/python_timby:test

nginx:
	cd ui && docker build . -t jimber/nginx_timby:test