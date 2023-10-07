# -*- coding: utf-8 -*-
"""
Created on Sun Jan 20 11:14:52 2019

@author: GWAllison

These tools are used to check input CASRN for validity (in a strict sense) and 
also to try to coerce inputs with minor issues into valid CASRN.
"""
import re
import string

### na_check appears to be a testing remnant of early problems that have been fixed.
### doesn't seem to be necessary!
# def na_check(df,collst=['CASNumber','IngredientName',
#                         'OperatorName','Supplier'],
#              txt = '',
#              verbose=True): # without verbose, this routine is useless work!
#     """Used to flag the unexpected condition of NaN in some columns.  Only
#     reports if this condition is found. """
#     printed_header = False
#     for col in collst:
#         if col in df.columns:
#             num = df[col].isna().sum()
#             if num>0:
#                 if not printed_header:
#                     printed_header=True
#                     if verbose:
#                         print(f'  ** NaN check: {txt} **')
#                 miss = (df[col]=='missing').sum()
#                 MISS = (df[col]=='MISSING').sum()
#                 if verbose:
#                     print(f'     -- {col} has {num} NA, {miss} missing and {MISS} MISSING')
#                     print(f'        -- NAs: \n{df[df[col].isna()][["CASNumber","IngredientName","OperatorName","Supplier"]]}')
                    
def is_valid_CAS_code(cas):
    """Returns boolean.
    
    Checks if number follows strictest format of CAS registry numbers:
        
    - three sections separated by '-', 
    - section 1 is 2-7 digits with no leading zeros, 
    - section 2 is two digits (no dropping leading zero),
    - section 3 (check digit) is just one digit that satisfies validation algorithm.
    - No extraneous characters."""
    try:
        for c in cas:
            err = False
            if c not in '0123456789-': 
                err = True
                break
        if err: return False
        lst = cas.split('-')
        if len(lst)!=3 : return False
        if len(lst[2])!=1 : return False # check digit must be a single digit
        if lst[0][0] == '0': return False # leading zeros not allowed
        s1int = int(lst[0])
        if s1int > 9999999: return False
        if s1int < 10: return False
        s2int = int(lst[1])
        if s2int > 99: return False
        if len(lst[1])!=2: return False # must be two digits, even if <10

        # validate test digit
        teststr = lst[0]+lst[1]
        teststr = teststr[::-1] # reverse for easy calculation
        accum = 0
        for i,digit in enumerate(teststr):
            accum += (i+1)*int(digit)
        if accum%10 != int(lst[2]):
            return False
        return True
    except:
        # some other problem
        return False


def cleanup_cas(cas):
    """Returns string.
    
    Removes extraneous characters and adjusts zeros where needed:
        
    - need two digits in middle segment and no leading zeros in first.
    Note that we DON'T check CAS validity, here. Just cleanup. 
    
    ** When an input has a single digit in the middle segment (two are required),
    this routine assumes the other digit is a missing leading zero.**
    
    If the routine cannot coerce into a valid CASRN safely, the original (non-valid) 
    input is returned.
    
    """
    cas = re.sub(r'[^0-9-]','',cas)
    lst = cas.split('-') # try to break into three segments
    if len(lst) != 3: return cas # not enough pieces - return filtered cas
    if len(lst[2])!= 1: return cas # can't do anything here with malformed checkdigit
    if len(lst[1])!=2:
        if len(lst[1])==1:     #NOTE this makes the assumption of a missing leading zero!
            lst[1] = '0'+lst[1]
        else:
            return cas # wrong number of digits in chunk2 to fix here
    lst[0] = lst[0].lstrip('0')
    if (len(lst[0])<2 or len(lst[0])>7): return cas # too many or two few digits in first segment
    
    return f'{lst[0]}-{lst[1]}-{lst[2]}'

    

##### Utility routines not used directly in production code but useful for 
##### testing and development
# def has_non_printable(s):
#     for c in s:
#         if not c in string.printable:
#             print(f'has non-printable {ord(c)} in {s}') 
#             return True
#     return False

# def show_ord(s):
#     t = ''
#     for c in s:
#         t+= f'{ord(c)}-'
#     print(t)

# def gen_check_digit(left='7732', middle='18'):
#     teststr = left+middle
#     teststr = teststr[::-1] # reverse for easy calculation
#     accum = 0
#     for i,digit in enumerate(teststr):
#         accum += (i+1)*int(digit)
#     print(accum%10)

