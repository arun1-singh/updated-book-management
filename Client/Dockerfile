# Frontend Dockerfile for React + Vite App
# Multi-stage build for optimal image size

# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* yarn.lock* ./

# Install dependencies
RUN if [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
    elif [ -f package-lock.json ]; then npm ci; \
    else npm install; fi

# Copy source code
COPY . .

# Build the production app
RUN npm run build

# Production stage - serve with Node
FROM node:18-alpine

WORKDIR /app

# Install serve to run the production build
RUN npm install -g serve

# Copy built assets from builder
COPY --from=builder /app/dist ./dist

# Create a simple server configuration
COPY --from=builder /app/package.json ./

# Expose the port (frontend dev server runs on 5173, but production on 3000)
# We'll use 5173 for consistency with dev environment
EXPOSE 5173

# Set environment variables
ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:5173 || exit 1

# Start the production server on port 5173
CMD ["serve", "-s", "dist", "-l", "5173"]
