import pprint
from stackapi import StackAPI
SITE = StackAPI('stackoverflow')
comments = SITE.fetch('comments')

for comment_metadata in comments["items"]:
    pprint.pprint(comment_metadata)
