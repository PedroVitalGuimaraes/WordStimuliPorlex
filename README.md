# Lexical Stimuli Selection from Porlex

A Python script to select and organize words drawn from the **Porlex v3** lexical database (Gomes, Castro, Lima & Mesquita, 2019).

## What the script does

1. Reads the `Porlex_v3_2019.xlsx` file (sheet `Porlex_v3`).
2. Filters the words that simultaneously meet:
   - `Nlet` (number of letters) between **7 and 10**
   - `CGram` (grammatical class) in **Adjective, Verb, Noun**
   - `FreqL` (lexical frequency) between **38 and 62**
3. Renames the variables:
   - `CGram` → **Grammatical Class (G)**
   - `Nlet` → **Length (C)**
   - `FreqL` → **Frequency (F)**
4. Randomly selects **80 words** (fixed seed = 42, for reproducibility).
5. Splits the 80 words into 2 lists of 40:
   - **Target Words**
   - **Distractor Words**
6. Each list of 40 is split into 2 groups of 20:
   - Target Words → **L1** and **L1A**
   - Distractor Words → **L2** and **L2A**
7. **L1** and **L1A** are further split into 4 blocks of 5 words each, numbered sequentially from **Block 1 to Block 8**.
8. For **L2** and **L2A** (also in blocks 1 to 8), the following is computed and displayed at the end of each block:
   - Mean and standard deviation of **Length**
   - Mean and standard deviation of **Frequency**
   - Distribution of grammatical classes, in the order **Verb, Noun, Adjective**

## Requirements

```bash
pip install pandas openpyxl
```

## Usage

1. Place the `Porlex_v3_2019.xlsx` file in the same folder as the script.
2. Run:

```bash
python select_stimuli.py
```

## Generated files

| File | Content |
|---|---|
| `filtered_words.csv` | All words that meet the filtering criteria |
| `selected_words_80.csv` | The 80 randomly selected words |
| `target_words_40.csv` | The 40 Target Words |
| `distractor_words_40.csv` | The 40 Distractor Words |
| `L1_blocks.txt` | L1 split into Blocks 1–4 |
| `L1A_blocks.txt` | L1A split into Blocks 5–8 |
| `L2_blocks.txt` | L2 split into Blocks 1–4, with statistics per block |
| `L2A_blocks.txt` | L2A split into Blocks 5–8, with statistics per block |

## Data source

Gomes, I., Castro, S. L., Lima, C. F., & Mesquita, A. B. (2019). *Porlex v3, uma base lexical do Português*. FPCE-UP. \
https://sigarra.up.pt/fpceup/pt/web_base.gera_pagina?p_pagina=NCL_DATABASES \
https://projetoler.pt/texto/porlex

