import {GET_EXPERIMENTS, SET_EXPERIMENT_FILTER} from "../actionTypes";

const initialState = {

    experiments:[],
    start:null,
    end:null

};


export function experiments(state=initialState, action) {


    switch(action.type) {
        case GET_EXPERIMENTS:
            return {...state, 
              experiments: action.data};
        case SET_EXPERIMENT_FILTER:
            return {...state,
                start: action.start, 
                end:action.end
            }
        default:
            return state;
    }

}