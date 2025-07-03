# SpaceNote Installation Guide for Ubuntu 24.04

This guide covers installing SpaceNote on Ubuntu 24.04 using Docker Compose.

## Prerequisites

### 1. Install Docker

```bash
# Update package index
sudo apt update

# Install required packages
sudo apt install -y ca-certificates curl

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Verify Installation

```bash
docker --version
docker compose version
```

## Installation

### 1. Create Project Directory

```bash
mkdir -p ~/spacenote
cd ~/spacenote
```

### 2. Create docker-compose.yml

```yaml
services:
  mongodb:
    image: mongo:8
    restart: unless-stopped
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_ROOT_USERNAME: spacenote
      MONGO_INITDB_ROOT_PASSWORD: changeme
      MONGO_INITDB_DATABASE: spacenote
    networks:
      - spacenote-network

  spacenote:
    image: ghcr.io/mcbarinov/spacenote:latest
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      SPACENOTE_DATABASE_URL: mongodb://spacenote:changeme@mongodb:27017/spacenote?authSource=admin
      SPACENOTE_SECRET_KEY: your-secret-key-change-this
      SPACENOTE_HOST: 0.0.0.0
      SPACENOTE_PORT: 3000
    depends_on:
      - mongodb
    networks:
      - spacenote-network

  caddy:
    image: caddy:2
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - spacenote
    networks:
      - spacenote-network

volumes:
  mongodb_data:
  caddy_data:
  caddy_config:

networks:
  spacenote-network:
```

### 3. Create Caddyfile

For HTTPS with automatic certificates:

```
your-domain.com {
    reverse_proxy spacenote:3000
}
```

For local development (HTTP only):

```
:80 {
    reverse_proxy spacenote:3000
}
```

### 4. Create .env File

```bash
# Database
MONGO_INITDB_ROOT_USERNAME=spacenote
MONGO_INITDB_ROOT_PASSWORD=changeme
MONGO_INITDB_DATABASE=spacenote

# SpaceNote
SPACENOTE_DATABASE_URL=mongodb://spacenote:changeme@mongodb:27017/spacenote?authSource=admin
SPACENOTE_SECRET_KEY=your-secret-key-change-this-to-random-string
SPACENOTE_HOST=0.0.0.0
SPACENOTE_PORT=3000
```

### 5. Start Services

```bash
# Start all services
docker compose up -d

# Check logs
docker compose logs -f

# Check service status
docker compose ps
```

## Post-Installation

### Access SpaceNote

- Local: http://localhost
- With domain: https://your-domain.com

### Default Admin Credentials

On first startup, SpaceNote creates a default admin account:
- Username: `admin`
- Password: `admin`

**Important**: Change this password immediately after first login!

### Stopping Services

```bash
docker compose down
```

### Updating SpaceNote

```bash
# Pull latest image
docker compose pull

# Restart services
docker compose up -d
```

## Troubleshooting

### Check Logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs spacenote
docker compose logs mongodb
```

### Reset Database

```bash
# Stop services
docker compose down

# Remove data volume
docker volume rm spacenote_mongodb_data

# Start again
docker compose up -d
```

### Common Issues

1. **Port already in use**: Change ports in docker-compose.yml
2. **Permission denied**: Make sure your user is in the docker group
3. **MongoDB connection failed**: Check SPACENOTE_DATABASE_URL matches MongoDB credentials

## Security Recommendations

1. Change all default passwords
2. Use strong SPACENOTE_SECRET_KEY (generate with `openssl rand -hex 32`)
3. Configure firewall to allow only necessary ports
4. Keep Docker and system packages updated
5. Use HTTPS in production (Caddy handles this automatically with valid domain)