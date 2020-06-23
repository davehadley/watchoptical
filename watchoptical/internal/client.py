from enum import Enum
from typing import Union

import dask
from dask.distributed import Client, LocalCluster
from dask.system import cpu_count
from dask_jobqueue import SLURMCluster
from distributed.system import memory_limit
import dask_jobqueue


class ClientType(Enum):
    SINGLE = "single"
    LOCAL = "local"
    CLUSTER = "cluster"


def client(clienttype: ClientType, memory: int = 4 * 1e9) -> Client:
    if (clienttype == ClientType.SINGLE):
        return _singleclient()
    elif (clienttype == ClientType.LOCAL):
        return _localclient(memory=memory)
    elif (clienttype == ClientType.CLUSTER):
        return _slurmclient(memory=memory)


def _localclient(memory: int) -> Client:
    numcores = cpu_count()
    availablememory = memory_limit()
    nworkers = int(max(1, min(availablememory // memory, numcores)))
    cluster = LocalCluster(n_workers=nworkers,
                           threads_per_worker=1,
                           memory_limit='auto')
    return Client(address=cluster)


def _slurmclient(memory: int, partition="epp,taskfarm", account="epp") -> Client:
    # For slurm usage instructions see: https://wiki.csc.warwick.ac.uk/twiki/bin/view/Desktop2018/CowUserGuide
    cluster = SLURMCluster(queue=partition, memory=memory, project=account, cores=1)
    cluster.adapt(minimum_jobs=10, maximum_jobs=100)
    return Client(address=cluster)


def _singleclient():
    return Client(processes=False)
