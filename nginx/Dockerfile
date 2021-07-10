FROM nginx

# Remove the default nginx.conf
RUN rm /etc/nginx/conf.d/default.conf

# Replace with our own nginx.conf
COPY nginx.conf /etc/nginx/conf.d/
COPY . .

RUN apt update
RUN apt install -y python3 python3-venv python3-pip libaugeas0 python3-certbot python3-certbot-nginx

RUN apt install -y cron
RUN echo "0 0,12 * * * root certbot renew -q" >> /etc/crontab

RUN chmod +x entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]