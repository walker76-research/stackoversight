from typing import Tuple


class TrieNode(object):
    def __init__(self, keyword: str):
        self.keyword = keyword
        self.children = []
        # Is it the last character of the word.`
        self.word_finished = False
        # How many times this character appeared in the addition process
        self.counter = 1


def add(root, keywords: []):
    """
    Adding a word in the trie structure
    """
    node = root
    for keyword in keywords:
        found_in_child = False
        # Search for the character in the children of the present `node`
        for child in node.children:
            if child.keyword == keyword:
                # We found it, increase the counter by 1 to keep track that another
                # word has it as well
                child.counter += 1
                # And point the node to the child that contains this keyword
                node = child
                found_in_child = True
                break
        # We did not find it so add a new chlid
        if not found_in_child:
            new_node = TrieNode(keyword)
            node.children.append(new_node)
            # And then point node to the new child
            node = new_node
    # Everything finished. Mark it as the end of a word.
    node.word_finished = True


def find_prefix(root, keywords: []) -> Tuple[bool, int]:
    """
    Check and return 
      1. If the prefix exists in any of the words we added so far
      2. If yes then how may words actually have the prefix
    """
    node = root
    # If the root node has no children, then return False.
    # Because it means we are trying to search in an empty trie
    if not root.children:
        return False, 0
    for keyword in keywords:
        char_not_found = True
        # Search through all the children of the present `node`
        for child in node.children:
            if child.keyword == keyword:
                # We found the char existing in the child.
                char_not_found = False
                # Assign node as the child containing the char and break
                node = child
                break
        # Return False anyway when we did not find a char.
        if char_not_found:
            return False, 0
    # Well, we are here means we have found the prefix. Return true to indicate that
    # And also the counter of the last node. This indicates how many words have this
    # prefix
    return node.word_finished, node.counter
