import swisseph as swe
from datetime import datetime, timezone

# --- CONFIG ---
# Your coordinates
LAT = -33.44
LON = -70.66
NOW = datetime.now(timezone.utc)

# --- BODIES TO DUMP ---
# 0-9 = Sun through Pluto
# 10-13 = Nodes & Moon variations (excluding Earth at ID 14)
# 15-20 = Chiron, Pholus, Ceres, Pallas, Juno, Vesta
PLANET_IDS = list(range(0, 10)) + list(range(10, 14)) + list(range(15, 21))

FIXED_STARS = ["Sirius", "Canopus", "Arcturus", "Vega", "Capella", "Rigel", "Procyon", "Betelgeuse", "Algol", "Aldebaran", "Spica", "Antares", "Regulus"]

ZODIAC = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]

def fmt_pos(deg):
    """Format decimal degrees to Zodiac notation"""
    sign = int(deg / 30)
    d = int(deg % 30)
    m = int((deg % 1) * 60)
    s = int(((deg % 1) * 60 % 1) * 60)
    return f"{d:02d} {ZODIAC[sign]} {m:02d}'{s:02d}\""

def main():
    # 1. Calculate Julian Day
    decimal_hour = NOW.hour + NOW.minute/60 + NOW.second/3600
    jd = swe.julday(NOW.year, NOW.month, NOW.day, decimal_hour)

    # 2. Set Topocentric (Surface) Coordinates for maximum precision
    swe.set_topo(LON, LAT, 0) # 0 meters altitude

    print(f"--- SWISSEPH DUMP: {NOW} UTC ---")
    print(f"Julian Day: {jd}")
    print(f"Delta T:    {swe.deltat(jd)} sec")

    # 3. Dump Planets & Asteroids
    print("\n" + "="*95)
    print(f"{'ID':<4} {'BODY':<12} {'LONGITUDE':<18} {'LATITUDE':<12} {'DIST (AU)':<12} {'SPEED (deg/day)':<15}")
    print("="*95)

    for pid in PLANET_IDS:
        try:
            # FLG_SWIEPH = Use Ephemeris file
            # FLG_SPEED  = Calculate speed
            # FLG_TOPOCTR = View from your location (not center of Earth)
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_TOPOCTR

            # Get name
            name = swe.get_planet_name(pid)

            # Calculate
            # res = [longitude, latitude, distance, speed_long, speed_lat, speed_dist]
            res, flags = swe.calc_ut(jd, pid, flags)

            retro = " (R)" if res[3] < 0 else ""

            print(f"{pid:<4} {name:<12} {fmt_pos(res[0]):<18} {res[1]:>8.4f}°  {res[2]:>10.5f}   {res[3]:>10.5f}{retro}")
        except swe.Error:
            pass # Skip if ephemeris file missing for asteroids

    # 4. Dump Fixed Stars
    #print("\n" + "="*95)
    #print(f"{'FIXED STAR':<17} {'LONGITUDE':<18} {'LATITUDE':<12} {'MAGNITUDE':<12}")
    #print("="*95)

    #for star in FIXED_STARS:
    #    try:
            # res = [long, lat, dist] (Stars don't really have speed in this context)
    #        res, flags = swe.fixstar2_ut(star, jd, swe.FLG_SWIEPH | swe.FLG_TOPOCTR)
            # Not all star returns give magnitude easily in Python wrapper, usually static lookup
     #       print(f"{star:<17} {fmt_pos(res[0]):<18} {res[1]:>8.4f}°")
     #   except swe.Error as e:
     #       print(f"Error {star}: {e}")

    # 5. Dump House Cusps
    print("\n" + "="*40)
    print("HOUSE CUSPS (Regiomontanus)")
    print("="*40)

    # 'R' = Regiomontanus, 'P' = Placidus, 'W' = Whole Sign
    cusps, ascmc = swe.houses_ex(jd, LAT, LON, b'R')

    print(f"ASC: {fmt_pos(ascmc[0])}")
    print(f"MC:  {fmt_pos(ascmc[1])}")

    for i, cusp in enumerate(cusps):
        if i == 0: continue # Cusp 0 is usually empty in the tuple
        print(f"House {i + 1}: {fmt_pos(cusp)}")

    print("\n" + "="*40)
    print("AYANAMSA (Sidereal Offset)")
    print("="*40)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    print(f"Lahiri Ayanamsa: {swe.get_ayanamsa_ut(jd):.4f}°")

if __name__ == "__main__":
    main()
