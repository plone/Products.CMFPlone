## Script (Python) "createMultiColumnList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=input_list,numCols=3, sort_on=None
##title=Turn a single list into a list of lists for multi column display

""" This method turns a list into a list of sublists for multi-column display.
    The number of sublists is determined by the numCols parameter.  The
    initial list may optionally be sorted based on the sort_on property, which
    should be the name of a property or method on the list items or the string
    'self', which will cause the list to be sorted in place without a sort
    function.
"""

from zExceptions import Forbidden
if container.REQUEST.get('PUBLISHED') is script:
    raise Forbidden('Script may not be published.')

list_len = len(input_list)

if sort_on and sort_on != 'self':
    # function for generating sort attribute (if callable)
    get_sort_attr = lambda x: (
                        callable(getattr(x, sort_on, None)) and
                        getattr(x, sort_on)() or
                        getattr(x, sort_on, None))

    dec_list = [(get_sort_attr(l), l) for l in input_list]
    dec_list.sort()
    input_list = [l[1] for l in dec_list]
elif sort_on == 'self':
    input_list.sort()

# Calculate the length of the sublists
sublist_len = (
    list_len % numCols == 0 and
    list_len / numCols or
    list_len / numCols + 1)

# Calculate the list end point given the list number
list_end = lambda list_num: (
                list_num == numCols - 1 and
                list_len or
                (list_num + 1) * sublist_len)

# Generate columns
final_lists = [input_list[i * sublist_len:list_end(i)] for i in range(numCols)]

return final_lists
