# pyright: reportCallIssue=false

from humf_experiments.nodes.train_model import TrainModel


class TestTrainModel:
    def test_run(self):
        node = TrainModel(
            max_epochs=1,
            model="ljc_water",
            data_root_dir="inputs/train_model/data/",
        )
        node.run()
