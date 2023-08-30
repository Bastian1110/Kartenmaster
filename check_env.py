"""
Testing script fot the gym environment 
By Sebastian Mora (@bastian1110)
"""

from uno import UnoEnv


def test_random_play(n_episodes=10):
    env = UnoEnv()

    for episode in range(n_episodes):
        obs = env.reset()
        done = False
        t = 0

        while not done:
            # Take a random action from the action space
            action = env.action_space.sample()
            obs, reward, done, info = env.step(action)

            # Print out the results for debugging
            print(
                f"Episode: {episode + 1}, Time Step: {t}, Action: {action}, Reward: {reward}, Info: {info}"
            )
            t += 1

        print(f"Episode {episode + 1} finished after {t} timesteps")


def manual_play():
    env = UnoEnv()
    obs, _trash = env.reset()
    done = False

    while not done:
        env.observation_to_human(obs)
        action = int(input("Enter your action: "))
        obs, reward, done, _tuncated, info = env.step(action)
        print(f"Action: {action}, Reward: {reward}, Info: {info}")


def test_action_mask(n_episodes=10):
    env = UnoEnv()

    for episode in range(n_episodes):
        obs, _ = env.reset()
        done = False
        t = 0

        while not done:
            env.observation_to_human(obs)
            print(env.valid_mask().index(True))
            action = env.action_space.sample()

            obs, reward, done, _, info = env.step(action)

            print(
                f"Episode: {episode + 1}, Time Step: {t}, New Player: {env.actual_player}, Action: {env.action_to_human(action)}, Reward: {reward}, Info: {info}"
            )
            t += 1

        print(f"Episode {episode + 1} finished after {t} timesteps")


manual_play()
