import { SHOW_WARNING, SHOW_INFO, SHOW_ERROR, SHOW_STOP, SHOW_SUCCESS } from "../actionTypes";
import {isJson} from "../../utils/utils"

export function showError(data) {

  const genericError = "EasyVA is unavailable at the moment. Pls try again later."
  let msg;

  if (!isJson(data)) {
    msg = data;
  }
  else {
    let jsonData = JSON.parse(data)
    if (jsonData && jsonData.message) {
      if (jsonData.message  == "Unexpected token E in JSON at position 0") 
        msg = genericError;
      else 
        msg = jsonData.message;    
    }
    else if (jsonData.messages) {
      msg = JSON.stringify(jsonData.messages)
    }
  }

  return {
    type: SHOW_ERROR,
    variant:"error",
    msg,
    open: true
  }
}

export function showInfo(msg) {
  return {
    type: SHOW_INFO,
    variant:"info",
    msg,
    open: true
  }
}

export function showWarning(msg) {
  return {
    type: SHOW_WARNING,
    variant:"warning",
    msg,
    open: true
  }
}

export function showStop() {
  return {
    type: SHOW_STOP,
    variant: "",
    open: false
  }
}


export function showSuccess(msg) {
  return {
    type: SHOW_SUCCESS,
    msg,
    variant: "success",
    open: true
  }
}
