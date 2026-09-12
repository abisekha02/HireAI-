# Development image: runs the Vite dev server with hot reload.
# For production, run `npm run build` and serve the static `dist/`
# output behind nginx or the backend's whitenoise/static handling.
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
