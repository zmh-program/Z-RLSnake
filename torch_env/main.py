from core import AgentDQN
agent = AgentDQN()

finished = False

if __name__ == '__main__':
    if finished:
        agent.test_forever()
    else:
        agent.train()
