import { createSelector } from 'reselect';
import * as _ from "lodash";

const startDate = state => state.start;
const endDate = state => state.end;
const experiments = state => state.experiments;

 /**
 * Returns only the experiments satisfying the filters
 */
export const getExperimentsByFilter = createSelector(
    [experiments, startDate, endDate],
    (experiments, start, end) => {

        var result =  _.compact(experiments.map(exp => {

            let created = new Date(exp.created);
            if (created <= end && created >= start)            
                return exp;
            else 
                return null;
        }));

        if (start && end)

            return result;
        else 
            return experiments
    }
);
