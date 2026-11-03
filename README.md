# GFF3 Feature Exporter

Extract a single feature's FASTA sequence from a GFF3 annotation file, selected by feature type and attribute key/value.

A GFF3 file can carry both the annotation feature table and the FASTA sequence of the molecules it describes, separated by a `##FASTA` directive. This tool parses both sections in one pass, locates the requested feature, pulls the corresponding subsequence by coordinate, reverse-complements it when the feature is on the minus strand, and prints it as standard-format FASTA.

## Usage

    python3 export_gff3_feature.py \
        --source_gff=/path/to/annotation.gff3 \
        --type=gene \
        --attribute=ID \
        --value=YAR003W

| Argument | GFF3 column | Description |
|---|---|---|
| `--source_gff` | — | Path to the GFF3 file |
| `--type` | 3 | Feature type to match (`gene`, `mRNA`, `CDS`, …) |
| `--attribute` | 9 | Attribute key (`ID`, `Name`, `Parent`, …) |
| `--value` | 9 | Attribute value to match |

Output is written to STDOUT.

## Example

`mini.gff3` is included so the tool can be run without the original dataset.

A plus-strand feature:

    $ python3 export_gff3_feature.py --source_gff=mini.gff3 --type=gene --attribute=ID --value=GENE001
    >gene:ID:GENE001
    AAAACCCCGGGGTTTTACGT

`GENE002` sits on the minus strand, so its sequence comes back reverse-complemented:

    $ python3 export_gff3_feature.py --source_gff=mini.gff3 --type=gene --attribute=ID --value=GENE002
    >gene:ID:GENE002
    TGCATTTTGGGGCCCCAAAA

A query that matches nothing exits cleanly rather than crashing:

    $ python3 export_gff3_feature.py --source_gff=mini.gff3 --type=gene --attribute=ID --value=NOPE
    WARNING: No features matched your query.

## Behavior

- **Strand-aware** — minus-strand features are reverse-complemented
- **Spec-compliant output** — sequence wrapped at 60 characters per line
- **Single-pass parsing** — feature table and embedded `##FASTA` block read in one traversal
- **No match** — warns and exits cleanly
- **Multiple matches** — warns, then exports the first
- **Missing sequence** — warns if the feature's `seqid` has no corresponding FASTA entry

## Validation

Developed and validated against the *Saccharomyces cerevisiae* S288C genome annotation across four test cases — three features present in the file and one deliberately absent, to confirm graceful handling of the empty-result case.

The S288C annotation file is not redistributed here; it is available from [SGD](https://www.yeastgenome.org/).

## Requirements

Python 3, standard library only.

## Context

Final project for **AS.410.634 Practical Computer Concepts for Bioinformatics** — M.S. Bioinformatics, Johns Hopkins University, Fall 2025.
