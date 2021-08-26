#!/bin/bash

#Installing dependencies for mkcert
sudo apt install libnss3-tools

#Installing golang
sudo apt install golang-go

#Cloning the repo and building the mkcert executable file
git clone https://github.com/FiloSottile/mkcert && cd mkcert
go build -ldflags "-X main.Version=$(git describe --tags)"

#Installing Certificate Authority on the local system
./mkcert -install

#Create certificates for the domains as needed
./mkcert -cert-file cert.pem -key-file key.pem 0.0.0.0 localhost 127.0.0.1 ::1

#Moving the cert.pem and key.pem file to suitable location
mv cert.pem ../Backend/cert/
mv key.pem ../Backend/cert/