##parameters=items,columns=3
##title=format a list of items into columns for better display

# returns a list of lists of items

rows=[]

i=0
l=len(items)

while 1:
    col=[]
    for n in range(columns):
        if i>=l:
            col.append(None)
        else:
            col.append(items[i])
            i=i+1
    rows.append(list(col))
    if i>=l: break

return rows

