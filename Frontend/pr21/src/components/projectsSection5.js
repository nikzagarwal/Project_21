import React, { Component } from 'react';
import $ from 'jquery';
import Plots from './plots.js';
import Download from './download.js';
import Metrics from './metrics.js';
import axios from 'axios';
import Papa from 'papaparse';
class ProjectsSection5 extends Component {



    constructor() {
        super();
        this.state = {
            data: "",
            inferencefile: undefined,
            plot: "",
            countplot: 0,
            inferenceTime: 1,
            freq: "D"
        };
        this.updateData = this.updateData.bind(this);
    }
    method() {
        this.setState(
            {
                data: "",
                counterplot: 0
            }
        );

    }
    handleGoBack = event => {
        event.preventDefault();
        var theFormItself = document.getElementById('projectsection5');
        $(theFormItself).hide();
        var theFormItself2 = document.getElementById('projectsection6');
        $(theFormItself2).show();
        var thebtnItself = document.getElementById('show');
        $(thebtnItself).show();
        this.setState({ data: "" });

    }
    updateData(result) {
        this.setState({
            data: result.data
        });
    }
    handlemetric = event => {
        console.log(this.props.projectdetails)
        var thebtnItself = document.getElementById('show');
        $(thebtnItself).hide();
        this.setState({ data: "a" });
        const projectid = this.props.projectdetails["projectID"];
        const modelid = this.props.projectdetails["modelID"];
        const FileDownload = require('js-file-download');
        axios.get('http://localhost:8000/getMetrics/' + projectid + "/" + modelid)
            .then((response) => {
                Papa.parse(response.data, {
                    complete: this.updateData,
                    header: true
                });
                if (this.props.projectdetails.modelType === "clustering") {
                    FileDownload(response.data, 'metrics.csv');
                    alert("File is big so it is downloaded");
                }
            });


    }
    handlePlot = event => {
        const FileDownload = require('js-file-download');
        const projectid = this.props.projectdetails["projectID"];
        axios.get('http://localhost:8000/getPlots/' + projectid)
            .then((response) => {
                this.setState({ plot: response.data });
                var answer = window.confirm("Plots are ready and displayed. Want to Download in a file?");
                if (answer) {
                    FileDownload(response.data, 'plot.html');
                }
                else {
                    console.log("plots not downloaded")
                }
            });
        this.setState({ countplot: 1 })
    }


    handleInferenceChange = event => {
        this.setState({
            inferencefile: event.target.files[0]
        })
    }
    handleFrequencyChange = event => {
        this.setState({
            freq: event.target.value
        })
    }
    handleTimeInferenceChange = event => {
        this.setState({
            inferenceTime: event.target.value
        })

    }
    handleGetPrediction = event => {
        event.preventDefault();
        const formdata = new FormData();
        formdata.append(
            "projectID",
            this.props.projectdetails["projectID"]

        );
        formdata.append(
            "modelID",
            this.props.projectdetails["modelID"]

        );
        formdata.append(
            "inferenceDataFile",
            this.state.inferencefile

        );
        const FileDownload = require('js-file-download');
        if (this.props.isauto === true)
            axios.post('http://localhost:8000/doInference', formdata, { headers: { 'Accept': 'multipart/form-data', 'Content-Type': 'multipart/form-data' } })
                .then((res) => {
                    console.log("Successful Auto inference", res)
                    FileDownload(res.data, 'prediction.csv');
                    alert("Prediction is Ready and Downloaded");
                },
                    (error) => { console.log(error) });
        else
            axios.post('http://localhost:8000/doManualInference', formdata, { headers: { 'Accept': 'multipart/form-data', 'Content-Type': 'multipart/form-data' } })
                .then((res) => {
                    console.log("Successful Manual Inference", res)
                    FileDownload(res.data, 'prediction.csv');
                    alert("Prediction is Ready and Downloaded");
                },
                    (error) => { console.log(error) });
    }
    handleGetTimePrediction = event => {
        event.preventDefault();
        const formdata = new FormData();
        formdata.append(
            "projectID",
            this.props.projectdetails["projectID"]

        );
        formdata.append(
            "modelID",
            this.props.projectdetails["modelID"]

        );
        formdata.append(
            "inferenceTime",
            this.state.inferenceTime

        );
        formdata.append(
            "frequency",
            this.state.freq

        );
        console.log(this.state.inferenceTime)
        const FileDownload = require('js-file-download');
        axios.post('http://localhost:8000/doTimeseriesInference', formdata, { headers: { 'Accept': 'multipart/form-data', 'Content-Type': 'multipart/form-data' } })
            .then((res) => {
                console.log("Successful", res)
                FileDownload(res.data, 'prediction.csv');
                alert("Prediction is Ready and Downloaded");
                axios.post('http://localhost:8000/doTimeseriesInferencePlot', formdata, { headers: { 'Accept': 'multipart/form-data', 'Content-Type': 'multipart/form-data' } })
                    .then((res) => {
                        console.log("Successful", res)
                        FileDownload(res.data, 'predictionplot.html');
                        alert("Prediction plot is Ready and Downloaded");
                    },
                        (error) => { console.log(error) });
            },
                (error) => { console.log(error) });


    }

    render() {
        return (

            <div className="section5 " id="projectsection5">
                 <div id="mySidenav" class="sidenav">
                    <h5>Hyperparamters</h5>
                    {/* <p>{this.props.hyperparameters</p> */}
                    <p>Work in progress...</p>
                </div>
                <div className="goback">
                    <button className="backbtn btn btn-secondary" onClick={this.handleGoBack}  > &larr; Models </button>

                </div>

                <div className="sec5heading">
                    <h1>Results </h1>
                </div>
               

                <div className="container">
                    {/* <!-- Nav tabs --> */}
                    <ul className="nav nav-tabs" id="myTab" role="tablist">
                        <li className="nav-item" role="presentation">
                            <button className="nav-link tabbtn active" id="Metrics-tab" data-bs-toggle="tab" data-bs-target="#metrics" type="button" role="tab" aria-controls="metrics" aria-selected="true">
                                {this.props.projectdetails.modelType === "clustering" ? "Alloted Clusters" : "Metrics"}</button>
                        </li>
                        <li className="nav-item" role="presentation">
                            <button className="nav-link tabbtn " id="plot-tab" onClick={this.handlePlot} data-bs-toggle="tab" data-bs-target="#plot" type="button" role="tab" aria-controls="Plot" aria-selected="false">EDA Plots</button>
                        </li>
                        <li className="nav-item" role="presentation">
                            <button className="nav-link tabbtn" id="download-tab" data-bs-toggle="tab" data-bs-target="#download" type="button" role="tab" aria-controls="Download" aria-selected="false">Download</button>
                        </li>
                        <li className="nav-item" role="presentation">
                            <button className="nav-link tabbtn" id="Inference-tab" data-bs-toggle="tab" data-bs-target="#inference" type="button" role="tab" aria-controls="Inference" aria-selected="false">Inference</button>
                        </li>
                    </ul>

                    {/* <!-- Tab panes --> */}
                    <div className="tab-content">
                        <div className="tab-pane active" id="metrics" role="tabpanel" aria-labelledby="metrics-tab">
                            {/* Metrics will be displayed here */}
                            {/* <input type="file" className="form-control" id="metric" onChange={this.handleChange} accept=".csv" name="metric"
                                placeholder="enter data in csv" required />
                            <button onClick={this.importCSV} className="sec5btn">Import</button> */}
                            <button onClick={this.handlemetric} className="sec5btn btn btn-primary" id="show">Show</button>
                            <Metrics data={this.state.data} mtype={this.props.projectdetails.modelType} />
                        </div>



                        <div className="tab-pane" id="plot" role="tabpanel" aria-labelledby="plot-tab">

                            <div className="container">
                                <div className="d-flex flex-row justify-content-center flex-wrap">
                                    <Plots plot={this.state.plot} />
                                    {/* <div className="d-flex flex-column plot" >
                                         <img src="3" className="img-fluid" alt=" Plot3 not for this model " />*/}

                                </div>
                            </div>
                        </div>
                        <div className="tab-pane" id="download" role="tabpanel" aria-labelledby="download-tab">

                            <section className=" cards2 card-group ">
                                <div className="card flip-card ">
                                    <div className="flip-card-inner ">
                                        <div className="flip-card-front2">
                                            <h1>Clean Data</h1>
                                        </div>
                                        <div className="flip-card-back2 ">
                                            <p>"Download clean Data"</p>
                                            <Download type="clean" projectdetails={this.props.projectdetails} />


                                        </div>
                                    </div>
                                </div>
                                <div className="card flip-card ">
                                    <div className="flip-card-inner">
                                        <div className="flip-card-front2">
                                            <h1>Pickle File</h1>
                                        </div>
                                        <div className="flip-card-back2 ">
                                            <p>"Download pickle file"</p>
                                            <Download type="pickle" projectdetails={this.props.projectdetails} />

                                        </div>
                                    </div>
                                </div>

                            </section>
                        </div>
                        <div className="tab-pane" id="inference" role="tabpanel" aria-labelledby="Inference-tab">
                            <div className="container " id="form1">
                                <form >
                                    <div className="createform">
                                        {this.props.projectdetails.modelType !== "timeseries" ? <div>

                                            <div className="row">
                                                <div className="col-40">
                                                    <label htmlFor="Inference">Enter data to get Prediction</label>
                                                </div>
                                                <div className="col-60">
                                                    <input type="file" className="form-control" id="inference" onChange={this.handleInferenceChange} accept=".csv" name="inference"
                                                        placeholder="enter training data in csv format" required />
                                                </div>
                                            </div>


                                            <div>
                                                <button type="submit" className="btn btn-secondary" onClick={this.handleGetPrediction} id="getresults" >Get Results</button>
                                            </div>
                                        </div> :
                                            <div>
                                                <div className="row">
                                                    <div className="col-40">
                                                        <label htmlFor="Inferencetime">Enter Periods you want to forecast</label>
                                                    </div>
                                                    <div className="col-60">
                                                        <input type="number" className="form-control" id="inferencetime" onChange={this.handleTimeInferenceChange} name="inferencetime"
                                                            placeholder="Enter number of future days for prediction" required />
                                                    </div>
                                                </div>
                                                <div className="row">
                                                    <div className="col-40">
                                                        <label htmlFor="Frequency">What is frequency of period? <span className="ibtn">i <span id="idesc">Is your period daily or monthly and so on</span></span></label>
                                                    </div>
                                                    <div className="col-60 ">
                                                        <select name="Frequency" id="Frequency" value={this.state.frequency} onChange={this.handleFrequencyChange}>
                                                            <option value="D">Daily</option>
                                                            <option value="W">Weekly</option>
                                                            <option value="M">Monthly</option>
                                                            <option value="Q">Quaterly</option>
                                                            <option value="Y">Yearly</option>
                                                        </select>
                                                    </div>
                                                </div>


                                                <div>
                                                    <button type="submit" className="btn btn-secondary" onClick={this.handleGetTimePrediction} id="getresultstime" >Get Results</button>
                                                </div>

                                            </div>
                                        }
                                    </div>
                                </form>
                            </div>
                        </div>

                    </div>
                </div >
            </div >

        );
    }
}

export default ProjectsSection5;
