#!/bin/bash

#The below function will be called in case Ctrl+C is pressed, i.e, Interrupt
terminationFunction () {
    trap INT                    #Restore signal handling to previous before exit.
    echo ''
    echo 'Exiting... Deleting folders created...'    # Printing Message
    rm -rf env                  #Deleting the environment if Interrupt is encountered
    echo 'Deletion Successful. Exited.'
    exit                        #To exit the script
}

# Set up SIGINT trap to call terminationFunction.
trap "terminationFunction" INT

echo 'Project21 Setting up Python Virtual Environment...'
python -m venv venv
echo 'Project21 Python Virtual Environment Created...'

#To Activate the Virtual Environment
. venv\\Scripts\\activate

#install requirements
echo 'Installing Requirements in the virtual environment... This may take a while... (15-20 mins) Please be patient...'
pip install -r requirements.txt
echo 'All requirements installed successfully...'

deactivate

# Restore signal handling to previous before exit.
trap INT