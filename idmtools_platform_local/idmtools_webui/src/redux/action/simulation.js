import {GET_SIMULATIONS, SHOW_ERROR} from "../actionTypes";
import {handleResponse} from "../../utils/utils";
import {showError, showInfo} from "./messaging";



function receiveSimulations(data) {
    return {
        type:GET_SIMULATIONS,
        data
    }

}


export function fetchSimulations() { 

  
    let url = "/api/simulations";
  
    
    return (dispatch) => {
        
        return fetch(url)
            .then(response => {
  
              handleResponse(response,
                (subjects)=>{ /*success handler*/                
                  dispatch(receiveSimulations(subjects))
                },
                (data)=> { /* failure handler */
                  dispatch(showError(data));
                })
  
            });
    };
  }



export function cancelSimulation(id) { 

  
    let url = "/api/simulations/"+id;
  
    
    return (dispatch) => {
        
        return fetch(url, {
                method: 'PUT',
                body:'{"status":"canceled"}',
                headers:{
                    'Content-Type': 'application/json'
                  }
            })
            .then(response => {
  
              handleResponse(response,
                (subjects)=>{ /*success handler*/                
                  dispatch(showInfo("Cancel operation is complete"))
                },
                (data)=> { /* failure handler */
                  dispatch(showError(data));
                })
  
            });
    };
  }