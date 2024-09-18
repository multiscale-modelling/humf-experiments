# pyright: reportReturnType=false

import submitit
import zntrack


def zop(path) -> str:
    return zntrack.outs_path(zntrack.nwd / path)


class SubmititNode(zntrack.Node):
    def run(self):
        executor = submitit.AutoExecutor(folder="submitit")
        executor.update_parameters(**self.get_executor_parameters())
        executor.submit(self.do_run).result()

    def get_executor_parameters(self):
        return {
            "cpus_per_task": 8,
            "mem_gb": 32,
        }

    def do_run(self):
        pass
