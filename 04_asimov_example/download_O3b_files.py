import os
import sys
import pesummary
from pesummary.io import read
from pesummary.gw.fetch import fetch_open_samples
from gwosc.datasets import find_datasets

def match_events(download_events, unique_event_max_versions):
    matches = {}

    # Extract full event names without versions from the O3b release
    unique_events_full = [event.rsplit('-', 1)[0] for event in unique_event_max_versions]

    for download_event in download_events:
        # First check: match full event name (excluding version)
        found = False
        for i, unique_event in enumerate(unique_events_full):
            if download_event == unique_event:
                matches[download_event] = unique_event_max_versions[i]
                found = True
                break

        # Second check: if no full match, try just the GWXXXXXX part
        if not found:
            download_base = download_event.split('_')[0]  # Get GWXXXXXX part
            for i, unique_event in enumerate(unique_events_full):
                if download_base == unique_event.split('_')[0]:
                    matches[download_event] = unique_event_max_versions[i]
                    found = True
                    break

        # If still not found, mark as None
        if not found:
            matches[download_event] = None

    return matches

def main():
    # Check if filename is provided as command line argument
    if len(sys.argv) != 2:
        print("Usage: python download_O3b_files.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    # Get the events from the O3b release
    o4_events_all = find_datasets(type='event', match="GW")
    unique_o4_events = {event.split('-')[0] for event in o4_events_all}
    unique_event_max_versions = sorted([max([e for e in o4_events_all if e.startswith(name)])
                            for name in unique_o4_events])

    # Get the events to run from input file
    try:
        with open(input_file, 'r') as file:
            download_events = [line.strip() for line in file]
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)

    results = match_events(download_events, unique_event_max_versions)

    # Print results and download files
    out_dir = "./"
    os.makedirs(out_dir, exist_ok=True)

    for download_event, matched_event in results.items():
        if matched_event:
            print(f"{download_event} -> {matched_event}")
            # Download the file for the event
            try:
                print(f"Getting: {matched_event}")
                fetch_open_samples(matched_event, unpack=False, read_file=False,
                                 delete_on_exit=False, outdir=out_dir, verbose=True)
            except Exception:
                try:
                    event_no_version = matched_event.split('-')[0]
                    print(f"Second attempt: {event_no_version}")
                    fetch_open_samples(event_no_version, unpack=False, read_file=False,
                                     delete_on_exit=False, outdir=out_dir, verbose=True)
                except:
                    print(f"Downloading {event_no_version} failed")
        else:
            print(f"{download_event} -> No match found")

if __name__ == "__main__":
    main()
