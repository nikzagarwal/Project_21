import React, { Component } from 'react';
import { Modal } from 'react-bootstrap';
import { Button } from 'react-bootstrap';

import axios from 'axios';

class LoginModal extends Component {
    constructor(props) {
        super(props)
        this.state = {
            Username: '',
            Password: '',
        }
    }
    handleUsernameChange = event => {
        this.setState({
            Username: event.target.value
        })
    }
    handlePasswordChange = event => {
        this.setState({
            Password: event.target.value
        })
    }
    handleSubmit = event => {
        let user = this.state.Username
        let pass = this.state.Password
        let data = { user, pass }
        axios.post('https://' + window.address + ':8000/login', JSON.stringify(data))
            .then((res) => {
                console.log("Successful1", res);
                if (res.success = true)
                    this.props.onHide()
                else {
                    window.reload();
                    alert("Wrong credentials trye again");
                }
            },
                (error) => { console.log(error) });
    }

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
                    <Modal.Header >
                        <Modal.Title id="contained-modal-title-vcenter">
                            Login
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <div className="ModalLogin">
                        <form onSubmit={this.handleSubmit}>
                            <div className="createform">
                                <div className="row">
                                    <div className="col-40">
                                        <label htmlFor="username">Enter Username  </label>
                                    </div>
                                    <div className="col-60">

                                        <input type="text" id="username" name="username" placeholder="enter username..." value={this.state.Username} onChange={this.handleUsernameChange} required />
                                    </div>
                                </div>
                                <div className="row">
                                    <div className="col-40">
                                        <label htmlFor="password">Enter Password  </label>
                                    </div>
                                    <div className="col-60">

                                        <input type="password" id="password" name="password" placeholder="Enter password..." value={this.state.Password} onChange={this.handlePasswordChange} required />
                                    </div>
                                </div>


                                <div>
                                    <button type="submit" className="btn btn-secondary" id="startengine" >Login</button>
                                </div>
                            </div>
                        </form>
                        </div>
                    </Modal.Body>
                    {/* <Modal.Footer>
                        <Button onClick={this.props.onHide}>Close</Button>
                    </Modal.Footer> */}
                </Modal>
            </div>
        );
    }
}

export default LoginModal;