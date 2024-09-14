import random
import torch
import torch.nn as nn
import torch.optim as optim

class GameEnvironment:
    def __init__(self):
        self.reset()

    def reset(self):
        # 每个玩家的left和right初始为1
        self.state = {
            "player1": {"left": 1, "right": 1},
            "player2": {"left": 1, "right": 1},
        }
        self.current_player = "player1"
        return self.state

    def step(self, action):
        """
        action 是一个元组 (chosen_own, chosen_opponent)，代表选手选中的自己和对方的数字。
        """
        own_choice, opponent_choice = action

        # 当前玩家的left或right
        own_value = self.state[self.current_player][own_choice]
        # 对方玩家的left或right
        opponent_value = self.state[self._opponent()][opponent_choice]

        # 相加操作
        new_value = own_value + opponent_value
        if new_value > 10:
            new_value -= 10
        
        # 更新当前玩家的数字
        self.state[self.current_player][own_choice] = new_value
        
        # 检查是否出现0
        if new_value == 0:
            done = self._check_win_condition()
            reward = 1 if done else 0
            next_player = self._opponent()
        else:
            done = False
            reward = 0
            next_player = self._opponent()

        self.current_player = next_player
        return self.state, reward, done

    def _check_win_condition(self):
        # 胜利条件：当前玩家的两个数字均为0
        return all(value == 0 for value in self.state[self.current_player].values())

    def _opponent(self):
        return "player2" if self.current_player == "player1" else "player1"

class PolicyNetwork(nn.Module):
    def __init__(self, input_dim=4, output_dim=4):
        super(PolicyNetwork, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, output_dim)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return torch.softmax(self.fc3(x), dim=-1)

class Agent:
    def __init__(self, input_dim, output_dim):
        self.policy_network = PolicyNetwork(input_dim, output_dim)
        self.optimizer = optim.Adam(self.policy_network.parameters(), lr=0.001)
    
    def get_action(self, state):
        state = torch.FloatTensor(state).unsqueeze(0)
        probs = self.policy_network(state)
        action = torch.multinomial(probs, 1)
        return action.item()
    
    def update(self, states, actions, rewards):
        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        
        # 计算策略的损失
        action_probs = self.policy_network(states)
        action_probs = action_probs.gather(1, actions.unsqueeze(1)).squeeze()
        
        # 计算损失
        loss = -torch.sum(torch.log(action_probs) * rewards)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()


class RandomAgent:
    def __init__(self):
        pass

    def act(self, state):
        # 随机选择自己的left或right，以及对方的left或right
        own_choice = random.choice(["left", "right"])
        opponent_choice = random.choice(["left", "right"])
        return (own_choice, opponent_choice)


def play_game(agent1, agent2):
    env = GameEnvironment()
    state = env.reset()
    done = False

    while not done:
        if env.current_player == "player1":
            action = agent1.act(state)
        else:
            action = agent2.act(state)

        state, reward, done = env.step(action)

    return reward


print('test')

# 训练例子
agent1 = RandomAgent()
agent2 = RandomAgent()

for episode in range(10000):  # 训练10000局
    play_game(agent1, agent2)


print("训练完成")