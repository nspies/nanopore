import subprocess
import sys

genome_path = "/oak/stanford/groups/msalit/shared/genomes/hg38/" \
              "GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna"


def run_command(command):
    sys.stderr.write(f"Running command '{command}'...")
    sys.stderr.flush()
    
    subprocess.check_call(command, shell=True)


def run_mapping(fastq, out_bam, threads=1):
    minimap2 = "minimap2"

    # we specify -z because the default seems to spit out alignments that
    # are not particularly contiguous 
    map_command = f"{minimap2} -t {threads} -a -z 600,200 -x map-ont {genome_path} {fastq} " \
                  f"| samtools sort -m 1G -@{threads} -O cram --reference {genome_path} > {out_bam}\n"

    run_command(map_command)


    index_command = f"samtools index {out_bam}"
    run_command(index_command)


def merge_bams(combined_path, bams):
    # merge_command = f"samtools merge -f -O cram --reference {genome_path} {combined_path} {' '.join(bams)}"
    # run_command(merge_command)

    merge_command = f"samtools cat {' '.join(bams)} | samtools sort -@4 -m 2G -O cram --reference {genome_path} -o {combined_path}"
    run_command(merge_command)
    
    run_command(f"samtools index {combined_path}")
