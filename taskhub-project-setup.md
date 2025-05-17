# TaskHub Project Files

## Frontend Setup

### 1. Create a new React project with Tailwind CSS

```bash
# Create React app
npx create-react-app taskhub-frontend
cd taskhub-frontend

# Install dependencies
npm install axios

# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 2. Configure Tailwind CSS

Create or update the following files:

**tailwind.config.js**
```javascript
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**src/index.css**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 3. Create Dockerfile for frontend

Create a file named `Dockerfile` in the root of your frontend project:

```Dockerfile
# Build stage
FROM node:20-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 4. Create nginx.conf

```
server {
    listen 80;
    
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://taskhub-backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Backend Setup

### 1. Create a new FastAPI project

```bash
# Create project directory
mkdir taskhub-backend
cd taskhub-backend

# Set up mise for environment management
cat > .mise.toml << EOL
[tools]
python = "3.12"
usage = "latest"

[env]
_.python.venv = { path = ".venv", create = true }
PROJECT_NAME = "taskhub-backend"
PREFIX = "{{ env.PROJECT_NAME }}"

[tasks."uv:reqs"]
description = "Install dependencies from requirements file"
alias = "uvr"
run = "uv pip install -r requirements.txt"

[tasks."uv:freeze"]
description = "Create requirements.txt from currently installed modules"
alias = "uvf"
run = "uv pip freeze > requirements.txt"

[tasks."uv:install"]
description = "Install pip packages"
alias = "uvi"
run = "uv pip install"

[tasks.install-deps]
description = "Install all dependencies"
run = "uv pip install fastapi uvicorn sqlalchemy psycopg2-binary redis pydantic python-dotenv"
alias = "deps"

[tasks.create-reqs]
description = "Create requirements.txt file"
run = "uv pip freeze > requirements.txt"

[tasks.dev]
description = "Run development server"
run = "uvicorn main:app --reload --host 0.0.0.0 --port 8000"

[tasks.info]
description = "Print project information"
run = '''
echo "Project: $PROJECT_NAME"
echo "Virtual Environment: $VIRTUAL_ENV"
'''
EOL

# Initialize the project using mise
mise install
mise run install-deps
mise run create-reqs
```

### 2. Create requirements.txt
```
fastapi==0.110.0
uvicorn==0.27.1
sqlalchemy==2.0.30
psycopg2-binary==2.9.9
redis==5.0.2
pydantic==2.6.3
python-dotenv==1.0.1
```

### 3. Create Dockerfile for backend

Create a file named `Dockerfile` in the root of your backend project:

```Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Running Locally for Testing

### 1. Set up Docker Compose for local testing

Create a `docker-compose.yml` file in the root of the project:

```yaml
version: '3'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:8000

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/taskhub
      - REDIS_URL=redis://redis:6379/0

  postgres:
    image: postgres:14
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=taskhub
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 2. Create a root .mise.toml file for the entire project

Create a `.mise.toml` file in the root of the project:

```toml
[tools]
node = "20"
python = "3.12"
usage = "latest"

[env]
PROJECT_NAME = "taskhub"

[tasks.setup-frontend]
description = "Set up the frontend project"
run = '''
cd frontend
npm install
'''

[tasks.setup-backend]
description = "Set up the backend project"
run = '''
cd backend
mise run install-deps
'''

[tasks.setup]
description = "Set up the entire project"
run = '''
mise run setup-frontend
mise run setup-backend
'''

[tasks.dev]
description = "Run the entire application in development mode"
run = "docker-compose up"

[tasks.build]
description = "Build Docker images"
run = '''
docker-compose build
'''

[tasks.k8s-apply]
description = "Apply Kubernetes manifests"
run = '''
kubectl apply -f k8s/
'''

[tasks.k8s-delete]
description = "Delete Kubernetes resources"
run = '''
kubectl delete -f k8s/
'''

[tasks.argocd-deploy]
description = "Deploy application using ArgoCD"
run = '''
argocd app create taskhub \
  --repo $REPO_URL \
  --path k8s \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace taskhub \
  --sync-policy automated
'''
```

### 3. Run the application locally

```bash
# Install required tools
mise install

# Set up the entire project
mise run setup

# Run the application in development mode
mise run dev

# Alternatively, to build and push Docker images
mise run build
docker tag taskhub-frontend:latest your-registry/taskhub-frontend:latest
docker tag taskhub-backend:latest your-registry/taskhub-backend:latest
docker push your-registry/taskhub-frontend:latest
docker push your-registry/taskhub-backend:latest
```

Visit http://localhost:3000 to see your application running.