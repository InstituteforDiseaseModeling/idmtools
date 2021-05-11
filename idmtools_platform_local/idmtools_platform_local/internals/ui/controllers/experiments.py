"""idmtools local platform experiment controller(API).

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import logging
import shutil
import sys
from contextlib import suppress
from typing import Optional, List, Tuple, Dict
import backoff
from flask import current_app
from flask_restful import Resource, reqparse, abort
from sqlalchemy import String, func, or_, and_
from sqlalchemy.exc import ProgrammingError, ResourceClosedError, OperationalError, DatabaseError
from idmtools_platform_local.config import DATA_PATH
from idmtools_platform_local.internals.data.job_status import JobStatus
from idmtools_platform_local.internals.ui.controllers.utils import validate_tags
from idmtools_platform_local.status import Status
from idmtools_platform_local.internals.ui.config import db


logger = logging.getLogger(__name__)


def progress_to_status_str(progress):
    """Convert progress to status."""
    if str(Status.failed) in progress and progress[str(Status.failed)] > 0:
        return 'failed'
    elif str(Status.canceled) in progress and progress[str(Status.canceled)] > 0:
        return 'canceled'
    elif str(Status.in_progress) in progress and progress[str(Status.in_progress)] > 0:
        return 'in_progress'
    elif str(Status.created) in progress and progress[str(Status.created)] > 0:
        return 'created'
    else:
        return 'done'


def handle_backoff_exc(details):
    """Log backoff exceptions to our app logger and restart db connection."""
    current_app.logger.info("Attempting to recover from DB API Error")
    curr_exec = sys.exc_info()[1]
    if isinstance(curr_exec, ProgrammingError):
        from idmtools_platform_local.internals.data import Base
        Base.metadata.create_all(db.get_engine())


@backoff.on_exception(backoff.constant, (ResourceClosedError, ProgrammingError, OperationalError, DatabaseError),
                      max_tries=5, interval=0.2)
def experiment_filter(id: Optional[str], tags: Optional[List[Tuple[str, str]]], page: int = 1, per_page: int = 10) -> \
        Tuple[Dict, int]:
    """
    List the status of experiment(s) with the ability to filter by experiment id and tags.

    Args:
        id (Optional[str]): Optional ID of the experiment you want to filter by
        tags (Optional[List[Tuple[str, str]]]): Optional list of tuples in form of tag_name tag_value to user to filter
            experiments with
        page(int): Which page to load. Defaults to 1
        per_page(int): Experiments per page. Defaults to 50
    """
    session = db.session
    # experiments don't have parents
    criteria = [JobStatus.parent_uuid == None]  # noqa: E711

    # start builder our optional criteria
    if id is not None:
        criteria.append(JobStatus.uuid == id)

    if tags is not None:
        for tag in tags:
            criteria.append((JobStatus.tags[tag[0]].astext.cast(String) == tag[1]))

    query = session.query(JobStatus).filter(*criteria).order_by(JobStatus.uuid.desc()).paginate(page, per_page)
    items = query.items
    total = query.total

    # this will fetch the overall progress of the simulations(sub jobs) for the experiments
    subjob_status_query = session.query(JobStatus.parent_uuid, JobStatus.status,
                                        func.count(JobStatus.status).label("total")) \
        .filter(and_(JobStatus.parent_uuid != None, JobStatus.parent_uuid.in_([i.uuid for i in items])))\
        .group_by(JobStatus.parent_uuid, JobStatus.status)  # noqa: E711

    sdf = subjob_status_query.all()

    # build lookup index
    li = {i.uuid: i for i in items}

    for row in sdf:
        if not hasattr(li[row.parent_uuid], 'progress'):
            li[row.parent_uuid].progress = dict()
        li[row.parent_uuid].progress[str(row.status)] = row.total

    for row in items:
        # experiments without sims will have no progress field
        if hasattr(row, 'progress'):
            row.status = progress_to_status_str(row.progress)
        else:
            row.progress = dict()
            row.status = 'created'
        row.data_path = row.data_path.replace(DATA_PATH, '/data')
    items = list(map(lambda x: x.to_dict(), items))
    return items, total


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
    """Experiment API controller."""
    def get(self, id=None):
        """Get experiment."""
        args = idx_parser.parse_args()
        args['id'] = id

        validate_tags(args['tags'])
        result, total = experiment_filter(**args)
        if id:
            if not result:
                abort(404, message=f"Could not find experiment with id {id}")
            return result[0]

        return result, 200, {'X-Total': total, 'X-Per-Page': args.per_page}

    def delete(self, id):
        """Delete an experiment."""
        args = delete_args.parse_args()
        session = db.session
        job: JobStatus = session.query(JobStatus).filter(JobStatus.uuid == id).first()
        if job is None:
            abort(400, message=f'Error: No experiment with id of {id}')

        if args['data']:
            print(f'Deleting {job.data_path}')
            with suppress(FileNotFoundError):
                shutil.rmtree(job.data_path)
        session.query(JobStatus).filter(or_(JobStatus.uuid == id, JobStatus.parent_uuid == id)).delete()
        return 204, None
