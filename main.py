import random
import hashlib
import secrets
import datetime
import json
import sys

# --- Configuration ---
NUM_WINNERS = 3
BASE_SEED = "CorvusEliteRaffle_April142025_WeightedEntries" # Set your raffle's base seed
PARTICIPANTS_FILE = "participants.json"

# --- Load Participants ---
try:
    with open(PARTICIPANTS_FILE, 'r') as f:
        participants_weights = json.load(f)
    if not isinstance(participants_weights, dict):
        raise ValueError("JSON file should contain a dictionary (object).")
    if not participants_weights:
        raise ValueError("Participant file is empty.")
except FileNotFoundError:
    print(f"Error: Participant file not found at '{PARTICIPANTS_FILE}'")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from '{PARTICIPANTS_FILE}'. Check format.")
    sys.exit(1)
except ValueError as e:
    print(f"Error loading participants: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred loading participants: {e}")
    sys.exit(1)

# --- Build Weighted Entry List ---
full_entry_list = []
for person, weight in participants_weights.items():
    if not isinstance(weight, int) or weight <= 0:
         print(f"Warning: Invalid weight '{weight}' for participant '{person}'. Skipping.", file=sys.stderr)
         continue
    full_entry_list.extend([person] * weight)

if not full_entry_list:
    print("Error: No valid participants found after processing weights.")
    sys.exit(1)

total_entries = len(full_entry_list)
num_unique_participants = len(participants_weights)

if NUM_WINNERS > num_unique_participants:
    print(f"Warning: Requesting {NUM_WINNERS} winners, but only {num_unique_participants} unique participants exist.", file=sys.stderr)
    print(f"Adjusting to draw {num_unique_participants} winner(s).", file=sys.stderr)
    NUM_WINNERS = num_unique_participants

# --- Generate Nonce ---
nonce = secrets.token_hex(16)
draw_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

# --- Combine Base Seed and Nonce, then Hash ---
combined_string = f"{BASE_SEED}-{nonce}"
final_seed_hex = hashlib.sha256(combined_string.encode('utf-8')).hexdigest()

# --- Seed the PRNG ---
random.seed(final_seed_hex)

# --- Shuffle the List ---
shuffled_list = full_entry_list[:]
random.shuffle(shuffled_list)

# --- Select Unique Winners ---
winners = []
drawn_participants = set()
for participant in shuffled_list:
    if participant not in drawn_participants:
        winners.append(participant)
        drawn_participants.add(participant)
        if len(winners) == NUM_WINNERS:
            break

# --- Output Results ---
print("=" * 50)
print(f"       Nonce + Seed Raffle Results ({NUM_WINNERS} Winners)")
print("=" * 50)
print(f"Draw Timestamp (UTC): {draw_timestamp}")
print(f"Number of Winners Drawn: {len(winners)}") # Actual number drawn
print(f"Total Weighted Entries: {total_entries}")
print(f"Unique Participants: {num_unique_participants}")
print("-" * 50)
print(f"Base Seed: '{BASE_SEED}'")
print(f"Nonce Generated: '{nonce}'")
print(f"Final Seed (SHA-256 Hash): '{final_seed_hex}'")
print("-" * 50)
print("           🏆 WINNERS 🏆")
if winners:
    for i, winner in enumerate(winners):
        print(f"{i+1}. {winner}")
else:
    print("No winners were drawn.")
print("=" * 50)
print("VERIFICATION INFO: Record the 'Base Seed' and 'Nonce Generated'.")
print("Use verify.py with these values to confirm the results.")
print("=" * 50)
