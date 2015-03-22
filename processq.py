#!/usr/bin/python

from nltk.corpus import wordnet as wn
from nltk.tree import Tree
from tags_and_patterns import *
from answer_types import *

# returns (expected answer type, synsets) for the given question_tree
# synsets is None except for the "what/which NP" case
# if wh-question, deletes the question key_node from question_tree
def answer_type(question_tree):
  (parent, key_node_index) = get_question_key_node(question_tree)
  key_node = parent[key_node_index]
  key_label = key_node.label()
  result = None
  synsets = None

  # binary question
  if is_verb(key_label):
    result = BINARY

  else:
    # who/whose, what, which, how many/much __
    if key_label == WHNP:
      wh_word = key_node[0][0].lower()
      if wh_word == 'who' or wh_word == 'whose':
        result = PERSON
      elif wh_word == 'what' or wh_word == 'which':
        result = THING
      if key_node[0].label() == WDT: # wh-word head with noun complement
        if wh_word in ['what', 'which'] and key_node[-1].label().startswith('NN'):
          synsets = wn.synsets(key_node[1][0], pos=wn.NOUN)
      elif key_node[0].label() == WHADJP: # how many/much __
        result = AMOUNT

    # where, when, why, how
    elif key_label == WHADVP:
      wh_word = key_node[0][0].lower()
      answer_types = {'where': PLACE, 'when': TIME, 'why': REASON, 'how': MANNER}
      result = answer_types[wh_word]

    # singleton how many/much
    elif key_node.label() == WHADJP:
      result = AMOUNT

    # delete key_node from question_tree
    del parent[key_node_index]

  return (result, synsets)

# DFSes (L-to-R) for the question type-identifying node
# - for wh questions, wh keyword can be preceded by PP
# - for binary questions, verb should be first
# returns (parent, key_node_index) where key_node_index is the index in parent
# where the key_node is. This facilitates removal of the key_node
def get_question_key_node(curr_node):
  for i in xrange(len(curr_node)):
    if is_key_node(curr_node[i].label()):
      return (curr_node, i)
    else:
      if isinstance(curr_node[i], Tree): 
        child_key_node = get_question_key_node(curr_node[i])
        if child_key_node is not None:
          return child_key_node
  return None

# returns True iff the label is a WH-phrase or verb (Vxx or MD)
def is_key_node(label):
  return label.startswith('WH') or is_verb(label)