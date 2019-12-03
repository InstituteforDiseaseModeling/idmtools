
import moment from "moment";



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