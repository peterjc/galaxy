#! /usr/bin/python
# this is a tool that creates new row/s
#Done by: Guru

"""
Get Flanking regions.

usage: %prog input out_file size direction
   -l, --cols=N,N,N,N: Columns for chrom, start, end, strand in file
"""

import sys, sets, re, os
import cookbook.doc_optparse
import pkg_resources
pkg_resources.require( "bx-python" )
from galaxyops import *
   
def main():   
    # Parsing Command Line here
    options, args = cookbook.doc_optparse.parse( __doc__ )
    
    try:
        chr_col_1, start_col_1, end_col_1, strand_col_1 = parse_cols_arg( options.cols )
        inp_file, out_file, size, direction = args
        size = int(size)
        if strand_col_1 == -1:
            strand = "+"        #if strand is not defined, default it to +
    except:
        cookbook.doc_optparse.exception()
        
    try:
        fi = open(inp_file,'r')
    except:
        print >> sys.stderr, "Unable to open input file"
        sys.exit()
    try:
        fo = open(out_file,'w')
    except:
        print >> sys.stderr, "Unable to open output file"
        sys.exit()
        
    skipped_lines = 0
    first_invalid_line = 0
    invalid_line = None
    elems = []
    j=0
    for i, line in enumerate( open( inp_file )):
        line = line.strip()
        if line and (not line.startswith( '#' )) and line != '':
            j+=1
            try:
                elems = line.split('\t')
                #if the start and/or end columns are not numbers, skip that line.
                assert int(elems[start_col_1])
                assert int(elems[end_col_1])
                if strand_col_1 != -1:
                    strand = elems[strand_col_1]
                #if the stand value is not + or -, skip that line.
                assert strand in ['+', '-']
                if direction == 'Upstream':
                    if strand == '+':
                        elems[end_col_1] = elems[start_col_1]
                        elems[start_col_1] = str(int(elems[start_col_1]) - size)
                    elif strand == '-':
                        elems[start_col_1] = elems[end_col_1]
                        elems[end_col_1] = str(int(elems[end_col_1]) + size)
                    print >>fo, '\t'.join(elems)
                    
                elif direction == 'Downstream':
                    if strand == '-':
                        elems[end_col_1] = elems[start_col_1]
                        elems[start_col_1] = str( int(elems[start_col_1]) - size )
                    elif strand == '+':
                        elems[start_col_1] = elems[end_col_1]
                        elems[end_col_1] = str(int(elems[end_col_1]) + size)
                    print >>fo, '\t'.join(elems)
                
                elif direction == 'Both':
                    newelem1 = str(int(elems[start_col_1]) - size)
                    newelem2 = elems[start_col_1]
                    newelem3 = elems[end_col_1]
                    newelem4 = str(int(elems[end_col_1]) + size)
                    elems[start_col_1]=newelem1
                    elems[end_col_1]=newelem2
                    print >>fo, '\t'.join(elems)
                    elems[start_col_1]=newelem3
                    elems[end_col_1]=newelem4
                    print >>fo, '\t'.join(elems)
            
            except:
                skipped_lines += 1
                if not invalid_line:
                    first_invalid_line = i + 1
                    invalid_line = line
    fo.close()
    
    #If number of skipped lines = num of lines in the file, inform the user to check metadata attributes of the input file.
    if skipped_lines == j:
        print 'Data issue: Skipped all lines in your input. Check the metadata attributes of the chosen input by clicking on the pencil icon next to it.'
        sys.exit()
    elif skipped_lines > 0:
        print '(Data issue: skipped %d invalid lines starting at line #%d which is "%s")' % ( skipped_lines, first_invalid_line, invalid_line )
    print 'Flank length : %d and location : %s ' %(size, direction)
    
if __name__ == "__main__":
    main()