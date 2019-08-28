import { createSelector } from 'reselect';
import * as _ from "lodash";

const startDate = state => state.start;
const endDate = state => state.end;
const simulations = state => state.simulations;

// export const getSelectedSubjectId = createSelector(
//     [getSelectedSubjectId, getSubjects],
//     (id, subjects) => {
//         return id;  //_.find(subjects, {"sid":id});
//     }
// );

 /**
 * Returns only the subjects satisfying the filters
 */
export const getSimulationsByFilter = createSelector(
    [simulations, startDate, endDate],
    (simulations, start, end) => {

        var result =  _.compact(simulations.map(sim => {

            let created = new Date(sim.created);
            if (created <= end && created >= start)
            //todo: if (filters.showOnlyConsensus & ...
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
