import {SHOW_ERROR} from '../redux/actionTypes'
import moment from "moment";


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

  export function formatDateString (dateStr) {
    if (!dateStr) return "";
  
    return moment(dateStr).format("YYYY-MM-DD HH:mm:ss");
  }


  //for handling http response
export function handleResponse(response, successHandler, failHandler) {

    if (response.ok) {
      return response.json() 
      .then (data => {
        successHandler(data);
      })
    } else {
      return response.text()
      .then (data => {
        failHandler(data);
      })
    }
  }

export function isJson(str) {
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
  }