from uno import UnoEnv


# Super usefull function that works for debugging UNO functionality
def manual_play():
    env = UnoEnv(config={})
    obs, _trash = env.reset()
    done = False

    while not done:
        env.observation_to_human(obs[env.actual_player]["real_obs"])
        print(obs[env.actual_player]["action_mask"])
        action = int(input("Enter your action: "))
        obs, reward, terminated, _tuncated, info = env.step({env.actual_player : action})
        done = terminated[env.actual_player]
        print(f"Action: {action}, Reward: {reward}, Info: {info}")

manual_play()