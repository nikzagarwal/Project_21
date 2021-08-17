import React, { Component } from 'react';

class Section1 extends Component {
    render() {
        return (
            <div className="section1">
                <div className="container typing-text">
                    <p>Curl Brings <span className="typed-text"></span><span className="cursor">&nbsp;</span></p>
                    <p>Together under one Umbrella</p>
                    <div className="section1text1">Auto Ml has the power to simplify artificial intelligence usage for people who are not into coding but still want to experience the magic of AI</div>
                    <div className="sec1btn-group">
                        <a href='#section2'> <button className="  btn  section1button section1button2">Start Expereince </button></a>
                        <a href='#section3'> <button className=" btn btn-primary section1button section1button2 ">View Demo </button></a>
                    </div>
                </div>
               
            </div>
        );
    }
}

export default Section1;