

import {GET_EXPERIMENTS, SHOW_ERROR} from "../actionTypes";
import {showError, handleResponse} from "../../utils/utils";


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