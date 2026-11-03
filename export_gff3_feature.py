#!/usr/bin/env python3
#export_gff3_feature.py
#Program - Export a feature's FASTA sequence from a GFF3 file

import argparse    #Reads command-line arguments
import sys         #For exiting program on demand

def reverse_complement(sequence):    #Function to compute reverse complement of DNA sequence, if on minus strand
        complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
        reverse_seq = reversed(sequence)  #Reverses the sequence
        reverse_complement_str = ""
        for base in reverse_seq:
                reverse_complement_str += complement[base]  #Adds complementary bases
        return reverse_complement_str  #Returns reverse-complemented string

def wrap_sequence(sequence, width=60):  #Function to wrap a sequence to fixed-width FASTA format
        wrapped = ""
        for i in range(0, len(sequence), width):
                wrapped += sequence[i:i+width] + "\n"
        return wrapped.rstrip("\n")  #Remove trailing newline

parser = argparse.ArgumentParser(description="Export a feature from a GFF3 file") #Create argument parser
parser.add_argument("--source_gff", required=True) #input GFF3 file
parser.add_argument("--type", required=True)       #input feature type
parser.add_argument("--attribute", required=True)  #input attribute key
parser.add_argument("--value", required=True)      #input attribute value
args = parser.parse_args()   #parse arguments

source_gff = args.source_gff  #storing input values
feature_type = args.type
attribute_key = args.attribute
attribute_value = args.value

matches = []   #list to store matching features
fasta_sequences = {}  #dictionary to store FASTA sequences
in_fasta = False
current_fasta_id = ""
current_fasta_seq = ""

with open(source_gff, "r") as file: #Opening GFF3 file
        for line in file:           #Read file line by line
                line = line.strip() #Remove whitespace and newline

                if line == "##FASTA":
                        in_fasta = True
                        continue

                if not in_fasta:
                        if line.startswith("#") or line.strip() == "":
                                continue

                        columns = line.split("\t")   #split GFF3 columns

                        if len(columns) != 9:
                                continue

                        sequence_id = columns[0]
                        ftype = columns[2]
                        start = columns[3]
                        end = columns[4]
                        strand = columns[6]
                        attributes = columns[8]

                        if ftype != feature_type:
                                continue

                        for attr in attributes.split(";"):  #split attributes
                                if attr.startswith(attribute_key + "="):
                                        if attr.split("=")[1].endswith(attribute_value):
                                                matches.append({"sequence_id": sequence_id, "start": int(start), "end": int(end), "strand": strand})

                else:    #Parse FASTA section
                        if line.startswith(">"):   #FASTA header line
                                if current_fasta_id != "":
                                        fasta_sequences[current_fasta_id] = current_fasta_seq
                                current_fasta_id = line[1:].split()[0]   #get FASTA ID
                                current_fasta_seq = ""
                        else:
                                current_fasta_seq += line.strip().upper()   #append sequence data

if current_fasta_id:
        fasta_sequences[current_fasta_id] = current_fasta_seq

if len(matches) == 0:    #check if no matching features were found
        print("WARNING: No features matched your query.")
        sys.exit(0)

if len(matches) > 1:
        print("WARNING: More than one feature matched your query. Exporting the first match.")

feature = matches[0]
sequence_id = feature["sequence_id"]
start = feature["start"]
end = feature["end"]
strand = feature["strand"]

if sequence_id not in fasta_sequences:    #Ensure FASTA sequence exists for chromosome
        print("WARNING: FASTA sequence for '{}' not found in file.".format(sequence_id))
        sys.exit(0)

full_sequence = fasta_sequences[sequence_id]   #full chromosome sequence
sub_sequence = full_sequence[start - 1:end]    #extract feature sequence

if strand == "-":    #check strand orientation
        sub_sequence = reverse_complement(sub_sequence)  #reverse complement if on minus strand

print(">{}:{}:{}".format(feature_type, attribute_key, attribute_value))   #prints FASTA header
print(wrap_sequence(sub_sequence, 60))   #print wrapped sequence
