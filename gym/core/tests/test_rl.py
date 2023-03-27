import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from core.envs.rl_env import CustomEnv
from stable_baselines3 import A2C, DDPG, PPO
from stable_baselines3.common import results_plotter
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.results_plotter import plot_results
from tqdm import tqdm

EPOCHS = 30


@pytest.mark.skip()
def test_ordinal():
    env = CustomEnv()

    observation = env.reset()

    info_records = []
    for _ in range(64):
        action = [0]
        observation, reward, done, info = env.step(action)
        info_records.append(info)
        if done:
            break

    df = pd.DataFrame(info_records)
    df.to_csv("results/ordinal.csv", index=False)


@pytest.mark.skip()
def test_a2c():
    env = CustomEnv()

    observation = env.reset()

    timesteps = 64 * 32

    model = A2C("MultiInputPolicy", env, verbose=0)

    model.learn(total_timesteps=timesteps,
                progress_bar=True)

    model.save('models/a2c')

    # test model
    observation = env.reset()

    info_records = []
    while 1:
        action, _states = model.predict(observation, deterministic=True)
        observation, reward, done, info = env.step(action)
        info_records.append(info)
        if done:
            break

    df = pd.DataFrame(info_records)
    df.to_csv("results/a2c.csv", index=False)


@pytest.mark.skip()
def test_ddpg():
    env = CustomEnv()
    n_actions = env.action_space.shape[-1]
    action_noise = NormalActionNoise(mean=np.zeros(
        n_actions), sigma=0.1 * np.ones(n_actions))

    model = DDPG("MultiInputPolicy", env, action_noise=action_noise, verbose=1)
    model.learn(total_timesteps=64 * 32,
                log_interval=10, progress_bar=True)
    model.save("models/ddpg")

    observation = env.reset()
    info_records = []

    for _ in range(64):
        action, _states = model.predict(observation, deterministic=True)
        observation, reward, done, info = env.step(action)
        info_records.append(info)
        if done:
            observation = env.reset()

    df = pd.DataFrame(info_records)
    df.to_csv("results/ddpg.csv", index=False)


@pytest.mark.skip()
def test_ppo():
    env = CustomEnv()
    model = PPO("MultiInputPolicy", env, verbose=1)
    model.learn(total_timesteps=64 * 32, progress_bar=True)
    model.save("ppo")

    observation = env.reset()
    info_records = []
    for _ in range(64):
        action, _states = model.predict(observation, deterministic=True)
        observation, reward, done, info = env.step(action)
        info_records.append(info)
        if done:
            observation = env.reset()

    df = pd.DataFrame(info_records)
    df.to_csv("results/ppo.csv", index=False)


# @pytest.mark.skip()
def test_proportion_honest_on_convergence():
    info_records = []
    ratios = np.linspace(0.0, 1, 100)
    for ratio in tqdm(ratios):
        env = CustomEnv(initial_honest_proportion=ratio)
        observation = env.reset()
        for _ in range(64):
            action = [1]
            observation, reward, done, info = env.step(action)
            info['initial_honest_ratio'] = ratio
            info_records.append(info)
            if done:
                observation = env.reset()

    df = pd.DataFrame(info_records)
    df.to_csv("results/honest_ratio.csv", index=False)
