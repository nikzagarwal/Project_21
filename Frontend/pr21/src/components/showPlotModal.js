import React, { Component } from 'react';
import { Modal } from 'react-bootstrap';
import { Button } from 'react-bootstrap';

class ShowdataModal extends Component {
    render() {
        const plotdata = this.props.plot
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
                            Eda Plots
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        {
                            plotdata === "" ?
                                <div>

                                    <div className="centered spinner-location">
                                        <div className="spinner-border text-dark spinner-border-lg" role="status">
                                            <span className="loadertext">Loading...</span>
                                        </div>
                                    </div>
                                </div> 
                                :
                                <div>

                                    <iframe title="Plot" srcDoc={plotdata} width="1080" height="540">hi</iframe>
                                </div>
                        }

                    </Modal.Body>
                    <Modal.Footer>
                        <Button onClick={this.props.onHide}>Close</Button>
                    </Modal.Footer>
                </Modal>
            </div>
        );
    }
}

export default ShowdataModal;