def calculate_team_strength(team):
    """Calculate the average rating of all players in the team."""
    total_rating = sum(player.rating for player in team.players.all())
    num_players = team.players.count()
    if num_players > 0:
        average_rating = total_rating / num_players
    else:
        average_rating = 1000  # Default rating for a team with no players
    return average_rating

def update_ratings(team1, team2, result):
    """Update player ratings based on the match outcome."""
    team1_strength = calculate_team_strength(team1)
    team2_strength = calculate_team_strength(team2)

    # Calculate the expected outcome based on team strengths
    expected_score_team1 = 1 / (1 + 10**((team2_strength - team1_strength) / 400))
    expected_score_team2 = 1 - expected_score_team1

    # Update player ratings based on the match result
    for player in team1.players.all():
        player_rating_diff = K_FACTOR * (result - expected_score_team1)
        player.rating += player_rating_diff
        player.save()

    for player in team2.players.all():
        player_rating_diff = K_FACTOR * ((1 - result) - expected_score_team2)
        player.rating += player_rating_diff
        player.save()

def process_match_result(match, team1_result, team2_result):
    """Process the match result and update player ratings."""
    if team1_result == 'win':
        result = 1
    elif team2_result == 'win':
        result = 0
    else:
        result = 0.5  # For draws or ties

    update_ratings(match.team1, match.team2, result)
    match.match_completed = True
    match.save()

# Example usage:
# Assuming you have an instance of the Match model named 'match'
# and the team1_result and team2_result are the match results for team 1 and team 2.

# Assuming you already defined the K_FACTOR for the Elo system.
K_FACTOR = 32

