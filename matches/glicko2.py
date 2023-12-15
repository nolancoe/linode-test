from users.models import Badge, Profile
from django.db.models import Max

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

    # Check if any player has the highest rating
    highest_rating = Profile.objects.aggregate(max_rating=Max('rating'))['max_rating']

    if highest_rating:
        highest_rated_players = Profile.objects.filter(rating=highest_rating)
        for highest_rated_player in highest_rated_players:
            # Add Badge 20 to the profile of the highest-rated player
            highest_rated_player.badges.add(Badge.objects.get(id=20))


def process_match_result(match, team1_result, team2_result, team1, team2):
    """Process the match result and update player ratings."""
    if team1_result == 'win':
        result = 1

        # Add Badges
        first_win_badge = 2
        fifth_win_badge = 3
        tenth_win_badge = 4
        twentieth_win_badge = 5
        fiftieth_win_badge = 6
        hundredth_win_badge = 7
        twohundredth_win_badge = 8
        threehundredth_win_badge = 9
        fourhundredth_win_badge = 10
        fivehundredth_win_badge = 11
        thousandth_win_badge = 12

        first_match_badge = 14

        players_without_first_win = team1.players.exclude(badges__id=first_win_badge)
        players_without_fifth_win = team1.players.exclude(badges__id=fifth_win_badge)
        players_without_tenth_win = team1.players.exclude(badges__id=tenth_win_badge)
        players_without_twentieth_win = team1.players.exclude(badges__id=twentieth_win_badge)
        players_without_fiftieth_win = team1.players.exclude(badges__id=fiftieth_win_badge)
        players_without_hundredth_win = team1.players.exclude(badges__id=hundredth_win_badge)
        players_without_twohundredth_win = team1.players.exclude(badges__id=twohundredth_win_badge)
        players_without_threehundredth_win = team1.players.exclude(badges__id=threehundredth_win_badge)
        players_without_fourhundredth_win = team1.players.exclude(badges__id=fourhundredth_win_badge)
        players_without_fivehundredth_win = team1.players.exclude(badges__id=fivehundredth_win_badge)
        players_without_thousandth_win = team1.players.exclude(badges__id=thousandth_win_badge)
        
        players_without_first_match = team1.players.exclude(badges__id=first_match_badge)
        other_players_without_first_match = team2.players.exclude(badges__id=first_match_badge)

        first_win = Badge.objects.get(id=first_win_badge)
        fifth_win = Badge.objects.get(id=fifth_win_badge)
        tenth_win = Badge.objects.get(id=tenth_win_badge)
        twentieth_win = Badge.objects.get(id=twentieth_win_badge)
        fiftieth_win = Badge.objects.get(id=fiftieth_win_badge)
        hundredth_win = Badge.objects.get(id=hundredth_win_badge)
        twohundredth_win = Badge.objects.get(id=twohundredth_win_badge)
        threehundredth_win = Badge.objects.get(id=threehundredth_win_badge)
        fourhundredth_win = Badge.objects.get(id=fourhundredth_win_badge)
        fivehundredth_win = Badge.objects.get(id=fivehundredth_win_badge)
        thousandth_win = Badge.objects.get(id=thousandth_win_badge)
        first_match = Badge.objects.get(id=first_match_badge)

        for player in players_without_first_win:
            player.badges.add(first_win)

        for player in players_without_fifth_win:
            if player.wins >= 4:
                player.badges.add(fifth_win)

        for player in players_without_tenth_win:
            if player.wins >= 9:
                player.badges.add(tenth_win)

        for player in players_without_twentieth_win:
            if player.wins >= 19:
                player.badges.add(twentieth_win)

        for player in players_without_fiftieth_win:
            if player.wins >= 49:
                player.badges.add(fiftieth_win)

        for player in players_without_hundredth_win:
            if player.wins >= 99:
                player.badges.add(hundredth_win)

        for player in players_without_twohundredth_win:
            if player.wins >= 199:
                player.badges.add(twohundredth_win)

        for player in players_without_threehundredth_win:
            if player.wins >= 299:
                player.badges.add(threehundredth_win)

        for player in players_without_fourhundredth_win:
            if player.wins >= 399:
                player.badges.add(fourhundredth_win)

        for player in players_without_fivehundredth_win:
            if player.wins >= 499:
                player.badges.add(fivehundredth_win)
                
        for player in players_without_thousandth_win:
            if player.wins >= 999:
                player.badges.add(thousandth_win)

        for player in players_without_first_match:
            player.badges.add(first_match)

        for player in other_players_without_first_match:
            player.badges.add(first_match)


    elif team2_result == 'win':
        result = 0

        # Add Badges
        first_win_badge = 2
        fifth_win_badge = 3
        tenth_win_badge = 4
        twentieth_win_badge = 5
        fiftieth_win_badge = 6
        hundredth_win_badge = 7
        twohundredth_win_badge = 8
        threehundredth_win_badge = 9
        fourhundredth_win_badge = 10
        fivehundredth_win_badge = 11
        thousandth_win_badge = 12

        first_match_badge = 14

        players_without_first_win = team1.players.exclude(badges__id=first_win_badge)
        players_without_fifth_win = team1.players.exclude(badges__id=fifth_win_badge)
        players_without_tenth_win = team1.players.exclude(badges__id=tenth_win_badge)
        players_without_twentieth_win = team1.players.exclude(badges__id=twentieth_win_badge)
        players_without_fiftieth_win = team1.players.exclude(badges__id=fiftieth_win_badge)
        players_without_hundredth_win = team1.players.exclude(badges__id=hundredth_win_badge)
        players_without_twohundredth_win = team1.players.exclude(badges__id=twohundredth_win_badge)
        players_without_threehundredth_win = team1.players.exclude(badges__id=threehundredth_win_badge)
        players_without_fourhundredth_win = team1.players.exclude(badges__id=fourhundredth_win_badge)
        players_without_fivehundredth_win = team1.players.exclude(badges__id=fivehundredth_win_badge)
        players_without_thousandth_win = team1.players.exclude(badges__id=thousandth_win_badge)
        
        players_without_first_match = team2.players.exclude(badges__id=first_match_badge)
        other_players_without_first_match = team1.players.exclude(badges__id=first_match_badge)

        first_win = Badge.objects.get(id=first_win_badge)
        fifth_win = Badge.objects.get(id=fifth_win_badge)
        tenth_win = Badge.objects.get(id=tenth_win_badge)
        twentieth_win = Badge.objects.get(id=twentieth_win_badge)
        fiftieth_win = Badge.objects.get(id=fiftieth_win_badge)
        hundredth_win = Badge.objects.get(id=hundredth_win_badge)
        twohundredth_win = Badge.objects.get(id=twohundredth_win_badge)
        threehundredth_win = Badge.objects.get(id=threehundredth_win_badge)
        fourhundredth_win = Badge.objects.get(id=fourhundredth_win_badge)
        fivehundredth_win = Badge.objects.get(id=fivehundredth_win_badge)
        thousandth_win = Badge.objects.get(id=thousandth_win_badge)
        first_match = Badge.objects.get(id=first_match_badge)

        for player in players_without_first_win:
            player.badges.add(first_win)

        for player in players_without_fifth_win:
            if player.wins >= 4:
                player.badges.add(fifth_win)

        for player in players_without_tenth_win:
            if player.wins >= 9:
                player.badges.add(tenth_win)

        for player in players_without_twentieth_win:
            if player.wins >= 19:
                player.badges.add(twentieth_win)

        for player in players_without_fiftieth_win:
            if player.wins >= 49:
                player.badges.add(fiftieth_win)

        for player in players_without_hundredth_win:
            if player.wins >= 99:
                player.badges.add(hundredth_win)

        for player in players_without_twohundredth_win:
            if player.wins >= 199:
                player.badges.add(twohundredth_win)

        for player in players_without_threehundredth_win:
            if player.wins >= 299:
                player.badges.add(threehundredth_win)

        for player in players_without_fourhundredth_win:
            if player.wins >= 399:
                player.badges.add(fourhundredth_win)

        for player in players_without_fivehundredth_win:
            if player.wins >= 499:
                player.badges.add(fivehundredth_win)
                
        for player in players_without_thousandth_win:
            if player.wins >= 999:
                player.badges.add(thousandth_win)

        for player in players_without_first_match:
            player.badges.add(first_match)

        for player in other_players_without_first_match:
            player.badges.add(first_match)

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

