# pyright: reportReturnType=false

import submitit
import zntrack


def zop(path) -> str:
    return zntrack.outs_path(zntrack.nwd / path)


class SubmititNode(zntrack.Node):
    def run(self):
        executor = submitit.AutoExecutor(folder="log_test")
        executor.update_parameters(**self.get_executor_parameters())
        executor.submit(self.do_run).result()

    def get_executor_parameters(self):
        return {}

    def do_run(self):
        pass
