import { HashRouter, Route } from "react-router-dom";
import {connect} from "react-redux";  

import React, {Component} from "react";
import {DASHBOARD_VIEW, EXPERIMENT_VIEW, SIMULATION_VIEW} from "../../redux/actionTypes";


class RouterContainer extends Component {

    constructor(props) {
        super(props);
        this.renderContent = this.renderContent.bind(this);
    }


    renderContent(view, title) {

        return( ()=> {
            this.props.dispatch( {
                type: view,
                title: title
            });

            return (
                this.props.children
            );
        });
    }

    render() {
        return (
          <HashRouter>
           <article style={{height:'100%'}}>
             <Route path="/" render={this.renderContent(DASHBOARD_VIEW, 'Dashboard')} />
             <Route path="/dashboard" render={this.renderContent(DASHBOARD_VIEW, 'Dashboard')} />
             <Route path="/experiment" render={this.renderContent(EXPERIMENT_VIEW, 'Experiment')} />
             <Route path="/simulation" render={this.renderContent(SIMULATION_VIEW, 'Simulation')} />
           </article>
         </HashRouter>
        )
      }
}

export default connect()(RouterContainer);
