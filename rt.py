#TODO Pull posterImage instead of large cover art
#TODO Scrape tv shows (need to also add get_ratings() parameter for movie or show argument)
#TODO Catch missing posterImage: https://www.rottentomatoes.com/assets/pizza-pie/images/poster_default.c8c896e70c3.gif
#TODO Use search query to choose a movie instead of wonky URL
import requests
import re
import json

# URL STRUCTURES
# Movies
# https://www.rottentomatoes.com/m/the_suicide_squad
# https://www.rottentomatoes.com/m/moana_2016
# TV Shows
# https://www.rottentomatoes.com/tv/superman_and_lois
# https://www.rottentomatoes.com/tv/superman_and_lois/s01
# https://www.rottentomatoes.com/tv/superman_and_lois/s01/e01

def get_ratings(media_name: str):
    # audience_icons = {
    #     'N/A': 'https://www.rottentomatoes.com/assets/pizza-pie/images/icons/audience/aud_score-empty.eb667b7a1c7.svg',
    #     'spilled': 'https://www.rottentomatoes.com/assets/pizza-pie/images/icons/audience/aud_score-rotten.f419e4046b7.svg',
    #     'upright': 'https://www.rottentomatoes.com/assets/pizza-pie/images/icons/audience/aud_score-fresh.6c24d79faaf.svg'
    # }

    critic_icons = {
        'N/A': 'https://www.rottentomatoes.com/assets/pizza-pie/images/icons/tomatometer/tomatometer-empty.cd930dab34a.svg',
        'rotten': 'https://www.rottentomatoes.com/assets/pizza-pie/images/icons/tomatometer/tomatometer-rotten.f1ef4f02ce3.svg',
        'fresh': 'https://www.rottentomatoes.com/assets/pizza-pie/images/icons/tomatometer/tomatometer-fresh.149b5e8adc3.svg',
        'certified-fresh': 'https://www.rottentomatoes.com/assets/pizza-pie/images/icons/tomatometer/certified_fresh.75211285dbb.svg'
    }

    footer_icon = 'https://www.rottentomatoes.com/assets/pizza-pie/images/favicon.ico'

    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
    headers = {
        'User-Agent': ua
    }

    # Movie
    media_type = 'm'
    # Television
    # media_type = 'tv'

    media_name = media_name
    media_name_formatted = media_name.replace(' ', '_').replace('-', '_').replace(',', '_').replace('.', '').replace(':', '').replace('\'', '').replace('&', 'and').lower()

    url = f'https://www.rottentomatoes.com/{media_type}/{media_name_formatted}'

    plot_regex = r'<div id="movieSynopsis" class="movie_synopsis clamp clamp-6 js-clamp" style="clear:both" data-qa="movie-info-synopsis">\s+(.+)\s+</div>'
    score_details_regex = r'<script id="score-details-json" type="application/json">(.+)</script>'
    cover_art_regex = r'<meta property="og:image" content="(.+)">'

    r = requests.get(url, headers=headers)

    src = r.text
    link = r.url

    if media_type == 'm':
        cover_art_matches = re.search(cover_art_regex, src)
        cover_art = cover_art_matches.group(1)
        plot_matches = re.search(plot_regex, src)
        plot = plot_matches.group(1)
        score_details_matches = re.search(score_details_regex, src)
        score_details_json_data = json.loads(score_details_matches.group(1))

        scoreboard = score_details_json_data['scoreboard']
        audience_banded_rating_count = scoreboard['audienceBandedRatingCount']
        audience_rating_copy = scoreboard['audienceRatingCopy']

        if scoreboard['audienceScore'] == "":
            audience_score = "--%"
        else:
            audience_score = scoreboard['audienceScore'] + "%"

        # audience_state = scoreboard['audienceState'] # N/A, spilled, upright

        info = scoreboard['info']
        rating = scoreboard['rating']
        
        embed_desc = f"{rating} | {info}\n\n{plot}"
        
        title = scoreboard['title']
        tomatometer_count = scoreboard['tomatometerCount']

        if scoreboard['tomatometerScore'] == "":
            tomatometer_score = "--%"
        else:
            tomatometer_score = scoreboard['tomatometerScore'] + "%"

        tomatometer_state = scoreboard['tomatometerState'] # N/A, rotten, fresh, certified-fresh
        
        thumbnail_icon = critic_icons[tomatometer_state]
    else:
        pass
        # print("TV show stat scraping not yet implemented.")
    return footer_icon, link, cover_art, audience_banded_rating_count, audience_rating_copy, audience_score, embed_desc, title, tomatometer_count, tomatometer_score, thumbnail_icon