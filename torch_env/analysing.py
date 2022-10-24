import matplotlib.pyplot as plt
import numpy
from numpy import average
from parameter import train_number

setup = False


class image(object):
    step = train_number // 10

    @staticmethod
    def setup():
        global setup
        if not setup:
            setup = True
            plt.ion()
            plt.figure(1)
            plt.title("Test Agent Episode Reward")

    def __init__(self):
        self.rewards = numpy.array([])
        self.scores = numpy.array([])
        self.episode = numpy.array([])

    def add(self, reward, episode, score):
        self.rewards = numpy.append(self.rewards, reward)
        self.episode = numpy.append(self.episode, episode)
        self.scores = numpy.append(self.scores, score)
        self.show_polt()

    def show_polt(self):
        self.setup()
        plt.plot(self.episode, self.rewards, c="r", label="reward")
        plt.plot(self.episode, self.scores, c="b", label="score")
        plt.pause(0.1)
