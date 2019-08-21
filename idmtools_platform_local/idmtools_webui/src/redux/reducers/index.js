import { combineReducers } from "redux";
import {simulations} from "./simulation";
import {experiments} from "./experiment";

import {changeView} from "./view";



export default combineReducers({simulations, experiments, changeView});
