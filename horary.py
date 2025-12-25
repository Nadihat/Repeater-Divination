import swisseph as swe
from datetime import datetime, timezone

# --- CONFIGURATION ---
LAT = -33.4489  # Santiago
LON = -70.6693
# Using Regiomontanus (Standard for Horary)
HOUSE_SYSTEM = b'R' 

ZODIAC = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
    "Node": swe.MEAN_NODE # Critical for Horary
}

def get_sign_pos(decimal_degrees):
    """Converts 360° to Sign, Degrees, Minutes."""
    sign_idx = int(decimal_degrees / 30)
    sign_name = ZODIAC[sign_idx]
    deg = int(decimal_degrees % 30)
    minutes = int((decimal_degrees % 1) * 60)
    return f"{deg:02d}° {sign_name} {minutes:02d}'"

def main():
    # 1. Get Time (Always UTC for calculation)
    now = datetime.now(timezone.utc)
    decimal_hour = now.hour + now.minute/60 + now.second/3600
    jd_ut = swe.julday(now.year, now.month, now.day, decimal_hour)

    print(f"\n" + "="*40)
    print(f" HORARY CHART: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f" Location: {LAT}, {LON} (Santiago)")
    print("="*40 + "\n")

    # 2. Calculate and Print Houses
    # Returns (cusps, ascmc)
    # 2. Calculate and Print Houses
    cusps, ascmc = swe.houses_ex(jd_ut, LAT, LON, HOUSE_SYSTEM)

    print("--- HOUSE CUSPS (Regiomontanus) ---")
    print(f"ASC: {get_sign_pos(ascmc[0])}")

    # Handle both 12-element and 13-element tuple variations
    if len(cusps) == 13:
        # 1-indexed version (standard C-style)
        for i in range(1, 13):
            print(f"House {i:02d}: {get_sign_pos(cusps[i])}")
    else:
        # 0-indexed version (standard Python-style)
        for i in range(len(cusps)):
            print(f"House {i+1:02d}: {get_sign_pos(cusps[i])}")

    print(f"MC:      {get_sign_pos(ascmc[1])}")
    # 3. Calculate and Print Planets
    print("\n--- PLANET POSITIONS ---")
    for name, id in PLANETS.items():
        # FLG_SWIEPH uses high-precision ephemeris
        # FLG_SPEED gives us the daily motion (to check if Retrograde)
        res, err = swe.calc_ut(jd_ut, id, swe.FLG_SWIEPH | swe.FLG_SPEED)
        
        lon = res[0]
        speed = res[3]
        retro = " (R)" if speed < 0 else ""
        
        print(f"{name:<8}: {get_sign_pos(lon)}{retro}")

    print("\n" + "="*40)
    swe.close()

if __name__ == "__main__":
    main()
