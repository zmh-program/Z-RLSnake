import os
import typing
from typing import Tuple
from rich import progress
import numpy
import torch
from torch.nn import *
from parameter import *
from memory import ReplayMemory
from game import RLenvironment
from datetime import datetime
from analysing import image


def _check_capability() -> typing.Union[bool, None]:
    """
    copy -> pytorch.cuda setup
    :return: True / None
    """
    if torch.version.cuda is not None:  # on ROCm we don't want this check
        _path = __import__("torch._C")
        for d in range(torch.cuda.device_count()):
            major, minor = torch.cuda.get_device_capability(d)
            if major * 10 + minor < min((int(arch.split("_")[1]) for arch in torch.cuda.get_arch_list()), default=35):
                return
        return True


device = torch.device(("cpu", "cuda")[torch.cuda.is_available() and _check_capability()])


class Squeeze(Module):
    @staticmethod
    def forward(tensor: torch.Tensor):
        return torch.squeeze(tensor)


def _2dimSqueezeTo4d(tensor: torch.Tensor, size) -> torch.Tensor:
    return tensor.reshape([int(numpy.prod(tensor.size()) // size // size), 1, size, size])


class Network(Module):
    def __init__(self):
        super(Network, self).__init__()
        self.module = Sequential(
            Conv2d(1, 1, kernel_size, padding=1), MaxPool2d(kernel_size), Softplus(),
            Linear(5, 1), Squeeze(), ReLU(),
            Linear(5, ACTION_NUMBER), Squeeze()
        )  # -> 8 <1d>

    def forward(self, tensor) -> torch.Tensor:
        return self.module(_2dimSqueezeTo4d(tensor, tensor_length))


class DeepQNetwork(object):
    def __init__(self):
        # DQN需要使用两个神经网络
        # eval为Q估计神经网络 target为Q现实神经网络
        self.eval_net, self.target_net = Network().to(device), Network().to(device)
        self.optimizer = torch.optim.Adam(self.eval_net.parameters(), lr=LR)  # optimizer
        self.loss_func = MSELoss()  # 误差
        self.memory = ReplayMemory()

        # self.push: callable = self.memory.push

    def update(self, state: torch.Tensor, action: torch.Tensor, reward: float, next_state: torch.Tensor):
        self.memory.push(_2dimSqueezeTo4d(state, tensor_length),
                         action.unsqueeze(0),
                         torch.tensor(reward, dtype=default_tensor_dtype).unsqueeze(0),
                         _2dimSqueezeTo4d(next_state, tensor_length))
        if self.memory.could_train():
            self.learn()

    @staticmethod
    def strict(value):  # RuntimeError: index 12 is out of bounds for dimension 1 with size 12
        return value if 0 <= value < ACTION_NUMBER else torch.tensor(ACTION_NUMBER - 1, dtype=torch.int64,
                                                                     device=device)

    def choose_action(self, tensor: torch.Tensor) -> torch.Tensor:
        return self.strict(torch.max(self.eval_net.forward(tensor.to(device))).data.long().to(device)) \
            if numpy.random.uniform() < EPSILON else \
            torch.randint(0, ACTION_NUMBER, size=(), dtype=torch.int64, device=device)

    def choose_action_by_network(self, tensor: torch.Tensor) -> torch.Tensor:
        """
        训练结果不带入ReplayMemory中, 用于testEpisode,
        选择动作全部使用神经网络, 而不是根据EPSILON判断.

        [i]: 会出现卡死情况
        [s]: 不使用 / 设置回合限制
        """
        return self.strict(torch.max(self.eval_net.forward(tensor.to(device))).data.long().to(device))

    def learn(self):  # 训练卷积神经网络的输出值
        batch = self.memory.get_batch()
        # 针对做过的动作b_a, 来选 q_eval 的值, (q_eval 原本有所有动作的值)
        q_eval = self.eval_net(torch.cat(batch.state).to(device)).gather(1,
                                                                         torch.cat(batch.action).reshape([128, 1]).to(
                                                                             device))  # shape (batch, 1) action的Q估计
        q_next = self.target_net(torch.cat(batch.next_state).to(device)).detach()  # q_next 不进行反向传递误差, detach Q现实
        q_target = torch.cat(batch.reward).to(device) + GAMMA * q_next.max(1)[0]  # shape (batch, 1) DQN算法核心.
        loss = self.loss_func(q_eval, q_target.unsqueeze(-1).float())  # 计算误差
        self.optimizer.zero_grad()
        loss.backward()  # 反向传递
        self.optimizer.step()

    def save_model(self):
        torch.save(self.target_net.state_dict(), 'target.pkl')
        torch.save(self.eval_net.state_dict(), "eval.pkl")

    def load_model(self):
        if os.path.isfile('target.pkl') and os.path.isfile("eval.pkl"):
            self.target_net.load_state_dict(torch.load("target.pkl"), strict=False)
            self.eval_net.load_state_dict(torch.load("eval.pkl"), strict=False)
            return True
        return False


class AgentDQN(object):
    data: (image, None)

    def __init__(self):
        self.dqn = DeepQNetwork()
        self.env = RLenvironment()
        self.train_num = int()

        if self.dqn.load_model():
            print("Updated Model successfully.")

    def agentEpisode(self):
        self.train_num += 1
        state = self.env.reset()
        for _ in progress.track(range(train_number), description=f"Agent {self.train_num}"):
            action = self.dqn.choose_action(state)
            next_state, reward = self.env.step(int(action))
            self.dqn.update(state, action, reward, next_state)
            state = next_state
            if not self.env.is_alive():
                state = self.env.reset()
        self.dqn.save_model()

    def testEpisode(self):
        state = self.env.reset()
        while self.env.is_alive():
            state, _ = self.env.step(int(self.dqn.choose_action(state)))
        if isinstance(self.data, image):
            self.data.add(self.env.get_total_reward(), self.env.getEpisode(), self.env.player_control.score)

    def pretrainingEpisode(self):
        """
        | 预训练 |
        pre-train是一个寻网络权值初值的过程，将pre-train的结果作为BP算法的权值的初值,
        能够解决深度网络在非凸目标函数上陷入局部最优的问题.从这个角度理解更象是带来更好的优化能力.
        在带有pre-train的深度网络的泛化表现上不仅仅是训练误差很小,同时泛化误差也很小,
        带有pre-train的网络在减小测试误差的能力上更优秀,
        感觉是pre-train的网络能够找到一个泛化能力好但是训练误差不一定好的初值.

        选自 CSDN / cjw_seeker / 深度网络pre-train对于深度网络的意义
        ADDR: https://blog.csdn.net/github_36129812/article/details/53116491
        """

        self.train_num += 1
        state = self.env.reset()
        for _ in progress.track(range(train_number), description=f"Pre-train {self.train_num}"):
            next_state, reward, action = self.env.pre_train()
            self.dqn.update(state, torch.tensor(action, device=device, dtype=torch.int64), reward, next_state)
            state = next_state
            if not self.env.is_alive():
                state = self.env.reset()
        self.dqn.save_model()

    def is_finished(self):
        return self.train_num >= max_pool

    def train(self):
        self.data = image()
        self.env.terminateEvent = self.terminateEvent
        while not self.is_finished():
            self.testEpisode()
            if self.train_num <= pre_training_pool:
                self.pretrainingEpisode()
            else:
                self.agentEpisode()

    def test_forever(self):
        self.env.debug = True
        self.env.setTick(True)

        self.data = None
        while True:
            self.testEpisode()

    def terminateEvent(self):
        self.dqn.save_model()
