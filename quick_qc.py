import numpy
import pysam
import sys
import tqdm

def n50(values, fraction=0.5):
    if len(values) < 5:
        return numpy.nan
    values = values.copy()
    values.sort()
    
    cumsum = numpy.cumsum(values)
    sum_ = cumsum[-1]
    
    i = numpy.where(cumsum>=fraction*sum_)[0][0]
    
    return values[i]
    
def coverages(lengths, cutoffs):
    covs = []
    for cutoff in cutoffs:
        cur_lengths = lengths[lengths >= cutoff]
        covs.append(cur_lengths.sum() / 3.1e9)
    return covs
    
def do_qc(path):
    inf = pysam.AlignmentFile(path)
    
    read_lengths = []
    unmapped_count = 0
    unmapped_bases = 0

    for count, read in tqdm.tqdm(enumerate(inf)):
        if read.is_secondary or read.is_supplementary:
            continue
        if read.is_unmapped:
            unmapped_bases += read.query_length
            unmapped_count += 1
            continue

        read_lengths.append(read.query_alignment_length)
        if count > 200000:
            print("ENDING EARLY:", read)
            break
        
    read_lengths = numpy.array(read_lengths)

    print(f"Number of mapped reads: {len(read_lengths):,} (excludes supplementary and secondary alignments)")
    print(f"Number of unmapped reads: {unmapped_count:,}")
    print(f"Number of unmapped bases: {unmapped_bases:,}")

    print(f"N50: {n50(read_lengths):,}")
    cutoffs = [0, 10e3, 25e3, 50e3, 100e3, 250e3, 500e3]
    covs = coverages(read_lengths, cutoffs)
    for cutoff, cov in zip(cutoffs, covs):
        print(f" coverage by reads >= {cutoff:>10,}: {cov:.3f}x ({cov/covs[0]:6.1%})")
    
    print("Top read lengths:")
    read_lengths.sort()
    
    for length in read_lengths[:-11:-1]:
        print(f" {length:,}")
                

if __name__ == "__main__":
        do_qc(sys.argv[1])
