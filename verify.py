import random
import hashlib
import json
import sys

# --- Configuration ---
PARTICIPANTS_FILE = "participants.json" # Must match the file used by main.py

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

NUM_UNIQUE_PARTICIPANTS = len(participants_weights)

print("=" * 50)
print("       Raffle Verification Tool")
print("=" * 50)

# --- Get Inputs for Verification ---
base_seed_to_verify = input("Enter the EXACT Base Seed used for the draw: ").strip()
nonce_to_verify = input("Enter the EXACT Nonce generated for the draw: ").strip()

while True:
    try:
        num_winners_to_verify = int(input(f"Enter the Number of Winners announced for the draw (max {NUM_UNIQUE_PARTICIPANTS}): ").strip())
        if 0 < num_winners_to_verify <= NUM_UNIQUE_PARTICIPANTS:
            break
        elif num_winners_to_verify > NUM_UNIQUE_PARTICIPANTS:
             print(f"Warning: Draw requested {num_winners_to_verify} winners, but only {NUM_UNIQUE_PARTICIPANTS} unique participants exist.")
             print("Will verify based on drawing max unique participants.")
             num_winners_to_verify = NUM_UNIQUE_PARTICIPANTS # Adjust verification target
             break
        else:
             print("Number of winners must be positive.")
    except ValueError:
        print("Invalid input. Please enter a whole number.")

print("-" * 50)
print("Verifying...")

# --- Re-Build Weighted Entry List ---
full_entry_list = []
for person, weight in participants_weights.items():
    if not isinstance(weight, int) or weight <= 0:
         # We don't need to print warnings here, just ensure logic matches main.py
         continue
    full_entry_list.extend([person] * weight)

if not full_entry_list:
     print("Error: No valid participants found in the loaded data.")
     sys.exit(1)

# --- Re-Calculate Final Seed ---
try:
    combined_string = f"{base_seed_to_verify}-{nonce_to_verify}"
    final_seed_hex = hashlib.sha256(combined_string.encode('utf-8')).hexdigest()
except Exception as e:
    print(f"Error during hash calculation: {e}")
    sys.exit(1)

# --- Re-Seed PRNG ---
random.seed(final_seed_hex)

# --- Re-Shuffle List ---
shuffled_list = full_entry_list[:]
random.shuffle(shuffled_list)

# --- Re-Select Unique Winners ---
derived_winners = []
drawn_participants = set()
for participant in shuffled_list:
    if participant not in drawn_participants:
        derived_winners.append(participant)
        drawn_participants.add(participant)
        if len(derived_winners) == num_winners_to_verify:
             break # Stop when intended number is reached

# --- Output Verification Results ---
print("\n" + "=" * 50)
print("       Verification Calculation Results")
print("=" * 50)
print(f"Using Base Seed: '{base_seed_to_verify}'")
print(f"Using Nonce:     '{nonce_to_verify}'")
print(f"Calculated Final Seed (SHA-256): '{final_seed_hex}'")
print(f"Verifying for {num_winners_to_verify} winner(s).")
print("-" * 50)
print("Derived Winners (based on these inputs):")

if not derived_winners:
     print("No winners could be derived with the provided inputs.")
else:
    for i, winner in enumerate(derived_winners):
        print(f"{i+1}. {winner}")

print("=" * 50)
print("\nACTION: Compare the 'Derived Winners' list above to the")
print("winners announced for the specific raffle run you are verifying.")
print("-> If they MATCH EXACTLY, the original draw is verified.")
print("-> If they DO NOT MATCH, check your inputs (Base Seed, Nonce, Num Winners)")
print("   or ensure the participants.json file hasn't changed since the draw.")
print("=" * 50)
