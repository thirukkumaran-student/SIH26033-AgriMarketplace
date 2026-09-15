# Stage 1: Build the frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# We can pass VITE_API_BASE_URL as an arg, but it defaults to the .env in the repo
RUN npm run build

# Stage 2: Backend runtime
FROM python:3.11-slim AS backend
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 3: Frontend runtime (Nginx)
FROM nginx:alpine AS frontend
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html
# We can use a custom nginx config if we need SPA routing, but a simple SPA needs a try_files rule.
# To keep it simple, we'll just add a small inline config.
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
