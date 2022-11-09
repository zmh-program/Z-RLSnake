from collections import namedtuple
from torch import float32

LR = 0.001  # Learning
EPSILON = 0.8  # 0.8 (80%): argmax index, 0.2(20%): random
GAMMA = 0.9  # 衰减值
ACTION_NUMBER = 8  # 本来是 361个act 0~360° 对应360度, 但是Linear的out_features太大, 计算量偏大, 所以改用 45° 一个act.

# About Batch/Tensor:
tensor_length = 15  # Must be odd!
# If you change this value (tensor_length), you should increase or decrease the number of Convolution,
# 即Conv2d & MaxPool2d.
assert tensor_length % 2 and not tensor_length % 5
tensor_radius = (tensor_length - 1) // 2
tensor_size = tensor_length ** 2
batch_size = 128

default_tensor_dtype = float32

# About Game & Display:
block_size = 20
height = 720  # The length must be divisible by the block_size.
width = 1400  # The length must be divisible by the block_size.
radius = block_size // 2
SCORE_TO_LENGTH = 5
COINS = 200
fps = 15
IGNORE_ZERO = True  # IGNORE ZERO at <function debug_batch>

# About RobotParam:
ROBOT_NUMBER = 0

# About Network:
kernel_size = 3
Transition = namedtuple('Transition', ('state', 'action', 'reward', 'next_state'))

# About Memory:
capacity = 2000

# About Episode:
max_pool = 10000
train_number = 5000
pre_training_pool = 5
