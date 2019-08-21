import {GET_SIMULATIONS} from "../actionTypes";

const initialState = {

    

};


export function simulations(state=initialState, action) {


    switch(action.type) {
        case GET_SIMULATIONS:
            return {...state, 
                simulations: action.data};
        default:
            return state;
    }

}