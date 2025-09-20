import datetime


def get_current_semester():
    today = datetime.date.today()
    year = today.year
    month = today.month
    day = today.day
    season = "Summer"
    if (8 <= month < 12) or \
            (month == 12 and day < 20):
        season =  "Fall"
    elif (1 <= month < 5) or \
            (month == 5 and day < 20):
        season =  "Spring"

    return season + f" {year}"


def convert_semester_readable(semester):
    season_code = semester[:2].lower()
    year = semester[2:]

    season_names = {
        'fa': 'Fall',
        'sp': 'Spring',
        'su': 'Summer'
    }

    season = season_names.get(season_code, 'Unknown')
    return f"{season} {year}"


def semester_to_number(semester):
    season_map = {'sp': 0, "su": 1, "fa": 2}
    return int(semester[2:]) * 10 + season_map.get(semester[2:].lower(), -1)