# coding=utf-8
import os

import torch

from asdl.lang.py.dataset import Django
from asdl.lang.py.py_utils import tokenize_code
import ast
import astor

from model import nn_utils
from model.neural_lm import LSTMLanguageModel


class Prior(object):
    def __init__(self):
        pass

    def __call__(self, code_list):
        raise NotImplementedError

    def eval(self):
        pass


class UniformPrior(Prior):
    def __init__(self, **kwargs):
        super(UniformPrior, self).__init__()

    def __call__(self, code_list):
        return [0. for code in code_list]


class LSTMPrior(LSTMLanguageModel, Prior):
    def __init__(self, args, vocab):
        super(LSTMPrior, self).__init__(vocab, args.embed_size, args.hidden_size, args.dropout)

        self.args = args

    def __call__(self, code_list):
        # we assume the code is generated from astor and therefore has an astor style!
        code_tokens = [tokenize_code(code, mode='canonicalize') for code in code_list]
        code_var = nn_utils.to_input_variable(code_tokens, self.vocab,
                                              cuda=self.args.cuda, append_boundary_sym=True)

        return -self.forward(code_var)

    @classmethod
    def load(self, model_path, cuda=False):
        params = torch.load(model_path, map_location=lambda storage, loc: storage)
        params['args'].cuda = cuda
        model = LSTMPrior(params['args'], params['vocab'])
        model.load_state_dict(params['state_dict'])

        return model

    def save(self, file_path):
        dir_name = os.path.dirname(file_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        params = {
            'args': self.args,
            'vocab': self.vocab,
            'state_dict': self.state_dict()
        }

        torch.save(params, file_path)
