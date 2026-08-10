FROM public.ecr.aws/nginx/nginx:1.29.3

# libheif arrives via nginx-module-image-filter -> libgd3. The base image still ships the
# version vulnerable to DSA-6417-1, so upgrade it here rather than waiting for a base bump.
RUN apt-get update \
    && apt-get install -y --no-install-recommends --only-upgrade \
    libssh2-1t64 \
    libheif1 \
    libheif-plugin-libde265 \
    libheif-plugin-dav1d \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN rm /etc/nginx/nginx.conf /etc/nginx/conf.d/default.conf

COPY ./config/nginx/production.conf /etc/nginx/nginx.conf
