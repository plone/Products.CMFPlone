## Script (Python) "collector_issue_trim_states.py"
##title=Return massaged list of states of issues in catalog.

# Pare out irrelevant states and trim '_confidential' from the rest.

import string

states = context.portal_catalog.uniqueValuesFor('review_state')

got = []
for i in states:
    if i in ['private', 'published', 'pending']:
        continue
    trim = string.split(i, '_')[0]
    if trim not in got:
        got.append(trim)

return got
