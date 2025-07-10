# SpaceNote Installation Guide for Ubuntu 24.04

This guide covers installing SpaceNote on Ubuntu 24.04 using Docker Compose.

**Note**: This guide assumes you're installing on a dedicated VPS as the root user.

## Prerequisites

### 1. Install Docker

```bash
# Update package index
apt update

# Install required packages
apt install -y ca-certificates curl

# Add Docker's official GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
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

### 2. Create .env File

```bash
# MongoDB Configuration
MONGO_INITDB_ROOT_USERNAME=spacenote
MONGO_INITDB_ROOT_PASSWORD=changeme-use-strong-password
MONGO_INITDB_DATABASE=spacenote

# SpaceNote Configuration
SPACENOTE_SESSION_SECRET_KEY=your-secret-key-change-this-to-random-string
SPACENOTE_HOST=0.0.0.0
SPACENOTE_PORT=3000

# Domain Configuration
DOMAIN=your-domain.com
```

**Important**: 
- Generate a strong secret key: `openssl rand -hex 32`
- Use a strong password for MongoDB
- Replace `your-domain.com` with your actual domain

### 3. Create docker-compose.yml

```yaml
services:
  mongodb:
    image: mongo:8
    restart: unless-stopped
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_INITDB_ROOT_USERNAME}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_INITDB_ROOT_PASSWORD}
      MONGO_INITDB_DATABASE: ${MONGO_INITDB_DATABASE}
    networks:
      - spacenote-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  spacenote:
    image: ghcr.io/mcbarinov/spacenote:latest
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      SPACENOTE_DATABASE_URL: mongodb://${MONGO_INITDB_ROOT_USERNAME}:${MONGO_INITDB_ROOT_PASSWORD}@mongodb:27017/${MONGO_INITDB_DATABASE}?authSource=admin
      SPACENOTE_SESSION_SECRET_KEY: ${SPACENOTE_SESSION_SECRET_KEY}
      SPACENOTE_HOST: ${SPACENOTE_HOST}
      SPACENOTE_PORT: ${SPACENOTE_PORT}
    depends_on:
      - mongodb
    networks:
      - spacenote-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  caddy:
    image: caddy:2
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - caddy_data:/data
      - caddy_data:/config
    environment:
      DOMAIN: ${DOMAIN}
    command: caddy reverse-proxy --from ${DOMAIN} --to spacenote:3000
    depends_on:
      - spacenote
    networks:
      - spacenote-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  mongodb_data:
  caddy_data:

networks:
  spacenote-network:
```

### 4. Start Services

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

To update to the latest version:

```bash
# Pull the latest images
docker compose pull

# Restart services with the new version
docker compose up -d
```

To update to a specific version:

```bash
# Edit docker-compose.yml and change the image tag from 'latest' to a specific version
# For example: ghcr.io/mcbarinov/spacenote:0.0.2

# Then pull and restart
docker compose pull
docker compose up -d
```

**Note**: SpaceNote follows semantic versioning. Check the [releases page](https://github.com/mcbarinov/spacenote/releases) for version history and changelog.

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
2. **Permission denied**: Check file permissions
3. **MongoDB connection failed**: Check that MongoDB credentials in .env file are correct

## Security Recommendations

1. Change all default passwords
2. Use strong SPACENOTE_SECRET_KEY (generate with `openssl rand -hex 32`)
3. Configure firewall to allow only necessary ports
4. Keep Docker and system packages updated
5. Use HTTPS in production (Caddy handles this automatically with valid domain)