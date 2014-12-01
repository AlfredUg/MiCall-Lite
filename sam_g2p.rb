=begin
Iterate through a CSV (produced by remap.py) where each row contains
 the contents of a SAM file.
Sequences have already been restricted to HIV env V3 if the reads were
 mapped to the 'V3LOOP' region.
Do not attempt to clean sequence based on CIGAR string.
Apply Conan's implementation of the geno2pheno (g2p) coreceptor
 tropism prediction algorithm to each entry.  Output tuples of header,
 g2p score, FPR, and g2p-aligned protein sequence.

Call:
ruby sam_to_g2p.rb <INPUT SAM csv> <OUTPUT scored csv>

Dependencies:
BioRuby
pssm_lib.rb
g2p.matrix
CSV [Ruby module]
=end

require 'csv'
require './pssm_lib'
require 'bio'
require 'ostruct'

QMIN = 20   # minimum base quality within insertions
QCUT = 10   # minimum base quality to not be censored
QDELTA = 5

def parse_options()
  options = OpenStruct.new
  options.remap_csv, options.g2p_csv = ARGV
  raise "Usage: #{__FILE__} remap_csv g2p_csv" unless options.g2p_csv
  
  options
end

# Applies a cigar string to recreate a read, then clips the read.
#
# * <tt>:cigar</tt> - a string in the CIGAR format, describing the relationship
#   between the read sequence and the consensus sequence
# * <tt>:seq</tt> - the sequence that was read
# * <tt>:qual</tt> - quality codes for each base in the read
# * <tt>:pos</tt> - first position of the read, given in consensus coordinates
# * <tt>:clip_from</tt> - first position to include after clipping, given in
#   consensus coordinates
# * <tt>:clip_to</tt> - last position to include after clipping, given in
#   consensus coordinates, nil means no clipping at the end
#
# Returns the new sequence and the new quality string
#
#   apply_cigar_and_clip("12M", "AAACAACCACCC", "AAAAAAAAAAAA", 0, 3, 9)
#   # => "CAACCA", "AAAAAA"
def apply_cigar_and_clip(cigar, seq, qual, pos=0, clip_from=0, clip_to=nil)
  clip_to = clip_to || -1
  newseq = '-' * pos
  newqual = '!' * pos
  is_valid =        /^((\d+)([MIDNSHPX=]))*$/.match(cigar)
  tokens = cigar.scan(/(\d+)([MIDNSHPX=])/)
  raise ArgumentError.new("Invalid CIGAR string: '#{cigar}'.") unless is_valid
  left = 0
  tokens.each do |token|
      length, operation = token
      length = length.to_i
      right = left + length - 1
      if operation == 'M'
          newseq += seq[left..right]
          newqual += qual[left..right]
          left += length
      elsif operation == 'D'
          newseq += '-'*length
          newqual += ' '*length
      elsif operation == 'I'
          its_quals = qual[left..right].unpack('C*') # array of ASCII codes
          if its_quals.map{|asc| asc-33 >= QMIN}.all?
              # accept only high quality insertions
              newseq += seq[left..right]
              newqual += qual[left..right]
          end
          left += length
      elsif operation == 'S'
          left += length
      else
          raise ArgumentError.new("Unsupported CIGAR token: '#{token}'.")
      end
      if left > seq.length
        message = "CIGAR string '#{cigar}' is too long for sequence '#{seq}'."
        raise ArgumentError.new(message)
      end
  end
  if left < seq.length
    message = "CIGAR string '#{cigar}' is too short for sequence '#{seq}'."
    raise ArgumentError.new(message)
  end
  newseq = newseq[clip_from..clip_to]
  newqual = newqual[clip_from..clip_to]
  return newseq, newqual
end

def merge_pairs(seq1, seq2, qual1, qual2)
    mseq = ''
    if seq2.length < seq1.length # make sure seq2 is longer
      seq1, seq2 = seq2, seq1 
      qual1, qual2 = qual2, qual1
    end
    i = 0
    qual1_ints = qual1.unpack('C*')
    qual2_ints = qual2.unpack('C*')
    qual1_ints.map! {|x| x - 33}
    qual2_ints.map! {|x| x - 33}
    
    seq2.each_byte { |b2|
        c2 = b2.chr
        q2 = qual2_ints[i]
        if i < seq1.length
            c1 = seq1[i,1]
            q1 = qual1_ints[i]
            if c1 == '-' and c2 == '-'
                mseq += '-'
            elsif c1 == c2
                if q1 > QCUT or q2 > QCUT
                    mseq += c1
                else
                    mseq += 'N'
                end
            else
                if (q2 - q1).abs >= QDELTA
                    if q1 > [q2, QCUT].max
                        mseq += c1
                    elsif q2 > QCUT
                        mseq += c2
                    else
                        mseq += 'N'
                    end
                else
                    mseq += 'N'
                end
            end
        else
            # past the end of read 1
            if c2 == '-' and q2 == 0
                mseq += 'n' # interval between reads
            else
                if q2 > QCUT
                    mseq += c2
                else
                    mseq += 'N'
                end
            end
        end
        i += 1 # increment at end of loop
    }
    return mseq
end

def main()
  options = parse_options()
  ## convert file contents into hash to collect identical variants
  
  pairs = Hash.new  # cache read for pairing
  merged = Hash.new # tabulate merged sequence variants
  sample_name = ''
  
  CSV.foreach(options.remap_csv) do |row|
      sample_name, qname, flag, rname, pos, mapq, cigar, rnext, pnext, tlen, seq, qual = row
      if rname != 'HIV1B-env-seed'
          # uninteresting region or the header row
          next
      end
      seq1, qual1 = apply_cigar_and_clip(cigar, seq, qual)
      pos1 = pos.to_i-1
      seq2 = '-'*pos1 + seq1 # pad the sequence
      qual2 = '!'*pos1 + qual1
  
      pair = pairs[qname]
      if pair == nil
        # cache this read
        pairs[qname] = {'seq'=>seq2, 'qual'=>qual2}
      else
        # merge reads
        pairs.delete(qname)
        seq1 = pair['seq'] # retrieve from cache
        qual1 = pair['qual']
      
        mseq = merge_pairs(seq1, seq2, qual1, qual2)
      
        count = merged.fetch(mseq, 0)
        merged[mseq] = count + 1
      end
  end  
  
  sorted = merged.sort_by {|k,v| v}.reverse  # sort by count in descending order
  
  ## apply g2p algorithm to merged reads
  f = File.open(options.g2p_csv, mode='w') # write-only
  f.write("sample,rank,count,g2p,fpr,aligned,error\n")  # CSV header
  
  rank = 0
  sorted.each do |s, count|
      rank += 1
      prefix = "#{sample_name},#{rank},#{count}"
      seq = s.delete '-'
      if (seq.count 'N') > (0.5*seq.length)
          # if more than 50% of sequence is garbage
          f.write("#{prefix},,,,low quality\n")
          next
      end
      
      if s.length % 3 != 0
          f.write("#{prefix},,,,notdiv3\n")
          next
      end
    
      if seq.length == 0
        f.write("#{prefix},,,,zerolength\n")
        next
      end
    
      dna = Bio::Sequence.auto(seq)
      prot = dna.translate
  
      # sanity check 1 - bounded by cysteines
      if !prot.match(/^C/) || !prot.match(/C$/)
          f.write("#{prefix},,,#{prot},cysteines\n")
          next
      end
  
      # sanity check 2 - no ambiguous codons
      if prot.count('X') > 0
          f.write("#{prefix},,,#{prot},ambiguous\n")
          next
      end
  
      # sanity check 3 - no stop codons
      if prot.count('*') > 0
          f.write("#{prefix},,,#{prot},stop codons\n")
          next
      end
  
      # sanity check 4 - V3 length in range 32-40 inclusive
      if prot.length < 32 || prot.length > 40
          f.write("#{prefix},,,#{prot},length\n")
          next
      end
  
      score, aligned = run_g2p(seq, $std_v3_g2p, load_matrix('g2p'))
      begin
          aligned2 = aligned.flatten * ""
      rescue
          # sequence failed to align
          f.write("#{prefix},#{score},,,failed to align\n")
          next
      end
      fpr = g2p_to_fpr(score)
      f.write("#{prefix},#{score},#{fpr},#{aligned2},\n")
  end
  
  f.close()
end

if __FILE__ == $0
  main()
end
