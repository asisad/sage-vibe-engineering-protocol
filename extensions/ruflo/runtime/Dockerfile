FROM node:22-bookworm-slim@sha256:de170b39439eb0e5a3444ad7d60b015614a381e10fecae2e30ec9e735122f38d
WORKDIR /opt/ruflo
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts --no-audit --no-fund
LABEL sage.ruflo.version="3.61.1" sage.ruflo.role="coordination-only"
ENV HOME=/tmp NODE_ENV=production NO_COLOR=1
WORKDIR /workspace
USER 65534:65534
ENTRYPOINT ["/usr/local/bin/node", "/opt/ruflo/node_modules/ruflo/bin/ruflo.js", "mcp", "start"]
