import React, { Component } from 'react';
import $ from 'jquery';
import axios from 'axios';
// import { HashLink as Link } from 'react-router-hash-link';
import Result from './Result.js';
import Preprocess from './Preprocess.js';
import ManualModel from './manualmodel.js';
import Section1 from './section1.js';
import Section3 from './section3.js';
import Section4 from './section4.js';
import Section7 from './section7.js';
// import Section5 from './section5.js';
// import Section6 from './section6.js';
import ShowdataModal from './showdataModal.js';
import ShowPlotModal from './showPlotModal.js';
import Papa from 'papaparse';

class Home extends Component {
    constructor(props) {
        super(props)
        this.state = {
            // userID: 101,
            projectname: '',
            train: undefined,
            mtype: 'classification',
            auto: true,
            target: '',
            modelnum: 1,
            nulltype: 'NA',
            currentmodel: 1,
            traindata: "{0:0}",
            clusteringType: "kmeans",
            modeldetail: {
                "Successful": "False",
                "dataID": 0,
                "modelID": 0,
                "projectID": 0,
                "userID": 0,
                "Accuracy":0,
                "hyperparams":0
            },
            projectdetail: {
                "projectID": 0,
                "userID": 0
            },
            preprocessForm: "",
            frequency: "D",
            dateColumn: '',
            automanualpreprocess: false,
            modelForm: "",
            numClusters: 4,
            modalShow: false,
            modalShow2: false,
            openWebSocketConnection: false,
            plot: ""
        }
        this.updateData = this.updateData.bind(this);
    }
    
    handleProjectNameChange = event => {
        this.setState({
            projectname: event.target.value
        })
    }
    handleTrainChange = event => {
        const formdata = new FormData();
        formdata.append(
            "train",
            event.target.files[0]
        );
        axios.post('http://localhost:8000/convertFile', formdata, { headers: { 'Accept': 'multipart/form-data', 'Content-Type': 'multipart/form-data' } })
            .then((response) => {
                console.log("Successful1", response);
                Papa.parse(response.data, {
                    complete: this.updateData,
                    header: true
                })
            },
                (error) => { console.log(error) });
        this.setState({
            train: event.target.files[0]
        })
        // console.log(event.target.files[0]);
    }
    updateData(result) {
        this.setState({
            traindata: result.data
        });
        console.log(this.state.traindata);
    }
    handleMtypeChange = event => {
        this.setState({
            mtype: event.target.value
        })
    }
    handleSubmit = event => {
        event.preventDefault();
        var theFormItself = document.getElementById('form1');
        $(theFormItself).hide();
        if (this.state.mtype !== "timeseries" && this.state.mtype !== "clustering") {
            var theFormItself2 = document.getElementById('form2');
            $(theFormItself2).show();
        }
        else if (this.state.mtype === "clustering") {
            var theFormItself3 = document.getElementById('form3');
            $(theFormItself3).show();
        }
        else {
            var theFormItself6 = document.getElementById('form6');
            $(theFormItself6).show();
        }
        // const { train } = this.state;
        // Papa.parse(train, {
        //     complete: this.updateData,
        //     header: true
        // });
        const formdata = new FormData();
        formdata.append(
            "userID",
            this.state.userID

        );
        formdata.append(
            "projectName",
            this.state.projectname

        );
        formdata.append(
            "mtype",
            this.state.mtype

        );
        formdata.append(
            "train",
            this.state.train
        );


        // console.log(this.state.traindata)

        axios.post('http://'+address+':8000/create', formdata, { headers: { 'Accept': 'multipart/form-data', 'Content-Type': 'multipart/form-data' } })
            .then((res) => {
                console.log("Successful1", res);
                this.setState({
                    projectdetail: res.data
                })
                console.log(this.state.projectdetail)
            },
                (error) => { console.log(error) });
    }
    handleAuto = event => {
        this.setState({
            auto: true
        })
        var theFormItself = document.getElementById('form2');
        $(theFormItself).hide();
        var theFormItself2 = document.getElementById('form3');
        $(theFormItself2).show();
    }
    handleManual = event => {
        this.setState({
            auto: false
        })

        axios.get('http://localhost:8000/getPreprocessParam')
            .then((response) => {
                console.log(response);
                this.setState({
                    preprocessForm: response.data

                })
            });
        var theFormItself = document.getElementById('form2');
        $(theFormItself).hide();
        var theFormItself2 = document.getElementById('form4');
        $(theFormItself2).show();
    }
    handleModelForm = (val) => {
        this.setState({
            modelForm: val
        })
    }
    handleTargetChange = event => {
        this.setState({
            target: event.target.value
        })
    }
    handleDateColumnChange = event => {
        this.setState({
            dateColumn: event.target.value
        })
        console.log(this.state.dateColumn)
    }
    handleFrequencyChange = event => {
        this.setState({
            frequency: event.target.value
        })
    }
    handleModelNumChange = event => {
        this.setState({
            modelnum: event.target.value
        })
    }
    handleClusteringTypeChange = event => {
        this.setState({
            clusteringType: event.target.value
        })
    }
    handleCLusterNumberChange = event => {
        this.setState({
            numClusters: event.target.value
        })
    }
    handleNullTypeChange = event => {
        this.setState({
            nulltype: event.target.value
        })
    }
    handleSubmit2 = event => {
        event.preventDefault();
        setTimeout(() => {
            this.setState({
                auto: true
            })
            event.preventDefault();
            var theFormItself = document.getElementById('form3');
            $(theFormItself).hide();
            var theFormItself2 = document.getElementById('sec1heading');
            $(theFormItself2).hide();
            var theFormItself3 = document.getElementById('sec1heading2');
            $(theFormItself3).show();
            var theFormItself4 = document.getElementById('loader');
            $(theFormItself4).show();
            this.setState({
                modeldetail: {
                    "Successful": "False",
                    "dataID": 0,
                    "modelID": 0,
                    "projectID": 0,
                    "userID": 0
                },
            })
            let userID = this.state.projectdetail["userID"]
            let projectID = this.state.projectdetail["projectID"]
            let isauto = this.state.auto
            let target = this.state.target
            if (target === '') {
                this.setState({
                    target: Object.keys(this.state.traindata[0])[0]
                })
                target = Object.keys(this.state.traindata[0])[0]
            }
            let modelnumber = this.state.modelnum
            let nulltype = this.state.nulltype
            let clusteringType = this.state.clusteringType
            let numClusters = this.state.numClusters
            let data = { userID, projectID, isauto, target, modelnumber, nulltype, clusteringType, numClusters }
            console.log(JSON.stringify(data))

            axios.post('http://localhost:8000/auto', JSON.stringify(data))
                .then(res => {
                    console.log("Successful2", res)
                    this.setState({
                        modeldetail: res.data
                    })
                    console.log(this.state.modeldetail)
                    this.setState({
                        openWebSocketConnection: false
                    })
                },
                    (error) => { console.log(error) });

        }
            , 100);
        setTimeout(() => {
            this.setState({
                openWebSocketConnection: true
            })
        }, 2000);

    }


    handleSubmitTime = event => {
        event.preventDefault();
        setTimeout(() => {
            var theFormItself = document.getElementById('form6');
            $(theFormItself).hide();
            var theFormItself2 = document.getElementById('sec1heading');
            $(theFormItself2).hide();
            var theFormItself3 = document.getElementById('sec1heading2');
            $(theFormItself3).show();
            var theFormItself4 = document.getElementById('loader');
            $(theFormItself4).show();
            this.setState({
                modeldetail: {
                    "Successful": "False",
                    "dataID": 0,
                    "modelID": 0,
                    "projectID": 0,
                    "userID": 0
                },
            })
            let userID = this.state.projectdetail["userID"]
            let projectID = this.state.projectdetail["projectID"]
            let target = this.state.target
            let dateColumn = this.state.dateColumn
            let frequency = this.state.frequency
            if (target === '') {
                this.setState({
                    target: Object.keys(this.state.traindata[0])[0]
                })
                target = Object.keys(this.state.traindata[0])[0]
            }
            console.log(dateColumn)
            if (dateColumn === '') {
                this.setState({
                    dateColumn: Object.keys(this.state.traindata[0])[0]
                })
                dateColumn = Object.keys(this.state.traindata[0])[0]
            }
            let data = { userID, projectID, target, dateColumn, frequency }
            console.log(JSON.stringify(data))

            axios.post('http://localhost:8000/timeseries', JSON.stringify(data))
                .then(res => {
                    console.log("SuccessfulTime", res)
                    this.setState({
                        modeldetail: res.data
                    })
                    console.log(this.state.modeldetail)
                    this.setState({
                        openWebSocketConnection: true
                    })
                },
                    (error) => { console.log(error) });
        }, 100);
        setTimeout(() => {
            this.setState({
                openWebSocketConnection: true
            })
        }, 1000);
    }
    handleSocketConnection = event => {
        this.setState({
            openWebSocketConnection: !this.state.openWebSocketConnection
        })
    }
    handleCurrentModel = (val) => {
        this.setState({
            currentmodel: val
        })
    }
    handleManualModelDetails = (res) => {
        this.setState({
            modeldetail: res
        })
    }
    handleGoForm2() {
        var theFormItself = document.getElementById('form3');
        $(theFormItself).hide();
        var theFormItself3 = document.getElementById('form4');
        $(theFormItself3).hide();
        var theFormItself4 = document.getElementById('form5');
        $(theFormItself4).hide();
        var theFormItself2 = document.getElementById('form2');
        $(theFormItself2).show();

    }
    handleSampleData = event => {
        this.setState({
            modalShow: true
        })
    }
    handleShowPlot = event => {
        var projectid = this.state.projectdetail.projectID
        console.log(projectid)
        const FileDownload = require('js-file-download');
        axios.get('http://'+address+':8000/getEDAPlot/' + projectid)
            .then((response) => {
                console.log(response)
                this.setState({ plot: response.data });
                var answer = window.confirm("Plots are ready and displayed. Want to Download in a file?");
                if (answer) {
                    FileDownload(response.data, 'plot.html');
                }
                else {
                    console.log("plots not downloaded")
                }
            });

        this.setState({
            modalShow2: true
        })
    }
    handleNewProject() {
        window.location.reload();
        // console.log(process.env)
    }
    componentDidMount(){
        let address=""
        if(process.env.REACT_APP_BACKEND_CONTAINER_NAME)
            address=process.env.REACT_APP_BACKEND_CONTAINER_NAME
        else
            address="localhost"
        console.log(address)
    }

    render() {
        return (
            <div>

                {/* ************************************************************************************************************************ */}

                {/* Section1 */}
                <Section1 />
                {/* <showdataModal/> */}
                {/* ************************************************************************************************************************ */}
                {/* Section2  */}
                <div className="section2" id="section2">
                    <div className="newproject" >

                    </div>
                    <div className="createpagebox " id="sec1heading">
                        <button className="btn btn-primary  sec1startbtn " onClick={this.handleNewProject}  >Start New Project </button>
                        <h1 >Start your project </h1>

                    </div>
                    <div className="createpagebox " id="sec1heading2">
                        <button className="btn btn-primary  sec1startbtn " onClick={this.handleNewProject}  >Start New Project </button>

                        <h1>TwentyOne Results</h1>

                        {/* <p>" Just fill relevant feeds and select few choices and you are good to go"</p> */}
                    </div>

                    {/* form1 */}
                    <div className="container " id="form1">
                        <form onSubmit={this.handleSubmit}>
                            <div className="createform">
                                <div className="row">
                                    <div className="col-40">
                                        <label htmlFor="projectname">Name of your project? <span className="ibtn">i <span id="idesc">Enter any relevant name for your project</span></span></label>
                                    </div>
                                    <div className="col-60">

                                        <input type="text" id="projectname" name="projectname" placeholder="Name your project..." value={this.state.projectname} onChange={this.handleProjectNameChange} required />
                                    </div>
                                </div>

                                <div className="row">
                                    <div className="col-40">
                                        <label htmlFor="train">Enter training data <span className="ibtn">i <span id="idesc">Enter the data on which you want to train your model</span></span></label>
                                    </div>
                                    <div className="col-60">
                                        <input type="file" className="form-control" id="train" onChange={this.handleTrainChange} accept=".csv ,.json, .xlsx" name="train"
                                            placeholder="enter training data in csv format" required />
                                    </div>
                                </div>
                                <div className="row">
                                    <div className="col-40">
                                        <label htmlFor="type">Which type of data is it? <span className="ibtn">i <span id="idesc">Generally if no. of classes less than 10 for target its Classification</span></span></label>
                                    </div>
                                    <div className="col-60 ">
                                        <select name="mtype" id="modeltype" value={this.state.mtype} onChange={this.handleMtypeChange}>
                                            <option value="classification">Classification</option>
                                            <option value="regression">Regression</option>
                                            <option value="clustering">Clustering</option>
                                            <option value="timeseries">Time Series</option>
                                        </select>

                                    </div>
                                </div>

                                <div>
                                    <button type="submit" className="btn btn-secondary" id="startengine" >Begin Engine </button>
                                </div>
                            </div>
                        </form>
                    </div>
                    {/* form2 */}
                    <div className="container" id="form2">
                        <div className="centered ">

                            <section className="createform  ">
                                <div className="card-group">
                                    <div className="card flip-card ">
                                        <div className="flip-card-inner">
                                            <div className="flip-card-front">
                                                <h1>Auto</h1>
                                            </div>
                                            <div className="flip-card-back">
                                                <p>"Leave everything on us and see the beauty of artificial Intelligence"</p>
                                                <button className="btn2 btn btn-primary" onClick={this.handleAuto} id="form2autobutton ">Select</button>
                                            </div>
                                        </div>
                                    </div>
                                    <div className=" card flip-card ">
                                        <div className="flip-card-inner">
                                            <div className="flip-card-front">
                                                <h1>Manual</h1>
                                            </div>
                                            <div className="flip-card-back">
                                                <p>"We believe you are always the boss and you can choose to make models as you wish"</p>
                                                <button className="btn2 btn btn-primary" onClick={this.handleManual}>Select</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                            </section>
                        </div>
                    </div>

                    {/* form3 */}
                    <div className="container" id="form3">
                        <div className="goback">
                            <button className="btn btn-primary backbtn " onClick={this.handleGoForm2}  > &larr; Back </button>
                            <button className="btn btn-primary sampleData" id="sampleData" onClick={this.handleSampleData}>See Sample Data</button>
                            <button className="btn btn-primary Eda" id="EDA" onClick={this.handleShowPlot}>See EDA Plot</button>
                            < ShowdataModal
                                show={this.state.modalShow}
                                onHide={() => this.setState({ modalShow: false })}
                                rawdata={this.state.traindata}
                            />
                            <ShowPlotModal
                                show={this.state.modalShow2}
                                onHide={() => this.setState({ modalShow2: false })}
                                plot={this.state.plot} />
                        </div>
                        <form onSubmit={this.handleSubmit2}>
                            <div className="createform">

                                {this.state.mtype !== "clustering" ?
                                    <div className="row">
                                        <div className="col-40">

                                            <label htmlFor="target">Target Variable  <span className="ibtn">i <span id="idesc">Select column which you want model to predict</span></span></label>
                                        </div>
                                        <div className="col-60">
                                            <select name="target" id="target" onChange={this.handleTargetChange}>
                                                {Object.keys(this.state.traindata[0]).map((key, i) =>
                                                    <option key={i} value={key} >{key}</option>
                                                )}
                                            </select>
                                            {/* <input type="text" id="target" name="target" onChange={this.handleTargetChange} placeholder="Enter target variable" required /> */}
                                        </div>
                                    </div>
                                    :
                                    <div>
                                        <div className="row">
                                            <div className="col-40">
                                                <label htmlFor="clusteringType">Which type of data is it? <span className="ibtn">i <span id="idesc">Kmeans is best in general</span></span></label>
                                            </div>
                                            <div className="col-60 ">
                                                <select name="clusteringType" id="clusteringType" value={this.state.clusteringType} onChange={this.handleClusteringTypeChange}>
                                                    <option value="kmeans">K-Means</option>
                                                    <option value="kmodes">K-Modes</option>
                                                    <option value="dbscan">Density-Based Spatial Clustering</option>
                                                    <option value="birch">Birch Clustering</option>
                                                    <option value="optics">OPTICS Clustering</option>
                                                    <option value="hclust"> Agglomerative Clustering</option>
                                                    <option value="meanshift">Mean shift Clustering</option>
                                                    <option value="ap">Affinity Propagation</option>
                                                </select>

                                            </div>
                                        </div>
                                        <div className="row">
                                            <div className="col-40">
                                                <label htmlFor="num_clusters">Number of clusters <span className="ibtn">i <span id="idesc">K=4 works good most of times</span></span></label>
                                            </div>
                                            <div className="col-60" >
                                                <input type="number" id="num_clusters" name="num_clusters" onChange={this.handleCLusterNumberChange} placeholder="Enter K" required />
                                            </div>
                                        </div>
                                    </div>

                                }

                                {/* <div className="row">
                                    <div className="col-40">
                                        <label htmlFor="modelno">How many top models you want?</label>
                                    </div>
                                    <div className="col-60" >
                                        <input type="number" id="modelno" name="modelno" onChange={this.handleModelNumChange} placeholder="Enter number of models" required />
                                    </div>
                                </div> */}
                                {/* <div className="row">
                                    <div className="col-40">
                                        <label htmlFor="nulltype">How are null values specified in dataset?</label>
                                    </div>
                                    <div className="col-60" >
                                        <input type="text" id="nulltype" name="nulltype" onChange={this.handleNullTypeChange} placeholder="Is it NULL, NA , ? , 0 or other (specify)"  />
                                    </div>
                                </div> */}

                                <div>
                                    <button type="submit" className="btn btn-secondary " id="trainnow" >Train Now</button>

                                </div>
                            </div>
                        </form>
                    </div>
                    {/* loader */}
                    <Result
                        modelnum={this.state.modelnum}
                        currentmodel={this.state.currentmodel}
                        projectdetail={this.state.modeldetail}
                        handler={this.handleCurrentModel}
                        projectname={this.state.projectname}
                        isauto={this.state.auto}
                        mtype={this.state.mtype}
                        openWebSocketConnection={this.state.openWebSocketConnection} />
                    {/* ************************************************************************************************************************ */}

                    {/* form 4 for manual preprocessing */}
                    <div className="container" id="form4">
                        <div className="goback">
                            <button className="btn btn-primary backbtn" onClick={this.handleGoForm2}  > Go Back </button>

                        </div>
                        <div className="PreprocessForm">
                            {/* <div className="autocheckbox">
                                <input type="checkbox" id="autopreprocess" onClick={this.handleAutoPreprocess} name="autopreprocess" />
                                <label htmlFor="autopreprocess"> Auto Pre-process</label>
                            </div>
                            <h1>Pre-process</h1>
                            <p>Each Column can be processed differently as required</p> */}
                            <Preprocess rawdata={this.state.traindata} proprocessForm={this.state.preprocessForm} automanualpreprocess={this.state.automanualpreprocess} handleModelForm={this.handleModelForm} projectdetail={this.state.projectdetail} />
                        </div>
                    </div>
                    {/* form 5 for model and hypeparameters selection*/}
                    <div className="container" id="form5">
                        <div className="goback">
                            <button className="btn btn-primary backbtn" onClick={this.handleGoForm2}  > Go Back </button>
                        </div>
                        <div className="Modelselection">
                            {/* <div className="autocheckbox">
                                <input type="checkbox" id="automodel" onClick={this.handleAutoModelSelect} name="automodel" />
                                <label htmlFor="automodel"> Auto Models</label>
                            </div>
                            <h1>Models</h1>
                            <p>Preprocessing is being done. Now, select models and their hyperparameters</p> */}
                            <ManualModel
                                modelForm={this.state.modelForm}
                                mtype={this.state.mtype}
                                projectdetail={this.state.projectdetail}
                                handleManualModelDetails={this.handleManualModelDetails}
                                handleSocketConnection={this.handleSocketConnection} />
                        </div>
                    </div>
                    {/* form6 for time series */}
                    <div className="container" id="form6">
                        <div className="goback">
                            <button className="btn btn-primary sampleData" id="sampleData" onClick={this.handleSampleData}>See Sample Data</button>
                            <button className="btn btn-primary Eda" id="EDA" onClick={this.handleShowPlot}>See EDA Plot</button>
                        </div>
                        <form onSubmit={this.handleSubmitTime}>
                            <div className="createform">


                                <div className="row">
                                    <div className="col-40">

                                        <label htmlFor="targettime">Target Variable  <span className="ibtn">i <span id="idesc">Select column which you want model to predict</span></span></label>
                                    </div>
                                    <div className="col-60">
                                        <select name="targettime" id="targettime" onChange={this.handleTargetChange}>
                                            {Object.keys(this.state.traindata[0]).map((key, i) =>
                                                <option key={i} value={key} >{key}</option>
                                            )}
                                        </select>
                                    </div>
                                </div>
                                <div className="row">
                                    <div className="col-40">

                                        <label htmlFor="date">Date Column  <span className="ibtn">i <span id="idesc">Select column which says about Date</span></span></label>
                                    </div>
                                    <div className="col-60">
                                        <select name="date" id="date" onChange={this.handleDateColumnChange}>
                                            {Object.keys(this.state.traindata[0]).map((key, i) =>
                                                <option key={i} value={key} >{key}</option>
                                            )}
                                        </select>
                                    </div>
                                </div>
                                <div>
                                    <div className="row">
                                        <div className="col-40">
                                            <label htmlFor="Frequency">What is frequency of time series? <span className="ibtn">i <span id="idesc">Is your data daily or monthly and so on</span></span></label>
                                        </div>
                                        <div className="col-60 ">
                                            <select name="Frequency" id="Frequency" value={this.state.frequency} onChange={this.handleFrequencyChange}>
                                                <option value="D">Daily</option>
                                                <option value="W">Weekly</option>
                                                <option value="M">Monthly</option>
                                                <option value="Q">Quaterly</option>
                                                <option value="Y">Yearly</option>
                                                {/* <option value="S">Secondly</option>
                                                <option value="T">Minutely</option>
                                                <option value="H">Hourly</option>
                                                <option value="B">Business days</option> */}




                                            </select>

                                        </div>
                                    </div>
                                </div>




                                <div>
                                    <button type="submit" className="btn btn-secondary" id="traintimenow" >Train Now</button>
                                </div>
                            </div>
                        </form>
                    </div>
                    {/* ************************************************************************************************************************ */}
                </div>
                {/* Section3  */}
                {/* This section is for showing demo video */}
                <Section3 />
                {/* ************************************************************************************************************************ */}
                {/* Section 5 */}
                {/* This section is to show detail of every trained model */}
                {/* <Section5 currentmodel={this.state.currentmodel} /> */}
                {/* ************************************************************************************************************************ */}
                {/* Section 6 */}
                {/* This section is to show all models trained */}
                {/* <Section6 modelnum={this.state.modelnum} handler={this.handleCurrentModel} projectname={this.state.projectname} isauto={this.state.isauto} /> */}
                {/* ************************************************************************************************************************ */}
                {/* Section 7 */}
                {/* This section is to show detail of every Project  */}
                <Section7 handler={this.handleCurrentModel} currentmodel={this.state.currentmodel} />
                {/* Section 4 */}
                {/* This Section id for About */}
                <Section4 />
                {/* ************************************************************************************************************************ */}

            </div >
        );
    }
}

export default Home;