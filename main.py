import pprint
from stackapi import StackAPI, StackAPIError
SITE = StackAPI('stackoverflow')
comments = SITE.fetch('comments')

post_ids = []
for comment_metadata in comments["items"]:
    # pprint.pprint(comment_metadata)
    post_ids.append(comment_metadata['post_id'])

post_ids = post_ids[:20]
try:
    posts = SITE.fetch('posts', ids=post_ids)
    # pprint.pprint(post_text)
except StackAPIError as e:
    print(e.message)
    exit(-1)

for post_metadata in posts["items"]:
    pprint.pprint(post_metadata)
