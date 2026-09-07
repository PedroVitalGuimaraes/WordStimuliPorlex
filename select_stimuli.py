"""
Script to select and organize lexical stimuli from Porlex v3.

Data source: Porlex v3 (Gomes, Castro, Lima & Mesquita, 2019),
a lexical database of European Portuguese ("Porlex_v3" sheet).

The script:
 1. Reads the Porlex v3 Excel file.
 2. Filters words with:
      - Nlet (number of letters)      between 7 and 10
      - CGram (grammatical class)     in {Adjective, Verb, Noun}
      - FreqL (lexical frequency)     between 38 and 62
 3. Renames the variables:
      CGram -> Grammatical Class (G)
      Nlet  -> Length (C)
      FreqL -> Frequency (F)
 4. Randomly selects 80 words from the filtered set.
 5. Splits the 80 words into two lists of 40:
      - Target Words
      - Distractor Words
 6. Each list of 40 is split into 2 groups: L1, L1A (from the Target list)
    and L2, L2A (from the Distractor list).
 7. L1 and L1A are further split into 4 blocks of 5 words (Block 1 to 8,
    numbered sequentially across L1 then L1A).
 8. For the L2 and L2A blocks (Block 1 to 8), the following are computed
    and written at the end of each block:
      - mean and standard deviation of Length
      - mean and standard deviation of Frequency
      - grammatical class distribution (order: Verb, Noun, Adjective)

Requirements: pandas, openpyxl
    pip install pandas openpyxl

Usage:
    Place the file "Porlex_v3_2019.xlsx" in the same folder as the script
    and run:
    python select_stimuli.py
"""

import random
import statistics as st
import pandas as pd

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
EXCEL_FILE = "Porlex_v3_2019.xlsx"
SHEET = "Porlex_v3"

SEED = 42                 # ensures reproducibility of the random sample
N_TOTAL = 80               # total number of words to select
N_PER_LIST = 40            # words per list (Target / Distractor)
N_PER_GROUP = 20           # words per group (L1, L1A, L2, L2A)
N_PER_BLOCK = 5            # words per block

NLET_MIN, NLET_MAX = 7, 10
FREQ_MIN, FREQ_MAX = 38, 62
VALID_CLASSES = {"no": "Noun", "vb": "Verb", "aj": "Adjective"}

random.seed(SEED)


# ----------------------------------------------------------------------
# 1. Loading and filtering the database
# ----------------------------------------------------------------------
def load_and_filter(file=EXCEL_FILE, sheet=SHEET):
    df = pd.read_excel(file, sheet_name=sheet, header=0)

    # The relevant columns in the Porlex v3 database are named
    # "Orto" (word), "CGram", "Nlet" and "FreqL".
    # Since the sheet has 2 unnamed leading columns (index and the word
    # itself), we locate the word column by position (column B).
    df = df.rename(columns={df.columns[1]: "Orto"})

    df = df[["Orto", "CGram", "Nlet", "FreqL"]].copy()
    df = df.dropna(subset=["Orto", "CGram", "Nlet", "FreqL"])

    mask = (
        df["Nlet"].between(NLET_MIN, NLET_MAX)
        & df["FreqL"].between(FREQ_MIN, FREQ_MAX)
        & df["CGram"].isin(VALID_CLASSES.keys())
    )
    filtered = df[mask].copy()

    # Rename the variables as requested
    filtered["Grammatical Class (G)"] = filtered["CGram"].map(VALID_CLASSES)
    filtered = filtered.rename(
        columns={"Nlet": "Length (C)", "FreqL": "Frequency (F)"}
    )
    filtered = filtered[
        ["Orto", "Grammatical Class (G)", "Length (C)", "Frequency (F)"]
    ]
    filtered = filtered.rename(columns={"Orto": "Word"})
    filtered = filtered.reset_index(drop=True)

    if len(filtered) < N_TOTAL:
        raise ValueError(
            f"Only {len(filtered)} words meet the criteria; "
            f"at least {N_TOTAL} are required."
        )
    return filtered


# ----------------------------------------------------------------------
# 2. Random selection of 80 words
# ----------------------------------------------------------------------
def select_80(df_filtered):
    return df_filtered.sample(n=N_TOTAL, random_state=SEED).reset_index(drop=True)


# ----------------------------------------------------------------------
# 3. Splitting into lists, groups and blocks
# ----------------------------------------------------------------------
def split_into_lists_and_groups(df80):
    target_words = df80.iloc[:N_PER_LIST].reset_index(drop=True)
    distractor_words = df80.iloc[N_PER_LIST:].reset_index(drop=True)

    l1 = target_words.iloc[:N_PER_GROUP].reset_index(drop=True)
    l1a = target_words.iloc[N_PER_GROUP:].reset_index(drop=True)

    l2 = distractor_words.iloc[:N_PER_GROUP].reset_index(drop=True)
    l2a = distractor_words.iloc[N_PER_GROUP:].reset_index(drop=True)

    return target_words, distractor_words, l1, l1a, l2, l2a


def split_into_blocks(group, starting_block_number):
    """Splits a group of 20 words into 4 blocks of 5, returning
    a dictionary {"Block N": DataFrame}."""
    blocks = {}
    for i in range(4):
        block_name = f"Block {starting_block_number + i}"
        start = i * N_PER_BLOCK
        end = start + N_PER_BLOCK
        blocks[block_name] = group.iloc[start:end].reset_index(drop=True)
    return blocks


# ----------------------------------------------------------------------
# 4. Block statistics (Length, Frequency, Grammatical Class)
# ----------------------------------------------------------------------
def compute_block_statistics(block):
    lengths = block["Length (C)"].tolist()
    frequencies = block["Frequency (F)"].tolist()

    mean_length = st.mean(lengths)
    sd_length = st.stdev(lengths) if len(lengths) > 1 else 0.0
    mean_freq = st.mean(frequencies)
    sd_freq = st.stdev(frequencies) if len(frequencies) > 1 else 0.0

    counts = block["Grammatical Class (G)"].value_counts()
    n_verb = int(counts.get("Verb", 0))
    n_noun = int(counts.get("Noun", 0))
    n_adjective = int(counts.get("Adjective", 0))

    return {
        "Mean Length": round(mean_length, 2),
        "SD Length": round(sd_length, 2),
        "Mean Frequency": round(mean_freq, 2),
        "SD Frequency": round(sd_freq, 2),
        "Verb": n_verb,
        "Noun": n_noun,
        "Adjective": n_adjective,
    }


# ----------------------------------------------------------------------
# 5. Writing results to text/CSV files
# ----------------------------------------------------------------------
def write_simple_list(file_name, title, block_groups):
    """Writes L1 / L1A: only the blocks of 5 words, without statistics."""
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(f"{title}\n")
        f.write("=" * len(title) + "\n\n")
        for block_name, block in block_groups.items():
            f.write(f"-- {block_name} --\n")
            for _, row in block.iterrows():
                f.write(
                    f"  {row['Word']:<15} "
                    f"Grammatical Class (G)={row['Grammatical Class (G)']:<10} "
                    f"Length (C)={int(row['Length (C)'])}  "
                    f"Frequency (F)={row['Frequency (F)']}\n"
                )
            f.write("\n")


def write_list_with_statistics(file_name, title, block_groups):
    """Writes L2 / L2A: the blocks of 5 words followed by the statistics
    (mean/SD of Length and Frequency, and Verb/Noun/Adjective distribution)."""
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(f"{title}\n")
        f.write("=" * len(title) + "\n\n")
        for block_name, block in block_groups.items():
            f.write(f"-- {block_name} --\n")
            for _, row in block.iterrows():
                f.write(
                    f"  {row['Word']:<15} "
                    f"Grammatical Class (G)={row['Grammatical Class (G)']:<10} "
                    f"Length (C)={int(row['Length (C)'])}  "
                    f"Frequency (F)={row['Frequency (F)']}\n"
                )
            stats = compute_block_statistics(block)
            f.write(
                f"  >> Mean Length = {stats['Mean Length']}  "
                f"SD Length = {stats['SD Length']}\n"
            )
            f.write(
                f"  >> Mean Frequency = {stats['Mean Frequency']}  "
                f"SD Frequency = {stats['SD Frequency']}\n"
            )
            f.write(
                f"  >> Grammatical Class distribution -> "
                f"Verb = {stats['Verb']}, Noun = {stats['Noun']}, "
                f"Adjective = {stats['Adjective']}\n\n"
            )


# ----------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------
def main():
    df_filtered = load_and_filter()
    df_filtered.to_csv("filtered_words.csv", index=False, encoding="utf-8-sig")

    df80 = select_80(df_filtered)
    df80.to_csv("selected_words_80.csv", index=False, encoding="utf-8-sig")

    target_words, distractor_words, l1, l1a, l2, l2a = (
        split_into_lists_and_groups(df80)
    )
    target_words.to_csv("target_words_40.csv", index=False, encoding="utf-8-sig")
    distractor_words.to_csv(
        "distractor_words_40.csv", index=False, encoding="utf-8-sig"
    )

    # L1 and L1A: Blocks 1-4 and 5-8 (no statistics)
    blocks_l1 = split_into_blocks(l1, starting_block_number=1)
    blocks_l1a = split_into_blocks(l1a, starting_block_number=5)

    write_simple_list("L1_blocks.txt", "L1 - Target Words (Group 1)", blocks_l1)
    write_simple_list(
        "L1A_blocks.txt", "L1A - Target Words (Group 2)", blocks_l1a
    )

    # L2 and L2A: Blocks 1-4 and 5-8 (with statistics at the end of each block)
    blocks_l2 = split_into_blocks(l2, starting_block_number=1)
    blocks_l2a = split_into_blocks(l2a, starting_block_number=5)

    write_list_with_statistics(
        "L2_blocks.txt", "L2 - Distractor Words (Group 1)", blocks_l2
    )
    write_list_with_statistics(
        "L2A_blocks.txt", "L2A - Distractor Words (Group 2)", blocks_l2a
    )

    print("Process complete. Generated files:")
    print(" - filtered_words.csv")
    print(" - selected_words_80.csv")
    print(" - target_words_40.csv")
    print(" - distractor_words_40.csv")
    print(" - L1_blocks.txt")
    print(" - L1A_blocks.txt")
    print(" - L2_blocks.txt  (with statistics)")
    print(" - L2A_blocks.txt (with statistics)")


if __name__ == "__main__":
    main()
