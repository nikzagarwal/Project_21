FROM node:10.19.0

LABEL version="2.0"
LABEL description="This is the docker image of the React Frontend App for Project21"
LABEL maintainers=["Curl Tech"]

COPY pr21/ /Frontend/pr21/

WORKDIR /Frontend/pr21/

RUN npm install
RUN npm install js-file-download --save
# RUN npm install react-scripts -g

#Ports needed to be exposed, 3000 is the port where react runs and 35729 is the port needed to enable hot reloading during development
EXPOSE 3000
EXPOSE 35729 

CMD ["npm", "start"]