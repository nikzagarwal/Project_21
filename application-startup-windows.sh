#!/bin/bash

#The below function will be called in case Ctrl+C is pressed, i.e, Interrupt
terminationFunction () {
    trap INT                    #Restore signal handling to previous before exit.
    echo ''
    echo 'Exiting... MongoDB Server Being Closed...'    # Printing Message
    sudo systemctl stop mongod
    echo 'Exited.'
    exit                        #To exit the script
}

# Set up SIGINT trap to call terminationFunction.
trap "terminationFunction" INT

#To Activate the Virtual Environment
. venv\Scripts\activate

#To Start React - Frontend Server
/bin/bash -ec 'cd Frontend/pr21 && npm start &'

#To Start FastAPI - Backend Server
/bin/bash -ec 'python3 api.py'

# Restore signal handling to previous before exit.
trap INT