import random
from parameter import Transition, capacity, batch_size


class ReplayMemory(object):
    def __init__(self):
        self.__memory = []
        self.position = 0
        self.counter = 0

    def get_memory_size(self) -> int:
        return len(self.__memory)

    def push(self, state, action, reward, next_state):
        if self.get_memory_size() < capacity:
            self.__memory.append(None)
        self.__memory[self.position] = Transition(state, action, reward, next_state)
        self.position = (self.position + 1) % capacity
        self.counter += 1

    def _sample(self, batch_num: int) -> list:
        return random.sample(self.__memory, batch_num)

    def get_batch(self) -> Transition:
        return Transition(*zip(*self._sample(batch_size)))

    def __len__(self):
        return len(self.__memory)

    def could_train(self) -> bool:
        return self.counter > capacity and self.get_memory_size() > batch_size

    __del__ = __init__
