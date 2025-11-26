import lightkurve as lk
import logging

logging.basicConfig(level=logging.INFO)

try:
    print("Searching...")
    search = lk.search_lightcurve("TIC 261136679", mission="TESS", author="SPOC")
    print(f"Found {len(search)} results.")
    if len(search) > 0:
        print("Downloading last one...")
        lc = search[-1].download()
        print("Downloaded:", lc)
    else:
        print("No results.")
except Exception as e:
    print("Error:", e)
