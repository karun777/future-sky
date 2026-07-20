# services/astro.py
import datetime as dt

SUN = [
    ("Capricorn",(12,22),( 1,19),"Earth"),
    ("Aquarius", ( 1,20),( 2,18),"Air"),
    ("Pisces",   ( 2,19),( 3,20),"Water"),
    ("Aries",    ( 3,21),( 4,19),"Fire"),
    ("Taurus",   ( 4,20),( 5,20),"Earth"),
    ("Gemini",   ( 5,21),( 6,20),"Air"),
    ("Cancer",   ( 6,21),( 7,22),"Water"),
    ("Leo",      ( 7,23),( 8,22),"Fire"),
    ("Virgo",    ( 8,23),( 9,22),"Earth"),
    ("Libra",    ( 9,23),(10,22),"Air"),
    ("Scorpio",  (10,23),(11,21),"Water"),
    ("Sagittarius",(11,22),(12,21),"Fire"),
]

def parse_birthdate(text: str):
    text = text.strip()
    for f in ("%Y-%m-%d","%d/%m/%Y","%d-%m-%Y","%d %b %Y","%d %B %Y"):
        try:
            return dt.datetime.strptime(text, f).date()
        except ValueError:
            pass
    return None

def compute_sun_sign(b: dt.date):
    md = (b.month, b.day)
    for name, start, end, element in SUN:
        if start <= end:
            if start <= md <= end:
                return name, element
        else:
            if md >= start or md <= end:
                return name, element
    return "Unknown", "Unknown"
