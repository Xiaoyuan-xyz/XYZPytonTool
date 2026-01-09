UNKNOWN = 4
A_WIN = 0
B_WIN = 1
DRAW = 2

PLAYER_A = 0
PLAYER_B = 1
from collections import deque

class RetrogradeSolver:
    def __init__(self, game):
        self.game = game
        self.N = 3025 # 总状态数
        self.num_actions = 4 # 总动作数
        self.status = [[UNKNOWN]*2 for _ in range(self.N)]  # [state][player]  甲0 乙1 表示胜负
        # 0为甲胜 1为乙胜 2为平局
        self.transitions = [[[ -1 for _ in range(self.num_actions)] for _ in range(2)] for _ in range(self.N)]
        # transitions[state][player][action] = next_state
        # 表示在状态state下player走action会得到next_state

    def initialize(self):
        # 初始化，给必胜策略的state打上标记
        for state in range(self.N): # 全体状态
            self.game.set_state(state)
            if self.game.is_terminal():
                winner = self.game.get_winner()
                if winner == PLAYER_A: # 0v3 乙先甲胜
                    self.status[state][PLAYER_B] = A_WIN
                elif winner == PLAYER_B: # 3v0 甲先乙胜
                    self.status[state][PLAYER_A] = B_WIN

            # 写状态转移表 此后game就没用了
            for player in [PLAYER_A, PLAYER_B]:
                for action in range(self.num_actions):
                    self.game.set_state(state)
                    self.game.action(player, action)
                    next_state = self.game.get_state()
                    self.transitions[state][player][action] = next_state

    def solve(self):
        queue = deque()

        # 先把终局状态入队
        for state in range(self.N):
            for player in [PLAYER_A, PLAYER_B]:
                if self.status[state][player] in [A_WIN, B_WIN]:
                    queue.append( (state, player) )

        while queue:
            current_state, current_player = queue.popleft()
            prev_player = 1 - current_player

            for prev_state in range(self.N):
                for action in range(self.num_actions):
                    if self.transitions[prev_state][prev_player][action] == current_state:
                        
                        if self.status[prev_state][prev_player] != UNKNOWN:
                            continue  # 已判定就不管
                        
                        # 乙先甲胜的前一个是甲先甲胜
                        if current_player == PLAYER_B and self.status[current_state][PLAYER_B] == A_WIN:
                            self.status[prev_state][PLAYER_A] = A_WIN
                            queue.append( (prev_state, prev_player) )
                        # 甲先乙胜的前一个是乙先乙胜
                        elif current_player == PLAYER_A and self.status[current_state][PLAYER_A] == B_WIN:
                            self.status[prev_state][PLAYER_B] = B_WIN
                            queue.append( (prev_state, prev_player) )
                        # 甲先甲胜的前一个，如果其后继全是甲先甲胜，那么它是乙先甲胜
                        elif current_player == PLAYER_A and self.status[current_state][PLAYER_A] == A_WIN and all([self.status[self.transitions[prev_state][PLAYER_B][a]][PLAYER_A] == A_WIN for a in range(self.num_actions)]):
                            self.status[prev_state][PLAYER_B] = A_WIN
                            queue.append( (prev_state, prev_player) )
                        # 乙先乙胜的前一个，如果其后继全是乙先乙胜，那么它是甲先乙胜
                        elif current_player == PLAYER_B and self.status[current_state][PLAYER_B] == B_WIN and all([self.status[self.transitions[prev_state][PLAYER_A][a]][PLAYER_B] == B_WIN for a in range(self.num_actions)]):
                            self.status[prev_state][PLAYER_A] = B_WIN
                            queue.append( (prev_state, prev_player) )
                        
                        

        # 剩下未定的算平局
        # for state in range(self.N):
        #     for player in [0, 1]:
        #         if self.status[state][player] == UNKNOWN:
        #             self.status[state][player] = DRAW

    def get_result(self, state, player):
        result = self.status[state][player]
        if result == A_WIN:
            return 'A胜'
        elif result == B_WIN:
            return 'B胜'
        elif result == DRAW:
            return '平局'
        else:
            return '未知'
def tuple_to_index(i, j):
    i += 1
    j += 1
    if i > j:
        i, j = j, i
    index = (j - 1) * j // 2 + i
    return index

def index_to_tuple(n):
    j = 1
    while n > j * (j + 1) // 2:
        j += 1
    prev_total = (j - 1) * j // 2
    i = n - prev_total
    return [i - 1, j - 1]

def state_to_index(state):
    i, j = state // 55, state % 55
    i+=1
    j+=1
    return index_to_tuple(i), index_to_tuple(j)

def index_to_state(tuple1, tuple2):
    i = tuple_to_index(tuple1[0], tuple1[1])
    j = tuple_to_index(tuple2[0], tuple2[1])
    return (i-1) * 55 + j-1        
        
class Game:
    def __init__(self):
        self.state = 0
        self.N = 3135
        self.a = [1, 1]
        self.b = [1, 1]
        
    
    def set_state(self, state):
        self.a, self.b = state_to_index(state)

    def get_state(self):
        return index_to_state(self.a, self.b)

    def is_terminal(self):
        return self.a == [0, 0] or self.b == [0, 0]

    def get_winner(self):
        if self.a == [0, 0] and self.b == [0, 0]:
            return DRAW
        if self.a == [0, 0]:
            return A_WIN
        if self.b == [0, 0]:
            return B_WIN
        return DRAW

    def update(self):
        self.a.sort()
        self.b.sort()

    def action(self, player: int, action: int):
        if self.a == [0, 0] or self.b == [0, 0]:
            self.a = [0, 0]
            self.b = [0, 0]
            return
        if player == PLAYER_A:
            if self.a[0] == 0 and action // 2 == 0:
                action += 2
            if self.b[0] == 0 and action % 2 == 0:
                action += 1        
            a_action = action // 2
            b_action = action % 2
            self.a[a_action] += self.b[b_action]
            self.a[a_action] %= 10
        elif player == PLAYER_B:
            if self.b[0] == 0 and action // 2 == 0:
                action += 2
            if self.a[0] == 0 and action % 2 == 0:
                action += 1        
            b_action = action // 2
            a_action = action % 2
            self.b[b_action] += self.a[a_action]
            self.b[b_action] %= 10
        self.update()        

game = Game()
solver = RetrogradeSolver(game)
solver.initialize()
solver.solve()