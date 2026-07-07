FROM public.ecr.aws/nginx/nginx:1.29.3

RUN apt-get update \
    && apt-get install -y --no-install-recommends --only-upgrade libssh2-1t64 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN rm /etc/nginx/nginx.conf /etc/nginx/conf.d/default.conf

COPY ./config/nginx/production.conf /etc/nginx/nginx.conf
