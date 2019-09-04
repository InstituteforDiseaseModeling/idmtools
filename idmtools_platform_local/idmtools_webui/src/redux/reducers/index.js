import { combineReducers } from "redux";
import {simulations} from "./simulation";
import {experiments} from "./experiment";

import {changeView} from "./view";
import {showMsg} from "./messaging";




export default combineReducers({simulations, experiments, changeView,showMsg});
