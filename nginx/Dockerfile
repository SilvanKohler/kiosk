FROM nginx

# Remove the default nginx.conf
RUN rm /etc/nginx/conf.d/default.conf

# Replace with our own nginx.conf
COPY nginx.conf /etc/nginx/conf.d/

RUN apt update
RUN apt install -y python3 python3-venv python3-pip libaugeas0 python3-certbot python3-certbot-nginx

COPY cert.sh .
RUN chmod +x cert.sh

RUN apt install -y cron
RUN echo "0 0,12 * * * root certbot renew -q" >> /etc/crontab

# CMD [ "certbot", "--nginx", "--non-interactive", "--agree-tos", "-m", "silvankohler@protonmail.com", "-d", "kiosk.silvankohler.live" ]