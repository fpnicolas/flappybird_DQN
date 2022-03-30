import random
from flappybird_dqn import Game


def policy_net(state):
    return random.choice([0, 1])


def play_flappyBird(game):
    game.reset()
    gross_reward = 0
    while True:
        last_screen = game.get_screen()
        current_screen = game.get_screen()
        state = current_screen - last_screen
        action = policy_net(state)
        print(action)
        _, reward, done, _ = game.step(action)
        gross_reward += reward
        last_screen = current_screen
        current_screen = game.get_screen()
        if not done:
            next_state = current_screen - last_screen
        else:
            next_state = None
            break


if __name__ == "__main__":
    game = Game()
    play_flappyBird(game)
