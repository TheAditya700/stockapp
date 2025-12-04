# Use an official Node.js runtime as a parent image
FROM node:18

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]

