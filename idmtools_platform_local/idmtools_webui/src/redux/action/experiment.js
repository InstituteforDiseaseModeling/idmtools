

import {GET_EXPERIMENTS, SHOW_ERROR} from "../actionTypes";
import {handleResponse} from "../../utils/utils";
import {showError, showInfo} from "./messaging";


function receiveExperiments(data) {
    return {
        type:GET_EXPERIMENTS,
        data
    }

}


export function fetchExperiments() { 

  
    let url = "/api/experiments";
  
    
    return (dispatch) => {
        
        return fetch(url)
            .then(response => {
  
              handleResponse(response,
                (subjects)=>{ /*success handler*/                
                  dispatch(receiveExperiments(subjects))
                },
                (data)=> { /* failure handler */
                  dispatch(showError(data));
                })
  
            });
    };
  }

  export function deleteExperiment(id) { 

  
    let url = "/api/experiments/"+id;

    
    return (dispatch) => {
        
        return fetch(url, {
                method: 'DELETE',

                // headers:{
                //     'Content-Type': 'application/json'
                //   }
            })
            .then(response => {
  
              handleResponse(response,
                (subjects)=>{ /*success handler*/                
                  
                  dispatch(showInfo("Delete operation is complete"))
                  dispatch(fetchExperiments());
                },
                (data)=> { /* failure handler */
                  dispatch(showError(data));
                })
  
            });
    };
  }