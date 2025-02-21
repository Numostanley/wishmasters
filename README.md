# Docker compose Installation

## Clone the repository:

```
git clone https://github.com/Numostanley/wishmasters.git
```

## Enter the root directory.
```
cd wishmasters
```

## create .env file
```
sudo nano .env
```

## Add these variables to your .env
```
export SECRET_KEY="your-secret-key"
export ENVIRONMENT="prod"

export ALLOWED_HOSTS="127.0.0.1,localhost,127.0.0.1:8000,13.51.48.129"

export API_PREFIX=api

export API_VERSIONS=v1

export POSTGRES_USER=user
export POSTGRES_PASSWORD=password
export POSTGRES_DB=mydatabase
export DATABASE_HOST=db
```

Run docker-compose

```
docker-compose up --build -d
```
