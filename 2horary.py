import swisseph as swe
from datetime import datetime, timezone
import itertools
import math

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

def normalize_degrees(degrees):
    """Normalize degrees to 0-360 range."""
    return degrees % 360

def calculate_midpoint(deg1, deg2):
    """Calculate the midpoint between two planetary positions."""
    # Handle the circular nature of degrees
    diff = abs(deg2 - deg1)
    if diff > 180:
        # Take the shorter arc
        if deg1 < deg2:
            midpoint = (deg1 + deg2 + 360) / 2
        else:
            midpoint = (deg1 + deg2 - 360) / 2
    else:
        midpoint = (deg1 + deg2) / 2
    
    return normalize_degrees(midpoint)

def calculate_aspect(deg1, deg2):
    """Calculate the aspect between two planets and return orb."""
    diff = abs(deg1 - deg2)
    if diff > 180:
        diff = 360 - diff
    
    aspects = {
        'Conjunction': (0, 8),
        'Sextile': (60, 6),
        'Square': (90, 8),
        'Trine': (120, 8),
        'Opposition': (180, 8)
    }
    
    for aspect_name, (exact_angle, orb) in aspects.items():
        if abs(diff - exact_angle) <= orb:
            return aspect_name, abs(diff - exact_angle)
    
    return None, None

def get_planet_dignity(planet_name, sign_idx):
    """Determine planetary dignity."""
    dignities = {
        'Sun': {'rulership': [4], 'exaltation': [0], 'detriment': [10], 'fall': [6]},
        'Moon': {'rulership': [3], 'exaltation': [1], 'detriment': [9], 'fall': [7]},
        'Mercury': {'rulership': [2, 5], 'exaltation': [5], 'detriment': [8, 11], 'fall': [11]},
        'Venus': {'rulership': [1, 6], 'exaltation': [11], 'detriment': [0, 7], 'fall': [5]},
        'Mars': {'rulership': [0, 7], 'exaltation': [9], 'detriment': [1, 6], 'fall': [3]},
        'Jupiter': {'rulership': [8, 11], 'exaltation': [3], 'detriment': [2, 5], 'fall': [9]},
        'Saturn': {'rulership': [9, 10], 'exaltation': [6], 'detriment': [3, 4], 'fall': [0]}
    }
    
    if planet_name not in dignities:
        return "Peregrine"
    
    planet_dig = dignities[planet_name]
    
    if sign_idx in planet_dig.get('rulership', []):
        return "Rulership"
    elif sign_idx in planet_dig.get('exaltation', []):
        return "Exaltation"
    elif sign_idx in planet_dig.get('detriment', []):
        return "Detriment"
    elif sign_idx in planet_dig.get('fall', []):
        return "Fall"
    else:
        return "Peregrine"

def calculate_harmonic_chart(planet_positions, harmonic):
    """Calculate harmonic chart positions."""
    harmonic_positions = {}
    for name, pos in planet_positions.items():
        harmonic_pos = normalize_degrees(pos * harmonic)
        harmonic_positions[name] = harmonic_pos
    return harmonic_positions

def find_moon_aspects(moon_pos, moon_speed, planet_positions, jd_ut):
    """Find Moon's last and next aspects."""
    moon_sign = int(moon_pos / 30)
    degrees_to_next_sign = (moon_sign + 1) * 30 - moon_pos
    hours_to_next_sign = degrees_to_next_sign / (moon_speed / 24)  # Convert daily motion to hourly
    
    aspects = []
    
    # Check aspects within the current sign
    for name, pos in planet_positions.items():
        if name == 'Moon':
            continue
            
        aspect_name, orb = calculate_aspect(moon_pos, pos)
        if aspect_name:
            # Calculate if applying or separating
            future_moon_pos = moon_pos + (moon_speed / 24)  # 1 hour ahead
            future_orb = abs(calculate_aspect(future_moon_pos, pos)[1] or 999)
            current_orb = orb
            
            if future_orb < current_orb:
                direction = "Applying"
            else:
                direction = "Separating"
                
            aspects.append({
                'planet': name,
                'aspect': aspect_name,
                'orb': orb,
                'direction': direction
            })
    
    void_of_course = len([a for a in aspects if a['direction'] == 'Applying']) == 0
    
    return aspects, void_of_course, hours_to_next_sign

def main():
    # 1. Get Time (Always UTC for calculation)
    now = datetime.now(timezone.utc)
    decimal_hour = now.hour + now.minute/60 + now.second/3600
    jd_ut = swe.julday(now.year, now.month, now.day, decimal_hour)

    print(f"\n" + "="*60)
    print(f" ADVANCED HORARY CHART: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f" Location: {LAT}, {LON} (Santiago)")
    print("="*60 + "\n")

    # 2. Calculate Houses
    cusps, ascmc = swe.houses_ex(jd_ut, LAT, LON, HOUSE_SYSTEM)

    print("--- HOUSE CUSPS (Regiomontanus) ---")
    print(f"ASC: {get_sign_pos(ascmc[0])}")

    # Handle both 12-element and 13-element tuple variations
    if len(cusps) == 13:
        for i in range(1, 13):
            print(f"House {i:02d}: {get_sign_pos(cusps[i])}")
    else:
        for i in range(len(cusps)):
            print(f"House {i+1:02d}: {get_sign_pos(cusps[i])}")

    print(f"MC:      {get_sign_pos(ascmc[1])}")

    # 3. Calculate Planet Positions and Store Data
    planet_positions = {}
    planet_speeds = {}
    planet_data = {}
    
    print("\n--- PLANET POSITIONS & DIGNITIES ---")
    for name, id in PLANETS.items():
        res, err = swe.calc_ut(jd_ut, id, swe.FLG_SWIEPH | swe.FLG_SPEED)
        
        lon = res[0]
        speed = res[3]
        retro = " (R)" if speed < 0 else ""
        
        planet_positions[name] = lon
        planet_speeds[name] = speed
        
        sign_idx = int(lon / 30)
        dignity = get_planet_dignity(name, sign_idx)
        
        print(f"{name:<8}: {get_sign_pos(lon)}{retro} [{dignity}]")
        
        planet_data[name] = {
            'position': lon,
            'speed': speed,
            'dignity': dignity,
            'retrograde': speed < 0
        }

    # 4. MIDPOINT TREES - The Plutonian Insight
    print("\n--- MIDPOINT TREES (Plutonian Insight) ---")
    midpoints = []
    planet_names = list(planet_positions.keys())
    
    for i, planet1 in enumerate(planet_names):
        for planet2 in planet_names[i+1:]:
            midpoint = calculate_midpoint(planet_positions[planet1], planet_positions[planet2])
            midpoints.append({
                'planets': f"{planet1}/{planet2}",
                'midpoint': midpoint,
                'position': get_sign_pos(midpoint)
            })
    
    # Sort by position for easier reading
    midpoints.sort(key=lambda x: x['midpoint'])
    
    print("Major Midpoints:")
    for mp in midpoints[:10]:  # Show first 10
        print(f"{mp['planets']:<15}: {mp['position']}")

    # 5. HARMONIC CHARTS - The Waveform Analysis
    print("\n--- HARMONIC ANALYSIS (The Waveform) ---")
    
    # 4th Harmonic - Stress patterns
    h4_positions = calculate_harmonic_chart(planet_positions, 4)
    print("4th Harmonic (Stress Patterns):")
    for name, pos in list(h4_positions.items())[:5]:
        print(f"{name:<8}: {get_sign_pos(pos)}")
    
    # 5th Harmonic - Technical talents
    h5_positions = calculate_harmonic_chart(planet_positions, 5)
    print("\n5th Harmonic (Technical Talents):")
    for name, pos in list(h5_positions.items())[:5]:
        print(f"{name:<8}: {get_sign_pos(pos)}")

    # 6. LUNAR ASPECTARIAN - The Pulse
    print("\n--- LUNAR ASPECTARIAN (The Pulse) ---")
    moon_pos = planet_positions['Moon']
    moon_speed = planet_speeds['Moon']
    
    aspects, void_of_course, hours_to_next_sign = find_moon_aspects(
        moon_pos, moon_speed, planet_positions, jd_ut
    )
    
    moon_sign_idx = int(moon_pos / 30)
    moon_dignity = get_planet_dignity('Moon', moon_sign_idx)
    moon_fast = abs(moon_speed) > 13.0  # Average daily motion is ~13°
    
    print(f"Moon Status: {moon_dignity}, {'Fast' if moon_fast else 'Slow'} Motion")
    print(f"Daily Motion: {moon_speed:.2f}°")
    print(f"Hours to Next Sign: {hours_to_next_sign:.1f}")
    print(f"Void of Course: {'YES' if void_of_course else 'NO'}")
    
    if aspects:
        print("\nCurrent Lunar Aspects:")
        for aspect in aspects:
            print(f"  {aspect['direction']} {aspect['aspect']} to {aspect['planet']} (orb: {aspect['orb']:.1f}°)")
    
    # 7. HORARY SUMMARY
    print("\n--- HORARY SUMMARY ---")
    asc_ruler_sign = int(ascmc[0] / 30)
    asc_ruler_planets = {
        0: 'Mars', 1: 'Venus', 2: 'Mercury', 3: 'Moon', 4: 'Sun', 5: 'Mercury',
        6: 'Venus', 7: 'Mars', 8: 'Jupiter', 9: 'Saturn', 10: 'Saturn', 11: 'Jupiter'
    }
    
    chart_ruler = asc_ruler_planets[asc_ruler_sign]
    ruler_dignity = planet_data[chart_ruler]['dignity']
    
    print(f"Chart Ruler: {chart_ruler} in {ruler_dignity}")
    print(f"Moon: {moon_dignity}, {'Applying' if not void_of_course else 'Void of Course'}")
    
    # Find strongest aspect
    if aspects:
        strongest = min(aspects, key=lambda x: x['orb'])
        print(f"Strongest Lunar Aspect: {strongest['direction']} {strongest['aspect']} to {strongest['planet']}")

    print("\n" + "="*60)
    swe.close()

if __name__ == "__main__":
    main()
