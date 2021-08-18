import React from 'react';
class Metrics extends React.Component {


    render() {
        if (this.props.data === "a")
            return (
                <div>

                    <div className="centered spinner-location">
                        <div className="spinner-border text-dark spinner-border-lg" role="status">
                            <span className="loadertext">Loading...</span>
                        </div>
                    </div>
                </div>
            );

        else {
            const metricdata = Object.values(this.props.data);
            const dicReg = ["Top models", "Name of Model", "Mean Absolute error", "Mean Square error", "Root mean square error", "R2 Score, 1 being best", "Root mean square logarathmic error"]
            const dicClassi = ["Top models", "Name of Model","Accuracy of model", "Area under the Roc Curve", "True positive/ (True positive+False negative)", "True positive/ (True positive+False positive)", "2*Precision*Recall/(Precision+Recall)"]
            
            if (this.props.mtype !== "clustering") {
                return (
                    <div>
                        {metricdata.map((data, i) => (
                            i === 0 ? (
                                <div className="metricstable " >
                                    <table>
                                        <thead>
                                            <tr>
                                                {Object.keys(data).map((key, i) =>
                                                    i < 7 ? (
                                                        <th>{key}
                                                            {this.props.mtype === "regression" ?
                                                                <span className="ibtn"> i <span id="idesc">{dicReg[i]}</span></span>
                                                                : 
                                                                <span className="ibtn"> i <span id="idesc">{dicClassi[i]}</span></span>
                                                            }
                                                        </th>) : null
                                                )}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {metricdata.map((data, i) => (
                                                (i < 3 && i< Object.keys(metricdata).length-1) ? (


                                                    <tr>
                                                        {Object.keys(data).map((key, j) =>
                                                            j < 7 ? (
                                                                j === 0 ?
                                                                    <td>{i + 1}</td> :
                                                                    <td>{data[key]}</td>
                                                            ) : null
                                                        )}

                                                    </tr>

                                                ) : null))}
                                        </tbody>
                                    </table>
                                </div>) : null))}

                        {/* {data.map((data, i) => (
                            i === 0 ?

                                (<div className="metricstable">

                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Model</th>
                                                <th>{data.Model}</th>
                                            </tr>
                                        </thead>
                                        <tbody>

                                            {Object.keys(data).map((key, i) => (

                                                (i > 1) ? (

                                                    < tr >
                                                        <td>{key}</td>
                                                        <td className="metricValue">   {data[key]}</td>
                                                    </tr>
                                                ) : null))}


                                        </tbody>

                                    </table>
                                </div>) : null
                        ))
                        } */}
                    </div>
                );
            }
            else {
                return (
                    <div>
                        <div >
                            {metricdata.map((data2, i) => (
                                i === 0 ?

                                    (<div className="metricstable clustertable">

                                        <table>
                                            <thead>
                                                < tr >
                                                    {Object.keys(data2).map((key, i) => (
                                                        i > 0 ?
                                                            <th> {key}</th> : null
                                                    ))}
                                                </tr>
                                            </thead>
                                            <tbody>

                                                {metricdata.map((key, i) => (

                                                    (i < 5) ? (

                                                        < tr >
                                                            {Object.keys(data2).map((key, i) => (
                                                                i > 0 ?
                                                                    <td>   {data2[key]}</td> : null
                                                            ))}
                                                        </tr>
                                                    ) : null))}


                                            </tbody>

                                        </table>
                                    </div>) : null
                            ))
                            }
                        </div>
                        <br /><br />
                        <h4 className="metricsNote">Note: Every row in dataset is alloted clusters and full list can be downloaded </h4>
                    </div>
                );
            }
        }
    }
}

export default Metrics;