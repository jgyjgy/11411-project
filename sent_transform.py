#!/usr/bin/python

from nltk.tree import Tree
from tags import *
from pattern.en import conjugate, lemma

WH = 'wh'
BINARY = 'binary'
# identifies the question as either WH or BINARY, or returns None if unsure
# question_tree is a Tree (directly descended from ROOT)
def q_type(question_tree):
  if question_tree.label() == WH_QUESTION:
    return WH
  elif question_tree.label() == BIN_QUESTION:
    return BINARY
  else:
    return None

# inverts the subj and aux (do-insertion if necessary) to transform the
# declarative sentence into a binary interrogative form
# REQUIRES: sentence_tree is a Tree(S(NP,VP,.))
# RETURNS: a string. The original subj is uncapitalized (if non-proper) but the
# aux is NOT capitalized.
def sent_to_bin_q(sentence_tree):
  assert(sentence_tree.label() == SENTENCE)
  subj = sentence_tree[0]
  assert(subj.label() == NP)
  vp = sentence_tree[1]
  assert(vp.label() == VP)
  head_verb = vp[0]
  assert(is_verb(head_verb.label()))
  verb = head_verb[0]

  # has auxiliary
  if is_modal(head_verb, vp) or lemma(verb) == 'be':
    uncap(subj) # uncapitalize original subj (unless proper noun)
    return ' '.join([verb, tree_to_string(subj), tree_to_string(vp[1])])

  # no auxiliary, use do-insertion
  else:
    head_verb[0] = lemma(verb) # convert head verb to infinitive
    uncap(subj) # uncapitalize original subj (unless proper noun)
    return ' '.join([conjugate('do', get_inflection(head_verb)),
        tree_to_string(subj), tree_to_string(vp)])

# inverts the aux (do-deletion if necessary) and subj to transform the binary
# interrogative into a declarative sentence
# REQUIRES: question_tree is a Tree (directly descended from ROOT)
# RETURNS: a string. The original aux is uncapitalized and the subj is
# capitalized
def bin_q_to_sent(question_tree):
  assert(question_tree.label() == BIN_QUESTION)
  aux = question_tree[0]
  uncap(aux) # uncapitalize the aux
  assert(is_verb(aux.label()))
  subj = question_tree[1]
  assert(subj.label() == NP)
  pred = question_tree[2]
  assert(pred.label() == VP or pred.label() == NP)

  # do-deletion
  if lemma(aux[0]) == 'do':
    assert(is_verb(pred.label()))
    head_verb = pred[0]
    # re-conjugate head verb with inflection of aux 'do'
    head_verb[0] = conjugate(head_verb[0], get_inflection(aux))
    return ' '.join([tree_to_string(subj), tree_to_string(pred)])

  # real (non-do) auxiliary
  else:
    return ' '.join([tree_to_string(subj).capitalize(), aux[0],
        tree_to_string(pred)])

# transforms the apposition 'np1, np2,' into a declarative sentence
def apposition_to_sent(np1, np2):
  head_noun = get_noun(np1)
  assert(head_noun is not None)
  copula = 'are' if is_plural(head_noun.label()) else 'is'
  return ' '.join([tree_to_string(np1), copula, tree_to_string(np2)])

# returns True iff the verb is a modal or auxiliary 'have', 'do'
def is_modal(head_verb, vp):
  return head_verb.label() == MODAL or (lemma(head_verb[0]) in ['have', 'do']
      and vp[1].label() == VP)

# Alias strings
ALIASES = {VERB_PAST: 'p', VERB_PLURAL: 'inf', VERB_3SG: '3sg'}
# returns the alias corresponding to the verb's distinguishable inflection
def get_inflection(verb):
  return ALIASES.get(verb.label())

# returns the noun which heads (possibly indirectly) np
def get_noun(np):
  node = np
  while node.label() == NP:
    moved = False
    for child in node: # move down to the first child which is an NP or noun
      if child.label().startswith('N'):
        node = child
        moved = True
        break
    # no child found, return None
    if not moved:
      return None
  return node

# uncapitalizes the phrase, unless its first word is a proper noun
def uncap(phrase):
  first = first_word(phrase)
  if first.label() != NOUN_PROPER:
    first[0] = first[0].lower()

# gets the leftmost leaf node of tree
def first_word(tree):
  while isinstance(tree[0], Tree):
    tree = tree[0]
  return tree

# converts the tree to string form
def tree_to_string(tree):
  return ' '.join(tree.leaves())
