# ---------- Build stage ----------
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code and build
COPY . .
RUN npm run build


# ---------- Production stage ----------
FROM node:20-alpine

WORKDIR /app

# Install a lightweight static server
RUN npm install -g serve

# Copy the built files from build stage
COPY --from=build /app/dist ./dist

# Expose required port
EXPOSE 3000

# Serve the production build
CMD ["serve", "-s", "dist", "-l", "3000"]
