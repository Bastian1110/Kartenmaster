from uno import UnoEnv


env = UnoEnv()
print(env.action_space)
print(env.observation_space)
env.reset()
print(env._get_obs())
