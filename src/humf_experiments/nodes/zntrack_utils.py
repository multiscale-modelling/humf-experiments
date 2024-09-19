# pyright: reportReturnType=false

import submitit
import zntrack


def zop(path) -> str:
    return zntrack.outs_path(zntrack.nwd / path)


class SubmititNode(zntrack.Node):
    def run(self):
        executor = submitit.AutoExecutor(folder=self.nwd / "submitit_logs/")
        executor.update_parameters(**self.get_executor_parameters())
        executor.submit(self.do_run).result()

    def get_executor_parameters(self):
        return {
            "cpus_per_task": 8,
            "mem_gb": 32,
            "timeout_min": 8 * 60,
        }

    def do_run(self):
        pass
