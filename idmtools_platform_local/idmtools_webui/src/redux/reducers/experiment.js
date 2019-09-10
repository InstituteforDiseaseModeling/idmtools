import {GET_EXPERIMENTS, SET_EXPERIMENT_FILTER, LOADING_EXPERIMENTS} from "../actionTypes";

const initialState = {

    experiments:[],
    start:null,
    end:null,
    loading:true

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
            };
        case LOADING_EXPERIMENTS:
            return {...state,
                loading: action.loading         
            };

        default:
            return state;
    }

}