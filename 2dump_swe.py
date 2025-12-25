import swisseph as swe
from datetime import datetime, timezone

# --- CONFIG ---
LAT = -33.44
LON = -70.66
NOW = datetime.now(timezone.utc)

# Planet IDs (Excluding Earth 14)
PLANET_IDS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20]

ZODIAC = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]

def fmt_pos(deg):
    sign = int(deg / 30)
    d = int(deg % 30)
    m = int((deg % 1) * 60)
    s = int(((deg % 1) * 60 % 1) * 60)
    return f"{d:02d} {ZODIAC[sign]} {m:02d}'{s:02d}\""

def main():
    # 1. Setup Time
    decimal_hour = NOW.hour + NOW.minute/60 + NOW.second/3600
    jd = swe.julday(NOW.year, NOW.month, NOW.day, decimal_hour)
    swe.set_topo(LON, LAT, 0)

    print(f"\n{'='*105}")
    print(f" SWISSEPH MASTER DUMP: {NOW.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"{'='*105}")

    # 2. Cosmic Constants
    res, _ = swe.calc_ut(jd, swe.ECL_NUT, 0)
    # res contains: [nut_long, nut_obl, true_obl, mean_obl, ...]
    nut_long, nut_obl, true_obl, mean_obl = res[0], res[1], res[2], res[3]
    eot = swe.time_equ(jd) 
    
    print(f"Julian Day:      {jd:.5f}")
    print(f"Equation of Time: {eot * 1440:.2f} minutes")
    print(f"True Obliquity:   {true_obl:.5f}°")
    print(f"Nutation Long:    {nut_long:.5f}°")

    # 3. Planetary Data
    print(f"\n{'='*105}")
    print(f"{'ID':<3} {'BODY':<10} {'LONGITUDE':<15} {'LAT':<7} {'DIST(AU)':<9} {'SPEED':<9} {'MAG':<5} {'PHASE':<6} {'HOUSE'}")
    print(f"{'='*105}")

    # Calculate houses to get ARMC (ascmc[2])
    cusps, ascmc = swe.houses_ex(jd, LAT, LON, b'R')
    
    for pid in PLANET_IDS:
        try:
            name = swe.get_planet_name(pid)
            
            # Position & Speed
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_TOPOCTR
            p_res, _ = swe.calc_ut(jd, pid, flags)
            
            # Phenomena (Magnitude/Phase)
            try:
                pheno, _ = swe.pheno_ut(jd, pid, swe.FLG_SWIEPH)
                mag = f"{pheno[4]:.1f}"
                phase = f"{pheno[1]*100:.0f}%"
            except:
                mag, phase = "-", "-"

            # --- THE FIXED HOUSE POSITION CALL ---
            # Signature decoded: (armc, geolat, eps, [obj_lon, obj_lat], hsys)
            h_val = swe.house_pos(ascmc[2], LAT, true_obl, [p_res[0], p_res[1]], b'R')
            h_num = int(h_val)

            retro = " (R)" if p_res[3] < 0 else ""
            
            print(f"{pid:<3} {name:<10} {fmt_pos(p_res[0]):<15} {p_res[1]:>7.2f} {p_res[2]:>9.4f} {p_res[3]:>8.3f}{retro:<3} {mag:<5} {phase:<6} {h_num}")

        except swe.Error:
            continue

    # 4. House Cusps
    print(f"\n{'='*40}")
    print(f" HOUSE CUSPS (Regiomontanus)")
    print(f"{'='*40}")
    print(f"ASC: {fmt_pos(ascmc[0])}")
    print(f"MC:  {fmt_pos(ascmc[1])}")
    for i in range(1, 13):
        print(f"House {i:02}: {fmt_pos(cusps[i])}")

    # 5. Fixed Stars
    print(f"\n{'='*40}")
    print(f" MAJOR FIXED STARS")
    print(f"{'='*40}")
    stars = ["Sirius", "Spica", "Antares", "Regulus", "Algol"]
    for s in stars:
        try:
            s_res, _ = swe.fixstar2_ut(s, jd, swe.FLG_SWIEPH)
            print(f"{s:<10} {fmt_pos(s_res[0])}")
        except:
            continue

    # 6. Eclipse Data
    print(f"\n{'='*40}")
    print(f" ECLIPSE PREDICTION")
    print(f"{'='*40}")
    try:
        res, tret = swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH)
        y, m, d, h = swe.revjul(tret[0])
        print(f"Next Solar: {y}-{m:02d}-{d:02d}")
        
        res, tret = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH)
        y, m, d, h = swe.revjul(tret[0])
        print(f"Next Lunar: {y}-{m:02d}-{d:02d}")
    except:
        print("Detailed eclipse files not found.")

if __name__ == "__main__":
    main()
    swe.close()
