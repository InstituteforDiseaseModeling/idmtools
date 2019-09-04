import {GET_SIMULATIONS, SET_SIMULATION_FILTER, LOADING_SIMULATION} from "../actionTypes";

const initialState = {

    simulations:[],
    start:null,
    end:null,
    loading:true

};


export function simulations(state=initialState, action) {


    switch(action.type) {
        case GET_SIMULATIONS:
            return {...state, 
                simulations: action.data};
        case SET_SIMULATION_FILTER:
            return {...state,
                start: action.start, 
                end:action.end
            };
        case LOADING_SIMULATION:
            return {...state,
                loading: action.loading         
            };
        
        default:
            return state;
    }

}