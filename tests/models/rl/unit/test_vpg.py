import argparse
from unittest import TestCase

import gym
import pytest
import torch
from pl_bolts.models.rl.common.agents import Agent
from pl_bolts.models.rl.common.gym_wrappers import ToTensor
from pl_bolts.models.rl.common.networks import MLP
from pl_bolts.models.rl.vanilla_policy_gradient_model import VanillaPolicyGradient
from pl_bolts.utils import _IS_WINDOWS
from torch import Tensor


class TestPolicyGradient(TestCase):
    def setUp(self) -> None:
        self.env = ToTensor(gym.make("CartPole-v0"))
        self.obs_shape = self.env.observation_space.shape
        self.n_actions = self.env.action_space.n
        self.net = MLP(self.obs_shape, self.n_actions)
        self.agent = Agent(self.net)

        parent_parser = argparse.ArgumentParser(add_help=False)
        parent_parser = VanillaPolicyGradient.add_model_specific_args(parent_parser)
        args_list = ["--env", "CartPole-v0", "--batch_size", "32"]
        self.hparams = parent_parser.parse_args(args_list)
        self.model = VanillaPolicyGradient(**vars(self.hparams))

    @pytest.mark.skipif(_IS_WINDOWS, reason="strange TimeOut or MemoryError")  # todo
    def test_loss(self):
        """Test the reinforce loss function."""

        batch_states = torch.rand(32, 4)
        batch_actions = torch.rand(32).long()
        batch_qvals = torch.rand(32)

        loss = self.model.loss(batch_states, batch_actions, batch_qvals)

        assert isinstance(loss, Tensor)

    def test_train_batch(self):
        """Tests that a single batch generates correctly."""

        self.model.n_steps = 4
        self.model.batch_size = 1
        xp_dataloader = self.model.train_dataloader()

        batch = next(iter(xp_dataloader))
        assert len(batch) == 3
        assert len(batch[0]) == self.model.batch_size
        assert isinstance(batch, list)
        assert isinstance(batch[0], Tensor)
        assert isinstance(batch[1], list)
        assert isinstance(batch[1][0], Tensor)
        assert isinstance(batch[2], Tensor)
