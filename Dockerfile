# ---- Frontend Build Stage ----
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# ---- Backend Final Stage ----
FROM python:3.9-slim AS backend
WORKDIR /app

# Copy built frontend from the builder stage
COPY --from=frontend-builder /app/frontend/dist /app/static

# Copy backend code and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY app.py .
RUN mkdir -p /data

# Set environment variable to indicate production
ENV APP_ENV=production

# Expose the port Hugging Face will use
EXPOSE 7860

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]

# ---- Frontend Final Stage ----
FROM nginx:alpine AS frontend
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]