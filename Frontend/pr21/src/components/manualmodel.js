import React, { Component } from 'react';
import HyperModal from './hypermodal.js';
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
            this.setState(prevState => ({

                hyperForm: Object.values({
                    ...prevState.hyperForm,
                    [val]: {
                        ...prevState.hyperForm[val],
                        "isSelected": true
                    }
                }),


            }
            ))
            // this.setState({ modalShow: true })
            // this.setState({ currentModel: event.target.value })
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
                                            modelName={this.state.currentModel}
                                            mtype={this.props.mtype}
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
                    <div id="modellist">
                        {Classificationitems}
                    </div>
                    <button className="preprocessbtn" onClick={this.handleTraining} >Train Now</button>

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
                        this.state.hyperForm[j].type === "Classification" ?
                            <div className="card sec6card manualcard">

                                <div className="card-body manualmodellist">
                                    <span> <input type="checkbox" id={i + "automodel"} value={this.state.hyperForm[j].name} onClick={this.handlehyperselection} name="automodel" />
                                        <label htmlFor="automodel" className="card-model-list"> {this.state.hyperForm[j].name}</label>
                                    </span>

                                    {/* <h4 className="card-title">{this.state.classimodellist[j]}</h4> */}
                                    <div className="manualmodelcard">
                                        {/* <input type="checkbox" id="automodel" value={this.state.classimodellist[j]} onClick={this.handlehyperselection} name="automodel" /> */}
                                        {/* <label htmlFor="automodel" > Select</label> */}
                                        <HyperModal
                                            show={this.state.modalShow}
                                            onHide={() => this.setState({ modalShow: false })}
                                            modelName={this.state.currentModel}
                                            mtype={this.props.mtype}
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