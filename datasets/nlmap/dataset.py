# coding=utf-8
from __future__ import print_function
import sys

from asdl.hypothesis import Hypothesis, ApplyRuleAction
from asdl.lang.nlmap.nlmap_transition_system import *
from asdl.asdl import ASDLGrammar
from components.action_info import get_action_infos
from components.dataset import Example
from components.vocab import VocabEntry, Vocab
from asdl.lang.nlmap.nlmap_helper import *

try: import cPickle as pickle
except: import pickle

import numpy as np


def load_dataset(transition_system, dataset_file):
    examples = []
    src_length_sum = 0
    tgt_length_sum = 0
    for idx, line in enumerate(open(dataset_file)):
        src_query, tgt_code = line.strip().split('\t')

        src_query_tokens = src_query.split(' ')
        #print (tgt_code)
        tgt_ast = logical_form_to_ast(transition_system.grammar, tgt_code)
        reconstructed_prolog_expr = ast_to_logical_form(tgt_ast)
        #print (tgt_code)
        #print (reconstructed_prolog_expr)
        #print(tgt_ast.to_string())
        assert tgt_code == reconstructed_prolog_expr

        tgt_actions = transition_system.get_actions(tgt_ast)

        # sanity check
        hyp = Hypothesis()
        for action in tgt_actions:
            assert action.__class__ in transition_system.get_valid_continuation_types(hyp)
            #print("action before instance", action.production)
            if isinstance(action, ApplyRuleAction):
                #print("action after instance", action.production)
                #print ("grammar type", transition_system.get_valid_continuating_productions(hyp))
                assert action.production in transition_system.get_valid_continuating_productions(hyp)
            hyp = hyp.clone_and_apply_action(action)

        assert hyp.frontier_node is None and hyp.frontier_field is None

        assert is_equal_ast(hyp.tree, tgt_ast)

        expr_from_hyp = transition_system.ast_to_surface_code(hyp.tree)
        assert expr_from_hyp == tgt_code

        tgt_action_infos = get_action_infos(src_query_tokens, tgt_actions)
        #print (idx)
        print ("length of src query tokens is {}".format(len(src_query_tokens)))
        print ("length of target actions is {}".format(len(tgt_actions)))
        print ("ratio of target src is {}".format(len(tgt_actions)/len(src_query_tokens)))
        src_length_sum += len(src_query_tokens)
        tgt_length_sum += len(tgt_actions)
        #print (tgt_action_infos)
        example = Example(idx=idx,
                          src_sent=src_query_tokens,
                          tgt_actions=tgt_action_infos,
                          tgt_code=tgt_code,
                          tgt_ast=tgt_ast,
                          meta=None)

        examples.append(example)
    print("avg ratio of target src is {}".format(tgt_length_sum / src_length_sum))
    return examples


def prepare_dataset():
    # vocab_freq_cutoff = 1 for atis
    vocab_freq_cutoff = 2  # for geo query
    grammar = ASDLGrammar.from_text(open('../../asdl/lang/nlmap/nlmap_asdl.txt').read())
    transition_system = NlmapTransitionSystem(grammar)

    train_set = load_dataset(transition_system, '../../data/nlmap/train.txt')
    test_set = load_dataset(transition_system, '../../data/nlmap/test.txt')

    # generate vocabulary
    src_vocab = VocabEntry.from_corpus([e.src_sent for e in train_set], size=5000, freq_cutoff=vocab_freq_cutoff)

    primitive_tokens = [map(lambda a: a.action.token,
                            filter(lambda a: isinstance(a.action, GenTokenAction), e.tgt_actions))
                        for e in train_set]

    primitive_vocab = VocabEntry.from_corpus(primitive_tokens, size=5000, freq_cutoff=0)

    # generate vocabulary for the code tokens!
    code_tokens = [transition_system.tokenize_code(e.tgt_code, mode='decoder') for e in train_set]
    code_vocab = VocabEntry.from_corpus(code_tokens, size=5000, freq_cutoff=0)

    vocab = Vocab(source=src_vocab, primitive=primitive_vocab, code=code_vocab)
    print('generated vocabulary %s' % repr(vocab), file=sys.stderr)

    action_len = [len(e.tgt_actions) for e in chain(train_set, test_set)]
    print('Max action len: %d' % max(action_len), file=sys.stderr)
    print('Avg action len: %d' % np.average(action_len), file=sys.stderr)
    print('Actions larger than 100: %d' % len(list(filter(lambda x: x > 100, action_len))), file=sys.stderr)

    pickle.dump(train_set, open('../../data/nlmap/train.bin', 'wb'))
    pickle.dump(test_set, open('../../data/nlmap/test.bin', 'wb'))
    pickle.dump(vocab, open('../../data/nlmap/vocab.freq2.bin', 'wb'))


if __name__ == '__main__':
    prepare_dataset()
