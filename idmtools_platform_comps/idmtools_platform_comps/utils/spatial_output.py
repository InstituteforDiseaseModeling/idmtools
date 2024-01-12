"""
idmtools utility.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import struct
import numpy as np


class SpatialOutput:

    def __init__(self):
        self.n_nodes = 0
        self.n_tstep = 0
        self.nodeids = []
        self.data = None
        self.start = 0
        self.interval = 1

    @classmethod
    def from_bytes(cls, bytes, filtered=False):
        # The header size changes if the file is a filtered one
        headersize = 16 if filtered else 8

        # Create the class
        so = cls()

        # Retrive the number of nodes and number of timesteps
        so.n_nodes, = struct.unpack('i', bytes[0:4])
        so.n_tstep, = struct.unpack('i', bytes[4:8])

        # If filtered, retrieve the start and interval
        if filtered:
            start, = struct.unpack('f', bytes[8:12])
            interval, = struct.unpack('f', bytes[12:16])
            so.start = int(start)
            so.interval = int(interval)

        # Get the nodeids
        so.nodeids = struct.unpack(str(so.n_nodes) + 'I', bytes[headersize:headersize + so.n_nodes * 4])
        so.nodeids = np.asarray(so.nodeids)

        # Retrieve the data
        so.data = struct.unpack(str(so.n_nodes * so.n_tstep) + 'f',
                                bytes[
                                headersize + so.n_nodes * 4:headersize + so.n_nodes * 4 + so.n_nodes * so.n_tstep * 4])
        so.data = np.asarray(so.data)
        so.data = so.data.reshape(so.n_tstep, so.n_nodes)

        return so

    def to_dict(self):
        return {'n_nodes': self.n_nodes,
                'n_tstep': self.n_tstep,
                'nodeids': self.nodeids,
                'start': self.start,
                'interval': self.interval,
                'data': self.data}
