import {GET_EXPERIMENTS} from "../actionTypes";

const initialState = {

    

};


export function experiments(state=initialState, action) {


    switch(action.type) {
        case GET_EXPERIMENTS:
            return {...state, 
              experiments: action.data};
        default:
            return state;
    }

}