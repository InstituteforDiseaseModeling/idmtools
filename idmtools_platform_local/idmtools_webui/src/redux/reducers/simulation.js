import {GET_SIMULATIONS, SET_SIMULATION_FILTER} from "../actionTypes";

const initialState = {

    simulations:[],
    start:null,
    end:null

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
            }
        default:
            return state;
    }

}