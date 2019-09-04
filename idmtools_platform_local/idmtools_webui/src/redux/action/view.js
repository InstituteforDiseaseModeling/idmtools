import {DASHBOARD_VIEW, 
    EXPERIMENT_VIEW, 
    SIMULATION_VIEW,
  } from "../actionTypes";
  
  
  export function dashboardView(){
  
    return (dispatch) => {
  
      dispatch(  {
        type: DASHBOARD_VIEW,
        title: "Dashboard"
      });
    }
  }

  export function simulationView(){
  
    return (dispatch) => {
  
      dispatch(  {
        type: SIMULATION_VIEW,
        title: "Simulation"
      });
    }
  }

  export function experimentView(){
  
    return (dispatch) => {
  
      dispatch(  {
        type: EXPERIMENT_VIEW,
        title: "Experiment"
      });
    }
  }