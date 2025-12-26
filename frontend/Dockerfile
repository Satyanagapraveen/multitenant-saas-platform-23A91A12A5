# Frontend Dockerfile for React/Vite Multi-Tenant SaaS
FROM node:20-alpine

# Set work directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Expose port
EXPOSE 3000

# Set environment variable for API URL (will be overridden by docker-compose)
ENV VITE_API_URL=http://localhost:5000/api

# Run Vite dev server on port 3000
CMD ["npm", "run", "dev"]
