import random
import numpy as np
from stateSpace import Action


class Rewards():
    rewards_table = np.zeros(len(Action))
    q_table = None
    q2_table = None  # For double Q-learning
    epoch = 0
    iteration = 0

    def __init__(self, states, actions, epsilon=0.9, gamma=0.3, lr=0.2, learning=True):
        super().__init__()
        self.learning = learning
        self.q_table = np.zeros([states, actions])
        self.q2_table = np.zeros([states, actions])
        self.epsilon_greedy = epsilon
        self.gamma = gamma
        self.lr = lr
        self.max_expected_reward = 0
        
        VERY_BAD = -0.8
        BAD = -0.4
        GOOD = 0.4
        VERY_GOOD = 1.2

        self.rewards_table[Action.SAFE_MoveOut.value] = 0.4
        self.rewards_table[Action.SAFE_MoveDice.value] = 0.01
        self.rewards_table[Action.SAFE_Goal.value] = 0.8
        self.rewards_table[Action.SAFE_Star.value] = 0.8
        self.rewards_table[Action.SAFE_Globe.value] = 0.4
        self.rewards_table[Action.SAFE_Protect.value] = 0.2
        self.rewards_table[Action.SAFE_Kill.value] = 1.5
        self.rewards_table[Action.SAFE_Die.value] = -0.5
        self.rewards_table[Action.SAFE_GoalZone.value] = 0.2

        self.rewards_table[Action.UNSAFE_MoveOut.value] = self.rewards_table[Action.SAFE_MoveOut.value] + BAD
        self.rewards_table[Action.UNSAFE_MoveDice.value] = self.rewards_table[Action.SAFE_MoveDice.value] + BAD
        self.rewards_table[Action.UNSAFE_Star.value] = self.rewards_table[Action.SAFE_Star.value] + BAD
        self.rewards_table[Action.UNSAFE_Globe.value] = self.rewards_table[Action.SAFE_Globe.value] + GOOD
        self.rewards_table[Action.UNSAFE_Protect.value] = self.rewards_table[Action.SAFE_Protect.value] + GOOD
        self.rewards_table[Action.UNSAFE_Kill.value] = self.rewards_table[Action.SAFE_Kill.value] + GOOD
        self.rewards_table[Action.UNSAFE_Die.value] = self.rewards_table[Action.SAFE_Die.value] + VERY_BAD
        self.rewards_table[Action.UNSAFE_GoalZone.value] = self.rewards_table[Action.SAFE_GoalZone.value] + GOOD
        self.rewards_table[Action.UNSAFE_Goal.value] = self.rewards_table[Action.SAFE_Goal.value] + GOOD

        self.rewards_table[Action.HOME_MoveOut.value] = self.rewards_table[Action.SAFE_MoveOut.value] + VERY_GOOD
        self.rewards_table[Action.HOME_MoveDice.value] = self.rewards_table[Action.SAFE_MoveDice.value] + VERY_BAD
        self.rewards_table[Action.HOME_Star.value] = self.rewards_table[Action.SAFE_Star.value] + VERY_BAD
        self.rewards_table[Action.HOME_Globe.value] = self.rewards_table[Action.SAFE_Globe.value] + VERY_BAD
        self.rewards_table[Action.HOME_Protect.value] = self.rewards_table[Action.SAFE_Protect.value] + VERY_BAD
        self.rewards_table[Action.HOME_Kill.value] = self.rewards_table[Action.SAFE_Kill.value] + VERY_BAD
        self.rewards_table[Action.HOME_Die.value] = self.rewards_table[Action.SAFE_Die.value] + VERY_BAD
        self.rewards_table[Action.HOME_GoalZone.value] = self.rewards_table[Action.SAFE_GoalZone.value] + VERY_BAD
        self.rewards_table[Action.HOME_Goal.value] = self.rewards_table[Action.SAFE_Goal.value] + VERY_BAD

    def update_epsilon(self, new_epsilon):
        self.epsilon_greedy = new_epsilon

    def get_state_action_of_array(self, value, array):
        if np.isnan(value):
            return (-1, -1)
        idx = np.where(array == value)
        random_idx = random.randint(0, len(idx[0]) - 1)
        state = idx[0][random_idx]
        action = idx[1][random_idx]
        return (state, action)

    def choose_next_action(self, action_table):
        q_table_options = np.multiply(self.q_table, action_table)

        if random.uniform(0, 1) < self.epsilon_greedy:
            self.iteration = self.iteration + 1
            nz = action_table[np.logical_not(np.isnan(action_table))]
            randomValue = nz[random.randint(0, len(nz) - 1)]
            state, action = self.get_state_action_of_array(randomValue, action_table)
        else:
            maxVal = np.nanmax(q_table_options)
            if not np.isnan(maxVal):
                state, action = self.get_state_action_of_array(maxVal, q_table_options)
            else:
                nz = action_table[np.logical_not(np.isnan(action_table))]
                random_value = nz[random.randint(0, len(nz) - 1)]
                state, action = self.get_state_action_of_array(random_value, action_table)
        return (state, action)

    def choose_next_action_double_q_learning(self, action_table):
        q_table_options = np.multiply(self.q_table, action_table)
        q2_table_options = np.multiply(self.q2_table, action_table)

        if random.uniform(0, 1) < self.epsilon_greedy:
            self.iteration = self.iteration + 1
            nz = action_table[np.logical_not(np.isnan(action_table))]
            random_value = nz[random.randint(0, len(nz) - 1)]
            state, action = self.get_state_action_of_array(random_value, action_table)
        else:
            q_max_val = np.nanmax(q_table_options)
            q2_max_val = np.nanmax(q2_table_options)

            if not np.isnan(q_max_val) and not np.isnan(q2_max_val):
                if random.uniform(0, 1) < 0.5:
                    state, action = self.get_state_action_of_array(q_max_val, q_table_options)
                else:
                    state, action = self.get_state_action_of_array(q2_max_val, q2_table_options)
            elif not np.isnan(q_max_val):
                state, action = self.get_state_action_of_array(q_max_val, q_table_options)
            elif not np.isnan(q2_max_val):
                state, action = self.get_state_action_of_array(q2_max_val, q2_table_options)
            else:
                nz = action_table[np.logical_not(np.isnan(action_table))]
                random_value = nz[random.randint(0, len(nz) - 1)]
                state, action = self.get_state_action_of_array(random_value, action_table)
        return (state, action)

    def q_learning_reward(self, state, new_action_table, action):
        state = int(state)
        action = int(action)

        # Q-learning equation
        reward = self.rewards_table[action]
        # Q-learning
        estimate_of_optimal_future_value = np.max(self.q_table * new_action_table)
        old_q_value = self.q_table[state, action]
        delta_q = self.lr * (reward + self.gamma * estimate_of_optimal_future_value - old_q_value)
        
        self.max_expected_reward += reward
        
        # Update the Q table from the new action taken in the current state
        self.q_table[state, action] = old_q_value + delta_q
        # print("update q table, state: {0}, action:{1}".format(state, action))

    def double_q_learning_reward(self, state, action):
        state = int(state)
        action = int(action)

        reward = self.rewards_table[action]
        if random.random() < 0.5:
            new_q_values = self.q_table[state]
            best_new_action = np.argmax(new_q_values)
            new_q_value = self.q2_table[state, best_new_action]
            delta_q = self.lr * (reward + self.gamma * new_q_value - self.q_table[state, action])
            self.q_table[state, action] += delta_q
        else:
            new_q_values = self.q2_table[state]
            best_new_action = np.argmax(new_q_values)
            new_q_value = self.q_table[state, best_new_action]
            delta_q = self.lr * (reward + self.gamma * new_q_value - self.q2_table[state, action])
            self.q2_table[state, action] += delta_q

        self.max_expected_reward += reward

    def sarsa_reward(self, state, new_action_table, action):
        state = int(state)
        action = int(action)

        reward = self.rewards_table[action]

        old_q_value = self.q_table[state, action]
        new_q_value = new_action_table[state, action]
        delta_q = self.lr * (reward + self.gamma * new_q_value - old_q_value)

        self.max_expected_reward += reward
        self.q_table[state, action] = old_q_value + delta_q

    def td0_reward(self, state, new_action_table, action):
        state = int(state)
        action = int(action)

        reward = self.rewards_table[action]

        old_q_value = self.q_table[state, action]
        new_q_value = np.max(new_action_table[state, :])
        delta_q = self.lr * (reward + self.gamma * new_q_value - old_q_value)

        self.max_expected_reward += reward

        # Update the Q table from the new action taken in the current state
        self.q_table[state, action] = old_q_value + delta_q
