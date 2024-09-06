# pyright: reportCallIssue=false

from humf_experiments.nodes.evaluate_models import EvaluateModels


class TestEvaluateModels:
    def test_run(self):
        node = EvaluateModels(
            data_root_dir="inputs/evaluate_models/data/",
            model_dir="inputs/evaluate_models/models/",
        )
        node.run()
