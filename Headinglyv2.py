import numpy as np
import matplotlib.pyplot as plt

num_simulations = 250000
balls_remaining = 63
total_score = 76  

# Using espn ask cric info for numbers
# input usually something like Lyon bowling to Stokes figures
bowler_probabilities = {
    'Lyon': {
        'stokes': {'0': 657/840, '1': 92/840, '2': 19/840, '3': 5/840, '4': 42/840, '6': 16/840, 'out': 9/840},
        'leach':  {'0': 63/73, '1': 0, '2': 3/73, '3': 2/73, '4': 1/73, '6': 1/73, 'out': 3/73}
    },
    'Cummins': {
        'stokes': {'0': 222/333, '1': 60/333, '2': 14/333, '3': 1/333, '4': 28/333, '6': 2/333, 'out': 6/333},
        'leach':  {'0': 36/51, '1': 9/51, '2': 1/51, '3': 2/51, '4': 3/51, '6': 0.00, 'out': 0.00}
    },
    'Hazlewood': {
        'stokes': {'0': 196/277, '1': 40/277, '2': 14/277, '3': 4/277, '4': 14/277, '6': 6/277, 'out': 3/277},
        'leach':  {'0': 23/29, '1': 2/29, '2': 0, '3': 2/29, '4': 1/29, '6': 0, 'out': 1/29}
    },
    'Pattinson': {
        'stokes': {'0': 42/56, '1': 7/56, '2': 3/56, '3': 0, '4': 3/56, '6': 0, 'out': 1/56},
        'leach':  {'0': 1, '1': 0, '2': 0, '3': 0, '4': 0, '6': 0, 'out': 0}
    },
}

# Define the specific bowling sequence
bowlers_sequence = (
    ['Pattinson'] * 4 + ['Lyon'] * 6 + ['Pattinson'] * 6 + ['Lyon'] * 6 + 
    ['Pattinson'] * 6 + ['Cummins'] * 6 + ['Hazlewood'] * 6 + ['Lyon'] * 6 + 
    ['Cummins'] * 6 + ['Lyon'] * 6 + ['Cummins'] * 6
)

def simulate_match():
    runs = 0
    balls_faced = 0
    stokes_on_strike = False  # Leach starts on strike
    balls_in_over = 0
    aggression_factor = 1.5  # Initial aggression factor for Stokes
    boundaries_hit = 0
    over_length = 4 #only 4 balls in the first over
    win_with_limit = None
    win_without_limit = None

    while win_without_limit is None:
        current_bowler = bowlers_sequence[balls_faced % len(bowlers_sequence)]  # Loop through bowlers
        batter = 'stokes' if stokes_on_strike else 'leach'
        probabilities = bowler_probabilities[current_bowler][batter].copy()
        
        if stokes_on_strike:
            # Apply aggression factor to 4s and 6s
            probabilities['4'] *= aggression_factor
            probabilities['6'] *= aggression_factor
            probabilities['out'] *= 1 + (aggression_factor * 0.1)  # Increase risk dynamically
            # Normalize probabilities
            total = sum(probabilities.values())
            for outcome in probabilities:
                probabilities[outcome] /= total
        
        outcome = np.random.choice(list(probabilities.keys()), p=list(probabilities.values()))
        
        if outcome == 'out':
            return (win_with_limit or 0, 0)  # England loses
        elif outcome == '0':
            pass
        elif outcome == '1':
            if stokes_on_strike and balls_in_over < 3:
                pass  # Stokes refuses the single before the 4th ball
            else:
                runs += 1
                stokes_on_strike = not stokes_on_strike  # Rotate strike
        elif outcome == '2':
            runs += 2
        elif outcome == '3':
            runs += 3
            stokes_on_strike = not stokes_on_strike  # Rotate strike
        elif outcome in ['4', '6']:
            runs += int(outcome)
            boundaries_hit += 1
            aggression_factor += 0.1  # Increase aggression with each boundary
        
        balls_faced += 1
        balls_in_over += 1
        
        # Check for win with limit
        if runs >= total_score:
            win_without_limit = 1
            if win_with_limit is None:
                win_with_limit = 1 if balls_faced <= balls_remaining else 0
        
        if balls_faced == balls_remaining and win_with_limit is None:
            win_with_limit = 1 if runs >= total_score else 0
        
        if balls_in_over == over_length:
            stokes_on_strike = not stokes_on_strike
            balls_in_over = 0
            over_length = 6  # Set all subsequent overs to 6 balls
    
    return win_with_limit, win_without_limit

# Run Monte Carlo Simulations
wins_with_limit = 0
wins_without_limit = 0

for i in range(num_simulations):
    win_limit, win_no_limit = simulate_match()
    wins_with_limit += win_limit
    wins_without_limit += win_no_limit
    if (i + 1) % 10000 == 0:
        print(f'Iteration {i + 1}/{num_simulations} completed')

win_probability_with_limit = wins_with_limit / num_simulations
win_probability_without_limit = wins_without_limit / num_simulations

# Display Results
print(f'Wins with ball limit: {wins_with_limit}')
print(f'Estimated Probability of England Winning (With Ball Limit): {win_probability_with_limit:.4f}')
print(f'Wins without ball limit: {wins_without_limit}')
print(f'Estimated Probability of England Winning (Without Ball Limit): {win_probability_without_limit:.4f}')

# Plot histogram
plt.bar(['Loss (With Limit)', 'Win (With Limit)', 'Loss (No Limit)', 'Win (No Limit)'],
        [num_simulations - wins_with_limit, wins_with_limit, num_simulations - wins_without_limit, wins_without_limit],
        color=['red', 'green', 'red', 'blue'])
plt.xlabel('Outcome')
plt.ylabel('Frequency')
plt.title('Monte Carlo Simulation of England’s Victory at Headingley')
plt.show()
