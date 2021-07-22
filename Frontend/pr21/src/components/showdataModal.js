import React, { Component } from 'react';
import { Modal } from 'react-bootstrap';
import { Button } from 'react-bootstrap';

class ShowdataModal extends Component {
    render() {
        const rawdata = Object.values(this.props.rawdata);
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
                            Data Sample
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        {rawdata.map((data, i) => (
                            i === 1 ? (
                                <div className="preprocesstable " id="preprocesstable">
                                    <table>
                                        <thead>
                                            <tr>
                                                {Object.keys(data).map((key, i) =>
                                                    <th>{key}</th>
                                                )}
                                            </tr>
                                        </thead>
                                        {rawdata.map((data, i) => (
                                            i < 5 ? (

                                                <tbody>
                                                    <tr>
                                                        {Object.keys(data).map((key) =>
                                                            <td>
                                                                {data[key]}

                                                            </td>)}

                                                    </tr>

                                                </tbody>) : null))}
                                    </table>
                                </div>) : null))}

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