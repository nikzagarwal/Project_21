import React, { Component } from 'react';
import { Modal } from 'react-bootstrap';
import { Button } from 'react-bootstrap';
class HyperModal extends Component {
    constructor(props) {
        super(props)
        this.state = {
            hyperForm: "",
        }
    }
    static getDerivedStateFromProps(nextProps, prevState) {
        // if (prevState.hyperForm === "") {
            return { hyperForm: Object.values(nextProps)[4] };
        // }

        return null;
    }
    handleHyperChange = (val) => event => {
        console.log(this.state.hyperForm)
        this.setState(prevState => ({

            hyperForm: Object.values({
                ...prevState.hyperForm,
                [this.props.modelNumber]: {
                    ...prevState.hyperForm[this.props.modelNumber],
                    "isSelected": true,
                    "hyper":
                        Object.values({
                            ...prevState.hyperForm[this.props.modelNumber].hyper,
                            [val]: {
                                ...prevState.hyperForm[this.props.modelNumber].hyper[val],
                                "ischanged": true,
                                "value": event.target.value
                            }
                        })
                }
            })
        }), () => {
            this.props.handlehyperChange(this.state.hyperForm)
        });





    }

    render() {
        // console.log(this.state.hyperForm)
        let model = ""
        const display = []


        if (this.props.show === true) {
            model = this.props.modelNumber
            // console.log(model)
            // console.log(this.state.hyperForm[model])
            const items = this.state.hyperForm[model].hyper
            // console.log(items)
            for (let i = 0; i < items.length; i++) {
                display.push(

                    <div className="row">
                        <div className="col-40">
                            <label htmlFor="outlier">{items[i]["name"]}</label>
                        </div>
                        {(() => {
                            switch (items[i].type) {
                                case 'int':
                                    return (
                                        < div className="col-60" >
                                            <input type="number" id={i + "hyper"} name={i + "hyper"} onChange={this.handleHyperChange(i)} placeholder="Enter Integervalue" required />
                                        </div>
                                    );
                                case 'float':
                                    return (
                                        < div className="col-60" >
                                            <input type="number" id={i + "hyper"} name={i + "hyper"} onChange={this.handleHyperChange(i)} placeholder="Enter Float value" required />
                                        </div>
                                    );
                                case 'bool':
                                    return (
                                        < div className="col-60" >
                                            <select name={i + "hyper"} id={i + "hyper"} onChange={this.handleHyperChange(i)}>
                                                <option value="false">False</option>
                                                <option value="true">True</option>
                                            </select>
                                        </div>
                                    );
                                case 'option':
                                    return (
                                        < div className="col-60" >
                                            <select name={i + "hyper"} id={i + "hyper"} onChange={this.handleHyperChange(i)}>
                                                {items[i].options.map((key) =>
                                                    <option value={key}>{key}</option>
                                                )}
                                            </select>
                                        </div>
                                    );
                                default:
                                    return null;
                            }
                        })()}

                        {/* <div className="col-60" >
                            <input type="text" id="name" name="name" onChange={this.handleNameChange} placeholder="Enter Value" required />
                        </div> */}
                    </div >


                )
            }

        }
        return (
            <div>
                <Modal
                    {...this.props}
                    size="lg"
                    aria-labelledby="contained-modal-title-vcenter"
                    centered

                >
                    <Modal.Header closeButton>
                        <Modal.Title id="contained-modal-title-vcenter">
                            {this.props.show === true ?
                                this.state.hyperForm[model].name :
                                null}
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <p>Give values to hyperparameters or leave blank for default </p>
                        {display}

                    </Modal.Body>
                    <Modal.Footer>
                        <Button onClick={this.props.onHide}>Done</Button>
                    </Modal.Footer>
                </Modal>

            </div>
        );
    }
}

export default HyperModal;