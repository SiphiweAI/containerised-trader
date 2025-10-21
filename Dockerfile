FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git curl cron wget gnupg supervisor \
    libnss3 libatk-bridge2.0-0 libgtk-3-0 \
    libx11-xcb1 libxcomposite1 libxcursor1 \
    libxdamage1 libxi6 libxtst6 libxrandr2 \
    libgbm1 libasound2 libpangocairo-1.0-0 \
    libpangoft2-1.0-0 libxshmfence1 libxinerama1 \
    libxext6 libegl1 libatk1.0-0 xvfb x11-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 5000

CMD ["/usr/bin/supervisord"]