import time, pandas as pd
from textblob import TextBlob
from colorama import Fore, Style, init
init(autoreset=True)

try:
    df = pd.read_csv('imdb_top_1000.csv')
except FileNotFoundError:
    print(Fore.RED + "Error: The file 'imdb_top_1000.csv' was not found")
    raise SystemExit

genres = sorted({g.strip() for xs in df['Genre'] for g in xs.split(',')})

def dots():
    for _ in range(3):
        print(Fore.YELLOW + '.', end='', flush=True)
        time.sleep(0.5)
    print()

def senti(p):
    return 'Positive' if p > 0 else 'Negative' if p < 0 else 'Neutral'

def recommend(genre=None, mood=None, rating=None, n=5):
    d = df

    if genre:
        d = d[d['Genre'].str.contains(genre, case=False, na=False)]

    if rating is not None:
        d = d[d['IMDB_Rating'] >= rating]

    if d.empty:
        return 'No suitable movie recommendation found'

    d = d.sample(frac=1).reset_index(drop=True)
    need_positive = bool(mood)
    out = []

    for _, r in d.iterrows():
        ov = r.get('Overview')
        if pd.isna(ov):
            continue

        pol = TextBlob(ov).sentiment.polarity

        if (not need_positive) or pol >= 0:
            out.append((r['Series_Title'], r['Genre'], r['IMDB_Rating'], pol))

        if len(out) == n:
            break

    return out if out else 'No suitable movie recommendation found'


def random_movie():
    r = df.sample(1).iloc[0]
    ov = r.get('Overview', '')
    pol = TextBlob(ov).sentiment.polarity if pd.notna(ov) else 0

    return [(r['Series_Title'], r['Genre'], r['IMDB_Rating'], pol)]


def show(recs, name):
    print(Fore.YELLOW + f'\n🎬 AI Movie Recommendations for {name}:\n')

    for i, (t, g, rating, p) in enumerate(recs, 1):
        print(Fore.CYAN + f"{i}. {t}")
        print(Fore.GREEN + f"   Genre: {g}")
        print(Fore.MAGENTA + f"   IMDB Rating: {rating}")
        print(Fore.BLUE + f"   Sentiment: {senti(p)} ({p:.2f})\n")


def get_genre():
    print(Fore.GREEN + 'Available Genres:')
    for i, g in enumerate(genres, 1):
        print(Fore.GREEN + f"{i}. {g}")

    while True:
        x = input(Fore.YELLOW + '\nEnter genre number or name: ').strip()

        if x.isdigit() and 1 <= int(x) <= len(genres):
            return genres[int(x) - 1]

        x = x.title()
        if x in genres:
            return x

        print(Fore.RED + 'Invalid input. Try again.\n')


def get_rating():
    while True:
        x = input(Fore.YELLOW + 'Enter minimum IMDB rating (7.6–9.3) or "skip": ').strip()

        if x.lower() == "skip":
            return None

        try:
            r = float(x)
            if 7.6 <= r <= 9.3:
                return r
            print(Fore.RED + 'Rating out of range.\n')
        except ValueError:
            print(Fore.RED + 'Invalid input.\n')


print(Fore.BLUE + '🎬 Welcome to the AI Movie Recommendation System!\n')

name = input(Fore.YELLOW + 'Enter your name: ').strip()
print(Fore.GREEN + f'\nHi {name}! Let’s find some great movies.\n')

choice = input(Fore.YELLOW + "Do you want (1) AI recommendations or (2) Random movie? ").strip()

if choice == '2':
    recs = random_movie()
    show(recs, name)

else:
    genre = get_genre()

    mood = input(Fore.YELLOW + 'How do you feel today? ').strip()
    print(Fore.BLUE + 'Analyzing mood', end='')
    dots()

    mp = TextBlob(mood).sentiment.polarity
    md = 'positive' if mp > 0 else 'negative' if mp < 0 else 'neutral'

    print(Fore.GREEN + f'Your mood is {md} ({mp:.2f})\n')

    rating = get_rating()

    print(Fore.BLUE + 'Finding movies', end='')
    dots()

    recs = recommend(genre, mood, rating)

    if isinstance(recs, str):
        print(Fore.RED + recs)
    else:
        show(recs, name)


while True:
    a = input(Fore.YELLOW + '\nMore recommendations? (yes/no): ').lower()

    if a == 'no':
        print(Fore.GREEN + f'\nEnjoy your movies, {name}!\n')
        break

    elif a == 'yes':
        recs = recommend(genre, mood, rating)
        if isinstance(recs, str):
            print(Fore.RED + recs)
        else:
            show(recs, name)

    else:
        print(Fore.RED + 'Invalid input.\n')