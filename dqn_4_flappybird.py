import math
import random
from collections import namedtuple, deque
from itertools import count
import os
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import time


# todo 把视野变小，加快训练速度

from flappybird_dqn import Game

# os.environ["CUDA_VISIBLE_DEVICES"] = '0'

env = Game()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward'))


class ReplayMemory(object):
    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)        # deque本身就是双向队列，但是如果可以随机存取那么要队列有什么用呢

    def push(self, *args):
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)


class DQN(nn.Module):
    def __init__(self, h, w, outputs):
        super(DQN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=5, stride=2)      # 卷积层
        self.bn1 = nn.BatchNorm2d(16)                               # 归一化
        self.conv2 = nn.Conv2d(16, 32, kernel_size=5, stride=2)
        self.bn2 = nn.BatchNorm2d(32)
        self.conv3 = nn.Conv2d(32, 32, kernel_size=5, stride=2)
        self.bn3 = nn.BatchNorm2d(32)

        # 以下空格前这部分代码是为了进行全连接
        def conv2d_size_out(size, kernel_size=5, stride=2):
            return (size - (kernel_size - 1) - 1) // stride + 1
        convw = conv2d_size_out(conv2d_size_out(conv2d_size_out(w)))
        convh = conv2d_size_out(conv2d_size_out(conv2d_size_out(h)))
        linear_input_size = convw * convh * 32
        self.head = nn.Linear(linear_input_size, outputs)

    def forward(self, x):
        x = x.to(device)
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))
        return self.head(x.view(x.size(0), -1))
        # 这些层有一个特别奇怪的地方，就是用对象直接当函数调用？
        # x.size(0)好像没有什么作用啊，我明白了，就是让其变成两维数据，第一维是batch，第二维是其他
        # Tensor.view是什么作用


BATCH_SIZE = 32
GAMMA = 0.999
EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 200
TARGET_UPDATE = 10

screen_height, screen_width = 300, 128
n_actions = 2

policy_net = DQN(screen_height, screen_width, n_actions).to(device)
# policy_net = torch.load("./policy_net")
target_net = DQN(screen_height, screen_width, n_actions).to(device)
# target_net.load_state_dict(policy_net.state_dict())
target_net.eval()           # 这里的eval与python的eval实现字符串命令的不同,是与train相关的evaluation

optimizer = optim.RMSprop(policy_net.parameters())
memory = ReplayMemory(10000)

step_done = 0


# epsilon-greedy算法
def select_action(state):
    global step_done
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * math.exp(-1. * step_done / EPS_DECAY)
    step_done += 1
    if sample > eps_threshold:
        with torch.no_grad():
            return policy_net(state).max(1)[1].view(1, 1)
    else:
        return torch.tensor([[random.randrange(n_actions)]], device=device, dtype=torch.long)


episode_durations = []


# Training loop
def optimize_model():
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE)
    batch = Transition(*zip(*transitions))
   # 屏蔽没有下一步的部分
    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None, batch.next_state)), device=device, dtype=torch.bool)
    non_final_next_states = torch.cat([s for s in batch.next_state if s is not None])
    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)
    state_action_values = policy_net(state_batch)
    state_action_values = state_action_values.gather(1, action_batch)
    next_state_values = torch.zeros(BATCH_SIZE, device=device)
    next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0].detach()
    expected_state_action_values = (next_state_values * GAMMA) + reward_batch
    criterion = nn.SmoothL1Loss()
    loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))        # 都是（128，1）

    optimizer.zero_grad()
    loss.backward()
    for param in policy_net.parameters():
        param.grad.data.clamp_(-1, 1)
    optimizer.step()


def play_once(env, training=True, num_episodes=50000):
    performance = []
    for i_episode in range(num_episodes):
        # t1 = time.time()
        env.reset()
        last_screen = env.get_screen()
        current_screen = env.get_screen()
        state = torch.tensor(current_screen - last_screen, dtype=torch.float).unsqueeze(0)
        # t2 = time.time()
        # print(t2-t1)
        for t in count():
            # t3 = time.time()
            action = select_action(state)
            # t4 = time.time()
            # print("select action: %d", t4-t3)
            # print(action)
            _, reward, done, info = env.step(action.item())
            # t5 = time.time()
            # print("step time: %d", t5-t4)
            reward = torch.tensor([reward], device=device)
            # print(reward)
            last_screen = current_screen
            current_screen = env.get_screen()
            if not done:
                next_state = torch.tensor(current_screen - last_screen, dtype=torch.float).unsqueeze(0)
            else:
                next_state = None
            if training:
                memory.push(state, action, next_state, reward)
                # t6 = time.time()
                # print("get next_state: %d", t6 - t5)
                optimize_model()
                # t7 = time.time()
                # print("optimze time: %d", t7 - t6)
            state = next_state
            if done:
                episode_durations.append(t + 1)
                performance.append(info)
                break
        if training and i_episode % TARGET_UPDATE == 0:
            target_net.load_state_dict(policy_net.state_dict())
        print("{} episode done".format(i_episode))
        print(performance[-1])
    torch.save(policy_net, "./policy_net")
    print('Training Complete')
    return performance


# Test
print(play_once(env, training=False, num_episodes=10))
