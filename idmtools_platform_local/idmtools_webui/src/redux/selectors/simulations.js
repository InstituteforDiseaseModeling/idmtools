import { createSelector } from 'reselect';
import * as _ from "lodash";

const startDate = state => state.start;
const endDate = state => state.end;
const simulations = state => state.simulations;

 /**
 * Returns only the simulations satisfying the filters
 */
export const getSimulationsByFilter = createSelector(
    [simulations, startDate, endDate],
    (simulations, start, end) => {

        var result =  _.compact(simulations.map(sim => {

            let created = new Date(sim.created);
            if (created <= end && created >= start)            
                return sim;
            else 
                return null;
        }));

        if (start && end)

        
            return result;
        else 
            return simulations
    }
);
