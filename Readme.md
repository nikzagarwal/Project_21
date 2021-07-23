# TwentyOne - 21

<p align="center">
  <img src="images/21_logo.png" alt="logo" style="width: 200px" />
</p>
<p align="center">
    <a href="https://curl.tech/" alt="Curl Tech">
    	<img src="http://img.shields.io/badge/CurlTech-informational?style=plastic">
    </a>
</p>
<p align="center">
    <img src="https://img.shields.io/badge/license-MIT-brightgreen.svg">
    <img src="https://img.shields.io/badge/Version-v2.0-orange.svg">
</p>
<hr>

Project 21 is an AutoML engine that aims to make the life of Data Scientists a lot easier by automating the process of generating, tuning and testing the best model according to their dataset.
You provide the data, we provide the best model along with the required expertise to get you started in the field of ML.

Get started now!
[Note: Project 21 is a work in progress. This repo will undergo major changes in the coming months]

---

## Running Project21

This project requires the following dependencies installed beforehand.

* `python` version `3.8+` and/or above.
* `node` version `v10.19.0` 
* `npm` version `6.14.4`
* `MongoDB Community` version `4.4.7` 
* `pip` version 20.0.2

### Installation and Running Instructions - Ubuntu

#### Method 1: Manually Typing Instructions In Terminal

To run the project on Ubuntu by manually typing the commands one by one, do the following - 

* Get a copy of this project locally and install the dependencies:

  1. Fork this repository.

  2. `git clone <url>` - put the url of your forked repo. Once you have the cloned copy locally. `cd` into the project folder.

  3. Create a virtual environment inside the project folder using the following:

     ```shell
     python3 -m venv venv
     ```

  4. Activate the virtual environment using:

     ```shell
     source venv/bin/activate
     ```

  5. Once the environment is activated, install the dependencies using:

     ```shell
     pip3 install -r requirements.txt
     ```

  6. Now install the react dependencies by the following:

     ```shell
     cd Frontend/pr21/
     npm i
     ```

* Once all dependencies are installed go to the project root folder and run the following commands:

  1. Activate the virtual environment if not done so:

     ```shell
     source venv/bin/activate
     ```

  2. Start the Database server (mongodb community server)

     ```shell
     sudo systemctl start mongod
     ```

     Enter your password, if prompted to do so.

  3. Start the Backend server (From the root folder)

     ```shell
     python3 api.py
     ```

  4. Start the Frontend server (From the root folder - can be done by opening a new terminal window)

     ```shell
     cd Frontend/pr21/
     npm start
     ```

* Go to `localhost:3000` and use Project21 for your needs!

#### Method 2: Using Shell Scripts

To run the project on Ubuntu using shell scripts, do the following - 

* Run the Installation shell script

  ```shell
  ./application-install-ubuntu.sh
  ```

* Start the Frontend, Backend and Database server

  ```shell
  ./application-startup-ubuntu.sh
  ```

* Go to `localhost:3000` and use Project21 for your needs!

---

### Installation and Running Instructions - Windows

#### Method 1 - Manually Typing Instructions In Terminal

To run the project on Windows by manually typing the commands one by one, do the following - 

* Get a copy of this project locally and install the dependencies

  1. Fork this repository.

  2. `git clone <url>` - put the url of your forked repo. Once you have the cloned copy locally. `cd` into the project folder.

  3. Create a virtual environment inside the project folder using the following:

     ```shell
     python -m venv venv
     ```

  4. Activate the virtual environment using:

     ```shell
     .\venv\Scripts\activate
     ```

  5. Now Install React dependencies by the following:

     ```shell
     cd Frontend\pr21\
     npm i
     ```

  6. Once the environment is activated, install the dependencies using:

     ```
     pip install -r requirements.txt
     ```

* Once all dependencies are installed go to the project root folder and run the following commands:

  1. Activate the virtual environment if not done so:

     ```shell
     .\venv\Scripts\activate
     ```

  2. Start the Database server - By running MongoDB Community Edition. (Can be downloaded from their website)

  3. Start the Backend server (From the root folder)

     ```shell
     python api.py
     ```

  4. Start the Frontend server (From the root folder - can be done by opening a new terminal window)

     ```shell
     cd Frontend\pr2\
     npm start
     ```

* Go to `localhost:3000/` and use Project21 for your needs!

#### Method 2 - Using Shell Scripts

To run the project on Windows using shell scripts, do the following - 

* Run the Installation shell script

  ```shell
  .\application-install-windows.sh
  ```

* Start the Frontend, Backend and Database server

  ```shell
  .\application-startup-windows.sh
  ```

* Go to `localhost:3000` and use Project21 for your needs!

---

Note: In case of any errors or bugs faced, please raise an issue on the GitHub page. Contributions are gladly welcomed!

---

# Table of Contents

-  [Getting Started](#getting_started)

-  [Architecture of Auto ML 21](#BLOCKS)

-  [Features of Auto ML 21](#Features-of-Project-21)

-  [ML Models](#ML-Models)

  # Getting Started <a id='getting_started'></a>

  

  ![alt text](https://github.com/nikzagarwal/Project_21/blob/master/images/twentyone%20(1)(1).jpeg)




# Architecture of Project 21  <a id='BLOCKS'></a>

### Main concepts

1. Task: task includes the problem type (classification, regression,  seq2seq), the pointer to the data and evaluation metric to be used to  build a model.
2. Data: data holds the raw content and the meta information about the  type of data (text, images, tabular etc.) and its characteristics (size, target, names, how to process etc).
3. Model: is either a machine learning or time series or deep learning model which is needed to learn the relation in the data.
4. Model Universe: is a collection of models, its hyper parameters and the tasks to which it has to be considered.

![top](https://github.com/pooja-bs-3003/twentyone/raw/main/imgs/Blocks.PNG)



## Top level architecture of TwentyOne



![top](https://github.com/pooja-bs-3003/twentyone/raw/main/imgs/top.PNG)

Top level architecture provides how things works in twentyone.



# Features of Project 21 <a id='Features-of-Project-21'></a>

- TwentyOne is designed to leverage transfer learning as much as possible. For  many problems the data requirement for 21 is minimal. This saves a lot  of time, effort and cost in data collection. Model training is also  greatly reduced.

- TwentyOne tries to be an auto ML engine, it can be used as an augmented ML  engine which can help data scientist to quickly develop models. This can bring best of both worlds leading to "Real Intelligence = Artificial  Intelligence + Human Intelligence"

- 21 builds "Robust Models"

- 21 requires less amount of user interaction

- Cost for development is minimal (mainly compute cost, rest is reduced).

- 21 provides Data Security and Privacy

- 21 takes less amount of time to build a model.

- Retraining can be done for same project to improve models 

  

  # ML Models <a id='ML-Models'></a>

  In 21 user can build two categories of machine learning models. They are:

  - **CLASSIFICATION**
  - **REGRESSION**
  - **CLUSTERING**
  - **TIME SERIES**

    

  ## CLASSIFICATION

    Machine learning algorithms is to recognize objects and being able to  separate them into categories. This process is called classification,  and it helps us segregate vast quantities of data into discrete values,  i.e. distinct, like 0/1, True/False, or a pre-defined output label  class.
    > Models Used:
    > 1. Logistic Regression
    > 2. Random Forest Classifier
    > 3. Decision Tree
    > 4. XGBOOST
    > 5. GaussianNB
    > 6. K-NN
    > 7. Polynomial
    > 8. SVR


- Performance of random forest is evaluated by Precision, Recall, F1-score & Accuracy.


   ## Regression

- Regression is a supervised learning technique which helps in finding the correlation between variables and enables us to predict the continuous output variable based on the one or more  predictor variables.
- Regression shows a line or curve that passes through all the datapoints on target-predictor graph in such a way that the vertical  distance between the datapoints and the regression line is minimum.

    > Models Used:
    > 1. Logistic Regression
    > 2. Random Forest Regression
    > 3. DecisionTree
    > 4. XGBOOST
    > 5. GaussianNB
    > 6. K-NN
    > 7. Polynomial
    > 8. SVC
    > 9. MultinomialNB
    
   ## Clustering
   
- Clustering is unsupervised algorithm technique which can be used on data where target variable in unknown. It can be used in forming groups of similar data on different basis
    > Models Used:
    > 1. Kmeans
    > 2. Lmodes
    > 3. DBSCAN
    > 4. Birch
    > 5. Optics
    > 6. K-NN
    > 7. Agglomerative
    > 8. Mean shift
    > 9. Affinity Propagation
    
    ## Time Series
   
- Time series algorithms are used on data which has dependency on time for example sales, finance, temperature etc.
    > Models Used:
    > 1. AR
    > 2. MA
    > 3. ARMA
    > 4. ARIMA
    > 5. SARIMA



### Maintained By

This repository is maintained by  **Shivaramkrs** and curl team members and contributors **Nikhil Agarwal**, **Paarth S Barkur**, **Rishabh Bhatt**, **Pooja BS** & **Shubham Kumar Shaw**.
