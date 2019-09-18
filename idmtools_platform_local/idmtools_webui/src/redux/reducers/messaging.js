import { SHOW_WARNING, SHOW_INFO, SHOW_ERROR, SHOW_STOP, SHOW_SUCCESS } from "../actionTypes";

export function showMsg( state = {infoMsg:'',open:false, variant:""}, action) {


  switch(action.type) {
    case SHOW_WARNING:
      return {...state, msg: action.msg, open:action.open, variant: action.variant};
    case SHOW_ERROR:
      return {...state, msg: action.msg, open:action.open, variant: action.variant};
    case SHOW_INFO:
      return {...state, msg: action.msg, open:action.open, variant: action.variant};
    case SHOW_STOP:
      return {...state, msg: '', open:action.open};
    case SHOW_SUCCESS:
      return {...state, msg: action.msg, open:action.open, variant: action.variant};
    default:
      return state;

  }
}
