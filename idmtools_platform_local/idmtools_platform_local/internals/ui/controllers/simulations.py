"""idmtools local platform simulations controller(API).

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import logging
import signal
import os
from typing import Optional, List, Tuple, Dict

import backoff
import docker
from flask import request, current_app
from flask_restful import Resource, reqparse, abort
from sqlalchemy import String
from sqlalchemy.exc import ResourceClosedError, ProgrammingError, OperationalError, DatabaseError

from idmtools_platform_local.internals.data.job_status import JobStatus
from idmtools_platform_local.internals.ui.controllers.utils import validate_tags
from idmtools_platform_local.status import Status
from idmtools_platform_local.internals.ui.config import db

logger = logging.getLogger(__name__)


@backoff.on_exception(backoff.constant, (ResourceClosedError, ProgrammingError, OperationalError, DatabaseError),
                      max_tries=5, interval=0.2)
def sim_status(simulation_id: Optional[str], experiment_id: Optional[str], status: Optional[str],
               tags: Optional[List[Tuple[str, str]]], page: int = 1, per_page: int = 20) -> Tuple[Dict, int]:
    """
    List of statuses for simulation(s) with the ability to filter by id, experiment_id, status, and tags.

    Args:
        simulation_id (Optional[str]): Optional Id of simulation
        experiment_id (Optional[str]): Optional experiment id
        status (Optional[str]): Optional status string to filter by
        tags (Optional[List[Tuple[str, str]]]): Optional list of tuples in form of tag_name tag_value to user to filter
            experiments with
        page(int): Which page to load. Defaults to 1
        per_page(int): Simulations per page. Defaults to 50
    Returns:
        None
    """
    session = db.session
    # Simulations ALWAYS have a parent
    criteria = [JobStatus.parent_uuid != None]  # noqa: E711

    # start building our filter criteria
    if simulation_id is not None:
        criteria.append(JobStatus.uuid == simulation_id)

    if experiment_id is not None:
        criteria.append(JobStatus.parent_uuid == experiment_id)

    if status is not None:
        criteria.append(JobStatus.status == Status[status])

    if tags is not None:
        for tag in tags:
            criteria.append((JobStatus.tags[tag[0]].astext.cast(String) == tag[1]))

    query = session.query(JobStatus).filter(*criteria).order_by(JobStatus.uuid.desc(), JobStatus.parent_uuid.desc()).paginate(page, per_page)
    total = query.total
    items = list(map(lambda x: x.to_dict(False), query.items))
    return items, total


status_strs = [str(status) for status in Status]
idx_parser = reqparse.RequestParser()
idx_parser.add_argument('experiment_id', help='Experiment ID', default=None)
idx_parser.add_argument('status', help='Status to filter by. Should be one of the following '
                                       '{}'.format(','.join(status_strs)),
                        choices=status_strs,
                        default=None)
idx_parser.add_argument('page', type=int, default=1, help="Page")
idx_parser.add_argument('per_page', type=int, default=20, help="Per Page")
idx_parser.add_argument('tags', action='append', default=None, help="Tags to filter by. Tags must be in format name,value")


class Simulations(Resource):
    """Simulation API controller."""
    def get(self, id=None):
        """Get simulation."""
        args = idx_parser.parse_args()
        args['simulation_id'] = id

        validate_tags(args['tags'])

        result, total = sim_status(**args)

        if id:
            if not result:
                abort(404, message=f"Could not find simulation with id {id}")
            return result[0]
        return result, 200, {'X-Total': total, 'X-Per-Page': args.per_page}

    def put(self, id):
        """Update simulation."""
        data = request.json
        # at moment, only allow status to be updated(ie canceled'
        # later, we may support resuming but we will need to include more data in the db to do this
        data = {k: v for k, v in data.items() if k == 'status' and v in ['canceled']}
        if 'status' in data:
            s = db.session
            current_job: JobStatus = s.query(JobStatus).filter(JobStatus.uuid == id).first()
            # check if we have a PID, if so kill it
            current_app.logger.info(f"Getting metadata for {id}")
            current_app.logger.debug(str(current_job.extra_details))
            if current_job.extra_details is not None:
                if 'pid' in current_job.extra_details:
                    try:
                        current_app.logger.info(f"Killing process for {current_job.extra_details['pid']} for {id}")
                        os.kill(current_job.extra_details['pid'], signal.SIGKILL)
                    except Exception as e:
                        current_app.logger.error('Could not kill procress')
                        current_app.logger.exception(e)
                elif 'container_id' in current_job.extra_details:
                    current_app.logger.info(f"Killing container {current_job.extra_details['container_id']} for {id}")
                    try:
                        client = docker.from_env()
                        con = client.containers.get(current_job.extra_details['container_id'])
                        con.stop()
                    except Exception as e:
                        current_app.logger.error('Could not kill container')
                        current_app.logger.exception(e)
            current_job.status = 'canceled'
            s.begin()
            s.add(current_job)
            s.commit()
            return True
        else:
            abort(400, message='Currently the only allowed simulation update is canceling a simulation')
