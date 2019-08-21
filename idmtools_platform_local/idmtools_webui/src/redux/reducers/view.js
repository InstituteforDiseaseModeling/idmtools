import {DASHBOARD_VIEW, 
    EXPERIMENT_VIEW, 
    SIMULATION_VIEW,
  } from "../actionTypes";
  
  const initialState = {
    selectedView: "DASHBOARD",
    selectedTitle: "Dashboard"
  }
  
  export function changeView(state=initialState,action) {
  
    switch (action.type) {
      case DASHBOARD_VIEW:
        return {...state, selectedView:action.type, selectedTitle: action.title};
      case EXPERIMENT_VIEW:
        return {...state, selectedView:action.type, selectedTitle: action.title}
      case SIMULATION_VIEW:
        return {...state, selectedView:action.type, selectedTitle: action.title}
      
      default:
        return state;
    }
  
  }
  