import logging
import shutil
from typing import Optional, List, Tuple

import pandas as pd
from flask import current_app
from flask_restful import Resource, reqparse, abort
from sqlalchemy import String, func, or_

from idmtools_platform_local.config import DATA_PATH
from idmtools_platform_local.workers.data.job_status import JobStatus
from idmtools_platform_local.workers.database import get_session
from idmtools_platform_local.workers.ui.controllers.utils import validate_tags

logger = logging.getLogger(__name__)


def experiment_filter(id: Optional[str], tags: Optional[List[Tuple[str, str]]], page:int = 1, per_page:int = 10) -> pd.DataFrame:
    """
    List the status of experiment(s) with the ability to filter by experiment id and tags

    Args:
        id (Optional[str]): Optional ID of the experiment you want to filter by
        tags (Optional[List[Tuple[str, str]]]): Optional list of tuples in form of tag_name tag_value to user to filter
            experiments with
    """
    session = get_session()
    try:
        # experiments don't have parents
        criteria = [JobStatus.parent_uuid == None]  # noqa: E711

        # start builder our optional criteria
        if id is not None:
            criteria.append(JobStatus.uuid == id)

        if tags is not None:
            for tag in tags:
                criteria.append((JobStatus.tags[tag[0]].astext.cast(String) == tag[1]))

        query = session.query(JobStatus).filter(*criteria).order_by(JobStatus.uuid.desc()).paginate(page, per_page)

        # Pull our experiment status into a dataframe
        df = pd.read_sql(query.statement, query.session.bind, columns=['uuid', 'status', 'data_path', 'tags'])

        # this will fetch the overall progress of the simulations(sub jobs) for the experiments
        subjob_status_query = session.query(JobStatus.parent_uuid, JobStatus.status,
                                            func.count(JobStatus.status).label("total")) \
            .filter(JobStatus.parent_uuid != None).group_by(JobStatus.parent_uuid, JobStatus.status)  # noqa: E711

        sdf = pd.read_sql(subjob_status_query.statement, subjob_status_query.session.bind, index_col=['parent_uuid'])

        # There may be a better way to do this merge of data. For now the loop works
        # basically we are building the progress bar for each experiment based on the simulation statuses
        df['progress'] = ''
        for index, row in df.iterrows():
            job = row['uuid']
            status_bars = []
            job_status = dict()
            if job in sdf.index.values:
                job_list = sdf.loc[job]
                # since we index by parent_uuid, if could have multiple rows. This is the general case(most experiments will
                # have simulations is different statuses at some point) so we convert any results that are a single row
                # from their series form to the transposed dataframe that we get in the general case
                if type(job_list) is pd.Series:
                    job_list = job_list.to_frame().transpose()
                # now build our status object
                for sidx, srow in job_list.iterrows():
                    job_status[str(srow['status'])] = int(srow['total'])
                # and make a pretty progress bar

                status_bars.append(job_status)
                # status_bars.append(parent_status_to_progress(job_status))
            # convert list to dict
            sb_dict = {}
            [sb_dict.update(v) for v in status_bars]
            df.at[index, 'progress'] = status_bars

        df['data_path'] = df['data_path'].apply(lambda x: x.replace(DATA_PATH, '/data'))
        # df['data_path'] = df['data_path'].apply(urlize_data_path)

        # we don't need status or parent_uuid or status(now that we have progress bars) for experiments. Let's drop those
        df.drop(columns=['parent_uuid', 'status'], inplace=True)
        # and let's rename columns to make it more clear fo user what they are looking at
        df.rename(index=str, columns=dict(uuid='experiment_id'), inplace=True)
        df['created'] = df['created'].astype(str)
        df['updated'] = df['updated'].astype(str)
    except Exception as e:
        logger.exception(e)
        raise e
    finally:
        session.close()
    return df


idx_parser = reqparse.RequestParser()
idx_parser.add_argument('tags', action='append', default=None,
                        help="Tags tio filter by. Tags must be in format name,value")
idx_parser.add_argument('page', type=int, default=1, help="Page")
idx_parser.add_argument('per_page', type=int, default=10, help="Per Page")
delete_args = reqparse.RequestParser()
delete_args.add_argument('data', help='Should the data for the experiment and all simulations be deleted as well?',
                         type=bool,
                         default=False)


class Experiments(Resource):
    def get(self, id=None):
        args = idx_parser.parse_args()
        args['id'] = id

        validate_tags(args['tags'])
        df = experiment_filter(**args)
        current_app.logger.error(df.head())
        result = df.to_dict(orient='records')
        if id:
            if not result:
                abort(404, message=f"Could not find experiment with id {id}")
            return result[0]
        return result

    def delete(self, id):
        args = delete_args.parse_args()
        session = get_session()
        try:
            job: JobStatus = session.query(JobStatus).filter(JobStatus.uuid == id).first()
            if job is None:
                abort(400, message=f'Error: No experiment with id of {id}')

            if args['data']:
                print(f'Deleting {job.data_path}')
                try:
                    shutil.rmtree(job.data_path)
                except FileNotFoundError:
                    # we will assume it has been cleaned up manually
                    pass
            session.query(JobStatus).filter(or_(JobStatus.uuid == id, JobStatus.parent_uuid == id)).delete()
            session.commit()
        finally:
            session.close()
        return 204, None
