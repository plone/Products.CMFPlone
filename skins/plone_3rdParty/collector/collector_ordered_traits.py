## Script (Python) "collector_ordered_traits.py"
##parameters=traits, order
##title=Return traits list ordered according to second arg, then remainder.

remainder = filter(None, traits[:])
got = []
for i in order:
    if not remainder:
        break
    if i in remainder:
        got.append(i)
        remainder.remove(i)

return got + remainder
