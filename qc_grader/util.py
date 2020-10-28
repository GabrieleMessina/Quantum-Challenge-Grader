import json

import numpy as np
from typing import Any, Optional, Tuple, Union

from qiskit import IBMQ, QuantumCircuit, assemble
from qiskit.providers import JobStatus
from qiskit.providers.ibmq import AccountProvider, IBMQProviderError
from qiskit.providers.ibmq.job import IBMQJob
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import Unroller


def get_provider() -> AccountProvider:
    # get provider
    try:
        provider = IBMQ.get_provider()
    except IBMQProviderError:
        provider = IBMQ.load_account()
    return provider


def get_job(job_id: str) -> Optional[IBMQJob]:
    try:
        job = get_provider().backends.retrieve_job(job_id).status()
        return job
    except Exception:
        pass

    return None


def get_job_status(job: Union[str, IBMQJob]) -> Tuple[str, Optional[JobStatus]]:
    try:
        if isinstance(job, IBMQJob):
            job_id = job.job_id()
            job_status = job.status()
        else:
            job_id = job
            job_status = get_provider().backends.retrieve_job(job_id).status()
    except Exception:
        return job_id, None

    return job_id, job_status


def circuit_to_json(qc: QuantumCircuit) -> str:
    class _QobjEncoder(json.encoder.JSONEncoder):
        def default(self, obj: Any) -> Any:
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, complex):
                return (obj.real, obj.imag)
            return json.JSONEncoder.default(self, obj)

    return json.dumps(circuit_to_dict(qc), cls=_QobjEncoder)


def circuit_to_dict(qc: QuantumCircuit) -> dict:
    qobj = assemble(qc)
    return qobj.to_dict()


def compute_cost(circuit: QuantumCircuit) -> int:

    print('⏳ This may take several minutes...')
    # Unroll the circuit
    pass_ = Unroller(['u3', 'cx'])
    pm = PassManager(pass_)
    new_circuit = pm.run(circuit)

    # obtain gates
    gates = new_circuit.count_ops()
    num_u3 = gates['u3']
    num_cx = gates['cx']

    # compute cost
    cost = num_u3 + 10 * num_cx

    return cost
