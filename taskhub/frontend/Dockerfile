FROM --platform=linux/arm64 node:23-alpine AS build
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM --platform=linux/arm64 node:23-alpine AS production
WORKDIR /app

# Copy built assets from build stage
COPY --from=build /app/package*.json ./
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/node_modules ./node_modules

# Set environment variables
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Expose the listening port
EXPOSE 3000

# Run the application
CMD ["npm", "start"]