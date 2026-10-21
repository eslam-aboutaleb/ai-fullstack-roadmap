# Exercise tags: resolve and record registry digests before promoting a real release.
FROM node:22-bookworm-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts
COPY index.html tsconfig.json vite.config.ts ./
COPY src ./src
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY server.py ./server.py
USER 10001:10001
EXPOSE 8787
CMD ["python", "-B", "server.py", "--host", "0.0.0.0"]
