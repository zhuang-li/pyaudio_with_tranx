# coding=utf-8
from asdl.transition_system import TransitionSystem, GenTokenAction

try:
    from cStringIO import StringIO
except:
    from io import StringIO

from collections import Iterable
from asdl.asdl import *
from asdl.asdl_ast import RealizedField, AbstractSyntaxTree

from common.registerable import Registrable
from asdl.lang.nlmap.nlmap_helper import logical_form_to_ast, ast_to_logical_form

def is_equal_ast(hyp_ast, ref_ast):
    hyp_ast_lf = ast_to_logical_form(hyp_ast)
    ref_ast_lf = ast_to_logical_form(ref_ast)
    return ref_ast_lf == hyp_ast_lf


@Registrable.register('nlmap')
class NlmapTransitionSystem(TransitionSystem):
    def compare_ast(self, hyp_ast, ref_ast):
        return is_equal_ast(hyp_ast, ref_ast)

    def ast_to_surface_code(self, asdl_ast):
        return ast_to_logical_form(asdl_ast)

    def surface_code_to_ast(self, code):
        return logical_form_to_ast(self.grammar, code)

    def hyp_correct(self, hyp, example):
        return is_equal_ast(hyp.tree, example.tgt_ast)

    def tokenize_code(self, code, mode):
        return code.strip().split(' ')

    def get_primitive_field_actions(self, realized_field):
        assert realized_field.cardinality == 'single'
        if realized_field.value is not None:
            return [GenTokenAction(realized_field.value)]
        else:
            return []


if __name__ == '__main__':
    pass
