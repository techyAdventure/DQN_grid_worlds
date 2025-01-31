import torch
from agent import Agent
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
import json
import time
import gym
from environment import Environment

env = Environment()

agent = Agent(state_size=2, action_size=4, seed=5)

n_episodes = 100_000
max_t = 200
eps_start = 1.0
eps_end = 0.01
eps_decay = 0.99995  # 0.999936


def dqn():

    scores = []                        # list containing scores from each episode
    scores_window = deque(maxlen=100)  # last 100 scores
    eps = eps_start                    # initialize epsilon
    max_score = 300.0
    for i_episode in range(1, n_episodes+1):
        # env.render()
        state = env.reset()
        # print(type(state))
        # quit()
        score = 0
        for t in range(max_t):

            action = agent.act(state, eps)
            next_state, reward, done = env.step(action)
            agent.step(state, action, reward, next_state, done)
            state = next_state
            score += reward

            if done:
                break

        scores_window.append(score)
        scores.append(score)
        eps = max(eps_end, eps_decay*eps)  # decrease epsilon
        #print("\nRewards: ",reward,"\n")
        print('\rEpisode {}\tAverage Score: {:.2f}'.format(
            i_episode, np.mean(scores_window)), end="")
        if i_episode % 100 == 0:
            print('\rEpisode {}\tAverage Score: {:.2f}'.format(
                i_episode, np.mean(scores_window)))

        if np.mean(scores_window) >= max_score:
            max_score = np.mean(scores_window)
            print('\nEnvironment solved in {:d} episodes!\tAverage Score: {:.2f}'.format(
                i_episode-100, np.mean(scores_window)))
            torch.save(agent.qnetwork_local.state_dict(),
                       'checkpoint_'+str(agent.reward_)+'.pth')
            # break
    return scores


start_time = time.time()
scores = dqn()
end_time = time.time()

scores_dqn_np = np.array(scores)
np.savetxt("scores_r_"+str(agent.reward_)+".txt", scores_dqn_np)


def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "Execution time: %d hours : %02d minutes : %02d seconds" % (hour, minutes, seconds)


n = end_time-start_time
train_time = convert(n)
print(train_time)

train_info_dictionary = {'algorithm': 'DQN_open_grid_reward', 'eps_start': eps_start, 'eps_end': eps_end,
                         'eps_decay': eps_decay, 'episodes': n_episodes, 'train_time': train_time,
                         'len1': agent.lenmem1, 'len3': agent.lenmem2, 'loss': agent.reward_, 'pop counter': agent.counter}

train_info_file = open('info_r_'+str(agent.reward_)+'.json', 'w')
json.dump(train_info_dictionary, train_info_file)
train_info_file.close()


def moving_average(a, n=100):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


scores_ma_dqn = moving_average(scores, n=100)

fig = plt.figure()
ax = fig.add_subplot(111)
plt.plot(np.arange(len(scores_ma_dqn)), scores_ma_dqn)
plt.ylabel('Score')
plt.xlabel('Episode')
plt.show()
