import {GET_SIMULATIONS, SHOW_ERROR} from "../actionTypes";
import {showError, handleResponse} from "../../utils/utils";



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