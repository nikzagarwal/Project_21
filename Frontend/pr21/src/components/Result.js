import React, { Component } from 'react';
import Section6 from './section6.js';
import Section5 from './section5.js';
import $ from 'jquery';
class Result extends Component {
    constructor(props) {
        super(props)
        this.state = {
            log1: [],
            log2: [],
            log3: [],
            log4: [],
            log5: [],
        }
    }
    OpenWebSocket =event=>{
        var theFormItself = document.getElementById('logbtn');
            $(theFormItself).hide();
            var theFormItself2 = document.getElementById('log');
            $(theFormItself2).show();
        const ws = new WebSocket("ws://localhost:8000/websocketStream")
            ws.onopen = () => {
                console.log("open")
            }
            ws.onmessage = evt => {

                this.setState({
                    log1: this.state.log2,
                    log2: this.state.log3,
                    log3: this.state.log4,
                    log4: this.state.log5,
                    log5: Object.values(Object.values(evt.data))
                })
                // console.log(evt.data)
            }
            ws.onclose = () => {
                console.log("closing socket connection =" + this.state.counter)
                
                ws.close();
            }
    }
    render() {
        if (this.props.projectdetail["Successful"] === "False") {
            // if (this.props.openWebSocketConnection === true) {
            //     this.OpenWebSocket()
            // }
            return (
                <div className="container loader" id="loader">
                    <p>" Your models are been created... Can we take a quick Tea Break ?? "</p>
                    <div className="centered spinner-location">
                        <div className="spinner-border text-dark spinner-border-lg" role="status">
                            <span className="loadertext">Loading...</span>
                        </div>
                    </div>
                    <br />
                    <div className="terminal" id="terminal">
                        <div id= "logbtn" >
                        <button className="btn btn-primary logbtn" onClick={this.OpenWebSocket}>See logs</button>
                        </div>
                        <div id="log">
                            {this.state.log1}<br />
                            {this.state.log2}<br />
                            {this.state.log3}<br />
                            {this.state.log4}<br />
                            {this.state.log5}<br />
                        </div>

                    </div>

                </div>
            );
        }
        else {
            return (
                <div>
                    <Section6
                        modelnum={this.props.modelnum}
                        handler={this.props.handler}
                        projectname={this.props.projectname}
                        isauto={this.props.isauto} />
                    <Section5
                        currentmodel={this.props.currentmodel}
                        projectdetails={this.props.projectdetail}
                        mtype={this.props.mtype}
                        isauto={this.props.isauto} />
                </div>
            );
        }
    }
}

export default Result;