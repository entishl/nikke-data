# ---- Frontend Build Stage ----
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# ---- Backend Final Stage ----
FROM python:3.9-slim
WORKDIR /app

# Copy built frontend from the builder stage
COPY --from=frontend-builder /app/frontend/dist /app/static

# Copy backend code and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
RUN mkdir /data
COPY list.json .
COPY cube.json .
COPY number.json .

# Expose the port Hugging Face will use
EXPOSE 7860

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]