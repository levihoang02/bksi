FROM node:18

WORKDIR /app

COPY gateway/package.json .
COPY gateway/package-lock.json .

# Install dependencies
RUN npm install

RUN npm install -g pm2

# Copy the rest of the application code
COPY gateway /app

# Expose the port the app runs on
EXPOSE 8210

# Start the application
CMD ["pm2-runtime", "start", "index.js", "--name", "gateway", "--env", "production"]