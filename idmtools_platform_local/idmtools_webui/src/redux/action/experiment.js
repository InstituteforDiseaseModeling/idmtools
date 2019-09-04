

import {GET_EXPERIMENTS, SET_EXPERIMENT_FILTER, LOADING_EXPERIMENTS} from "../actionTypes";
import {handleResponse} from "../../utils/utils";
import {showError, showInfo} from "./messaging";


function receiveExperiments(data) {
    return {
        type:GET_EXPERIMENTS,
        data
    }

}

export function loading(loading) {
  return {
    type:LOADING_EXPERIMENTS,
    loading
  }
}

export function fetchExperiments() { 

  
    let url = "/api/experiments";
  
    
    
    return (dispatch) => {

      dispatch(loading(true));
        
        return fetch(url)
            .then(response => {
  
              handleResponse(response,
                (subjects)=>{ /*success handler*/                
                  dispatch(receiveExperiments(subjects))
                  dispatch(loading(false));
                },
                (data)=> { /* failure handler */
                  dispatch(showError(data));
                  dispatch(loading(false));
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


  export function setFilter(start, end) {
    return {
      type: SET_EXPERIMENT_FILTER,
      start, end
    }
  }