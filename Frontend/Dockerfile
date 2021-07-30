FROM node:10.19.0

LABEL version="2.0"
LABEL description="This is the docker image of the React Frontend App for Project21"
LABEL maintainers=["Curl Tech"]

COPY pr21/ /Frontend/pr21/

WORKDIR /Frontend/pr21/
RUN npm i
RUN npm install js-file-download --save

EXPOSE 3000

CMD ["npm", "start"]