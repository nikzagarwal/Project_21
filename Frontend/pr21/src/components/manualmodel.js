import React, { Component } from 'react';
import HyperModal from './hypermodal.js';
import axios from 'axios';
import $ from 'jquery';
class ManualModel extends Component {
    constructor(props) {
        super(props)
        this.state = {
            classimodellist: ['LogisticRegression', 'RandomForestClassifier', 'DecisionTree', 'XGBOOST', 'GaussianNB', 'K-NN'],
            regmodellist: ['LinearRegression', 'PolynomialRegression', 'RandomForest', 'DecisionTree', 'XGBOOST', 'K-NN'],
            modalShow: false,
            currentModel: "",
            hyperForm: ""
        }
    }
    static getDerivedStateFromProps(nextProps, prevState) {
        if (prevState.hyperForm === "") {
            return { hyperForm: Object.values(nextProps)[0] };
        }

        return null;
    }
    handlehyperselection = (val) => event => {
        var checkbox = event.target;
        if (checkbox.checked) {
            // this.setState(prevState => ({

            //     hyperForm: Object.values({
            //         ...prevState.hyperForm,
            //         [val]: {
            //             ...prevState.hyperForm[val],
            //             "isSelected": true
            //         }
            //     }),


            // }
            // ))
            // console.log(val)
            this.setState({ modalShow: true })
            this.setState({ currentModel: val })
        }

        else {
            this.setState(prevState => ({

                hyperForm: Object.values({
                    ...prevState.hyperForm,
                    [val]: {
                        ...prevState.hyperForm[val],
                        "isSelected": false
                    }
                })

            }
            ))

            this.setState({ modalShow: false })
        }
    }
    handlehyperChange = (data) => {
        this.setState({
            hyperForm: data
        })
    }
    handleAutoModelSelect = event => {
        var checkbox = event.target;
        var theFormItself = document.getElementById('modellist');
        $(theFormItself).toggle();
        let type
        if (this.props.mtype === 'classification')
            type = "Classification"
        else
            type = "Regression"
        if (checkbox.checked === true) {
            const len = this.state.hyperForm.length
            for (let i = 0; i < len; i++) {
                if (this.state.hyperForm[i].type === type) {
                    this.setState(prevState => ({

                        hyperForm: Object.values({
                            ...prevState.hyperForm,
                            [i]: {
                                ...prevState.hyperForm[i],
                                "isSelected": true
                            }
                        }),


                    }
                    ))
                }
            }

        }
        else{
            const len = this.state.hyperForm.length
            for (let i = 0; i < len; i++) {
                if (this.state.hyperForm[i].type === type) {
                    this.setState(prevState => ({

                        hyperForm: Object.values({
                            ...prevState.hyperForm,
                            [i]: {
                                ...prevState.hyperForm[i],
                                "isSelected": false
                            }
                        }),


                    }
                    ))
                }
            }
        }

    }
    handleTrain = event => {
        let projectID = this.props.projectdetail.projectID
        let userID = this.props.projectdetail.userID
        console.log(JSON.stringify(this.state.hyperForm))
        axios.post('http://localhost:8000/manual/' + userID + '/' + projectID, JSON.stringify(this.state.hyperForm))
            .then(res => {
                console.log("SuccessfulTime", res)
                this.setState({
                    modeldetail: res.data
                })
                console.log(this.state.modeldetail)
            },
                (error) => { console.log(error) });


    }
    render() {
        console.log(this.state.hyperForm)
        if (this.props.mtype === 'classification') {
            const Classificationitems = []
            const len = this.state.hyperForm.length
            for (let i = 0; i < len; i += 3) {
                let item = []
                for (let j = i; j < i + 3 && j < len; j++) {
                    item.push(
                        this.state.hyperForm[j].type === "Classification" ?
                            <div className="card sec6card manualcard">

                                <div className="card-body manualmodellist">
                                    <span> <input type="checkbox" id={j + "automodel"} value={this.state.hyperForm[j].name} onClick={this.handlehyperselection(j)} name="automodel" />
                                        <label htmlFor="automodel" className="card-model-list"> {this.state.hyperForm[j].name}</label>
                                    </span>
                                    <div className="manualmodelcard">
                                        <HyperModal
                                            show={this.state.modalShow}
                                            onHide={() => this.setState({ modalShow: false })}
                                            modelNumber={this.state.currentModel}
                                            mtype={this.props.mtype}
                                            hyperForm={this.state.hyperForm}
                                            handlehyperChange={this.handlehyperChange}
                                        />
                                    </div>
                                </div>
                            </div>
                            : null
                    )
                }
                Classificationitems.push(
                    <div className="card-group text-center">
                        {item}
                    </div>
                )

            }
            return (
                <div>
                    <div className="autocheckbox">
                        <input type="checkbox" id="automodel" onClick={this.handleAutoModelSelect} name="automodel" />
                        <label htmlFor="automodel"> Auto Models</label>
                    </div>
                    <h1>Models</h1>
                    <p>Preprocessing is being done. Now, select models and their hyperparameters</p>

                    <div id="modellist">
                        {Classificationitems}
                    </div>
                    <button className="preprocessbtn btn btn-secondary" onClick={this.handleTrain} >Train Now</button>

                </div >
            );
        }
        else if (this.props.mtype === 'regression') {
            const Regressionitems = []
            const len = this.state.hyperForm.length
            for (let i = 0; i < len; i += 3) {
                let item = []
                for (let j = i; j < i + 3 && j < len; j++) {
                    item.push(
                        this.state.hyperForm[j].type === "Regression" ?
                            <div className="card sec6card manualcard">

                                <div className="card-body manualmodellist">
                                    <span> <input type="checkbox" id={j + "automodel"} value={this.state.hyperForm[j].name} onClick={this.handlehyperselection(j)} name="automodel" />
                                        <label htmlFor="automodel" className="card-model-list"> {this.state.hyperForm[j].name}</label>
                                    </span>

                                    {/* <h4 className="card-title">{this.state.classimodellist[j]}</h4> */}
                                    <div className="manualmodelcard">
                                        {/* <input type="checkbox" id="automodel" value={this.state.classimodellist[j]} onClick={this.handlehyperselection} name="automodel" /> */}
                                        {/* <label htmlFor="automodel" > Select</label> */}
                                        <HyperModal
                                            show={this.state.modalShow}
                                            onHide={() => this.setState({ modalShow: false })}
                                            modelNumber={this.state.currentModel}
                                            mtype={this.props.mtype}
                                            hyperForm={this.state.hyperForm}
                                            handlehyperChange={this.handlehyperChange}
                                        />
                                    </div>
                                </div>
                            </div>
                            : null
                    )
                }
                Regressionitems.push(
                    <div className="card-group  text-center">
                        {item}
                    </div>
                )

            }
            return (
                <div>
                    <div className="autocheckbox">
                        <input type="checkbox" id="automodel" onClick={this.handleAutoModelSelect} name="automodel" />
                        <label htmlFor="automodel"> Auto Models</label>
                    </div>
                    <h1>Models</h1>
                    <p>Preprocessing is being done. Now, select models and their hyperparameters</p>
                    <div id="modellist">
                        {Regressionitems}
                    </div>
                    <button className="preprocessbtn btn btn-secondary" onClick={this.handleTrain}> Train Now</button>

                </div>

            );
        }
        else {
            return (
                <div>
                    <h1>Clustering manual models</h1>
                </div>
            );
        }


    }
}

export default ManualModel;