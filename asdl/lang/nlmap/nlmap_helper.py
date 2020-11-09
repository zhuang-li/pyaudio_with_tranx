# -*- coding: utf-8 -*-
# coding=utf-8
from asdl.lang.nlmap.node import Node

import copy
from io import StringIO
import re
from collections import Iterable

from asdl.asdl import *
from asdl.asdl_ast import AbstractSyntaxTree, RealizedField

from os.path import dirname, abspath
import os


def parse_nlmap_expr_helper(nlmap_tokens, start_idx):
    i = start_idx
    name = nlmap_tokens[i]
    node = Node(name)
    i += 1
    if nlmap_tokens[i] == '(':
        i += 1
        while True:
            if nlmap_tokens[i] == ',':
                # and
                i += 1
            child_node, end_idx = parse_nlmap_expr_helper(nlmap_tokens, i)
            node.add_child(child_node)
            i = end_idx

            if i >= len(nlmap_tokens): break
            if nlmap_tokens[i] == ')':
                i += 1
                break

    return node, i

def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

    """
    inner = anony_keyval(keyval* one)
    query_u = anony_area_nwr(area one, nwr* two)
    query_u = anony_nwr(nwr* one)
    meta_req = anony_meta_req_meta_req(meta_req one, meta_req two)
    meta_req = anony_meta_req_meta_pos(meta_req one, meta_pos two)
    """
def check_production(grammar, stack, look_ahead_node):
    """
    inner = anony_keyval(keyval* one)
    query_u = anony_area_nwr(area one, nwr* two)
    query_u = anony_nwr(nwr* one)
    meta_req = anony_meta_req_meta_req(meta_req one, meta_req two)
    meta_req = anony_meta_req_meta_pos(meta_req one, meta_pos two)
    """
    while True:
        node = stack.pop()
        if node.production.type.name == 'keyval' and \
                ((not look_ahead_node) or
                 ((not look_ahead_node.production.type.name == 'keyval') and (not look_ahead_node.production.type.name == 'inner'))):
                prod = grammar.get_prod_by_ctr_name("anony_keyval")
                ast_node = AbstractSyntaxTree(prod, [RealizedField(prod['one'], node)])
                stack.append(ast_node)
        elif node.production.type.name == 'nwr' and \
                ((not look_ahead_node) or
                 (not look_ahead_node.production.type.name == 'keyval')):
            ast_node = None
            nwr_queue = []
            nwr_queue.append(node)
            while stack:
                node = stack.pop()
                if node.production.type.name == 'nwr':
                    nwr_queue.append(node)
                else:
                    if node.production.type.name == 'area':
                        prod = grammar.get_prod_by_ctr_name("anony_area_nwr")
                        var_field_one = RealizedField(prod['one'], node)
                        nwr_queue.reverse()
                        var_field_two = RealizedField(prod['two'], nwr_queue)
                        ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two])
                        break
                    else:
                        stack.append(node)
                        break
            if not ast_node:
                prod = grammar.get_prod_by_ctr_name("anony_nwr")
                nwr_queue.reverse()
                ast_node = AbstractSyntaxTree(prod, [RealizedField(prod['one'], nwr_queue)])
            stack.append(ast_node)
        elif node.production.type.name == 'int_lit':
            prod = grammar.get_prod_by_ctr_name("anony_dist_int")
            ast_node = AbstractSyntaxTree(prod, [RealizedField(prod['one'], node)])
            stack.append(ast_node)
        elif len(stack) >= 1:
            node_second = node
            node_first = stack.pop()
            if node_first.production.type.name == 'meta_req':
                if node_second.production.type.name == 'meta_req':
                    prod = grammar.get_prod_by_ctr_name('anony_meta_req_meta_req')
                    var_field_one = RealizedField(prod['one'], value=node_first)
                    var_field_two = RealizedField(prod['two'], value=node_second)
                    ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two])
                    stack.append(ast_node)
                elif node_second.production.type.name == 'meta_pos':
                    prod = grammar.get_prod_by_ctr_name('anony_meta_req_meta_pos')
                    var_field_one = RealizedField(prod['one'], value=node_first)
                    var_field_two = RealizedField(prod['two'], value=node_second)
                    ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two])
                    stack.append(ast_node)
                else:
                    stack.append(node_first)
                    stack.append(node_second)
                    break
            elif node_first.production.type.name == 'keyval' and node_second.production.type.name == 'inner':
                prod = grammar.get_prod_by_ctr_name('anony_keyval_inner')
                var_field_one = RealizedField(prod['one'], value=node_first)
                var_field_two = RealizedField(prod['two'], value=node_second)
                ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two])
                stack.append(ast_node)
            else:
                stack.append(node_first)
                stack.append(node_second)
                break
        else:
            stack.append(node)
            break

"""
elif node.production.type.name == 'var_lit':
prod = grammar.get_prod_by_ctr_name('anony_val')
var_field_one = RealizedField(prod['one'], node)
ast_node = AbstractSyntaxTree(prod, [var_field_one])
stack.append(ast_node)
"""

"""
    if len(anony_ast_node_list) >= 1 and anony_ast_node_list[0].production.type.name == 'keyval':
            if len(anony_ast_node_list) == 2:
                prod = grammar.get_prod_by_ctr_name("anony_keyval_inner")
                keyval_var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
                inner_arg_ast_node_two = anony_ast_node_list[1]
                inner_var_field_two = RealizedField(prod['two'], inner_arg_ast_node_two)
                ast_node = AbstractSyntaxTree(prod,
                                      [keyval_var_field_one, inner_var_field_two])
            elif len(anony_ast_node_list) == 1:
                prod = grammar.get_prod_by_ctr_name("anony_keyval")
                keyval_var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
                ast_node = AbstractSyntaxTree(prod, [keyval_var_field_one])
            else:
                raise NotImplementedError
    elif len(anony_ast_node_list) >= 1 and anony_ast_node_list[0].production.type.name == 'nwr':
        if len(anony_ast_node_list) == 2:
            prod = grammar.get_prod_by_ctr_name("anony_nwr_osm")
            var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
            var_field_two = RealizedField(prod['two'], anony_ast_node_list[1])
            ast_node = AbstractSyntaxTree(prod,
                                          [var_field_one, var_field_two])
        elif len(anony_ast_node_list) == 1:
            #print ("anony_nwr")
            prod = grammar.get_prod_by_ctr_name("anony_nwr")
            var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
            ast_node = AbstractSyntaxTree(prod,
                                          [var_field_one])
        else:
            raise NotImplementedError
    elif len(anony_ast_node_list) == 2 and anony_ast_node_list[0].production.type.name == 'meta_req':
        arg_ast_node_one = anony_ast_node_list[0]
        arg_ast_node_two = anony_ast_node_list[1]
        if anony_ast_node_list[1].production.type.name == 'meta_req':
            prod = grammar.get_prod_by_ctr_name('anony_meta_req_meta_req')
            var_field_one = RealizedField(prod['one'], value=arg_ast_node_one)
            var_field_two = RealizedField(prod['two'], value=arg_ast_node_two)
            ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two])
        elif anony_ast_node_list[1].production.type.name == 'meta_pos':
            prod = grammar.get_prod_by_ctr_name('anony_meta_req_meta_pos')
            var_field_one = RealizedField(prod['one'], value=arg_ast_node_one)
            var_field_two = RealizedField(prod['two'], value=arg_ast_node_two)
            ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two])
        else:
            raise NotImplementedError
    elif len(anony_ast_node_list) >= 2 and anony_ast_node_list[0].production.type.name == 'area' and anony_ast_node_list[1].production.type.name == 'osm':
        prod = grammar.get_prod_by_ctr_name("anony_area_osm")
        var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
        var_field_two = RealizedField(prod['two'], anony_ast_node_list[1])
        ast_node = AbstractSyntaxTree(prod,
                                  [var_field_one, var_field_two])
    elif len(anony_ast_node_list) == 1 and anony_ast_node_list[0].production.type.name == 'osm':
        prod = grammar.get_prod_by_ctr_name("anony_osm")
        var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
        ast_node = AbstractSyntaxTree(prod,
                                  [var_field_one])
    elif len(anony_ast_node_list) == 1 and anony_ast_node_list[0].production.type.name == 'x':
        prod = grammar.get_prod_by_ctr_name('anony_x')
        var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
        ast_node = AbstractSyntaxTree(prod, [var_field_one])
"""
def semi_shift_reduce(grammar, anony_ast_node_list):
    stack = []
    for i, node in enumerate(anony_ast_node_list):
        stack.append(node)
        look_ahead_node = None
        if i + 1 < len(anony_ast_node_list):
            look_ahead_node = anony_ast_node_list[i + 1]
        check_production(grammar, stack, look_ahead_node)

    return stack

def check_binary_production(grammar, node_first, node_second):
    ast_node = None
    if node_first.production.type.name == 'keyval' and node_second.production.type.name == 'inner':
        prod = grammar.get_prod_by_ctr_name("anony_keyval_inner")
        keyval_var_field_one = RealizedField(prod['one'], node_first[0])
        inner_arg_ast_node_two = node_second[1]
        inner_var_field_two = RealizedField(prod['two'], inner_arg_ast_node_two)
        ast_node = AbstractSyntaxTree(prod,
                                      [keyval_var_field_one, inner_var_field_two])
    elif node_first.production.type.name == 'nwr' and node_second.production.type.name == 'osm':
        prod = grammar.get_prod_by_ctr_name("anony_nwr_osm")
        var_field_one = RealizedField(prod['one'], node_first)
        var_field_two = RealizedField(prod['two'], node_second)
        ast_node = AbstractSyntaxTree(prod,
                                      [var_field_one, var_field_two])
    elif node_first.production.type.name == 'meta_req':
        if node_second.production.type.name == 'meta_req':
            prod = grammar.get_prod_by_ctr_name('anony_meta_req_meta_req')
            var_field_one = RealizedField(prod['one'], value=node_first)
            var_field_two = RealizedField(prod['two'], value=node_second)
            ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two])
        elif node_second.production.type.name == 'meta_pos':
            prod = grammar.get_prod_by_ctr_name('anony_meta_req_meta_pos')
            var_field_one = RealizedField(prod['one'], value=node_first)
            var_field_two = RealizedField(prod['two'], value=node_second)
            ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two])
    elif node_first.production.type.name == 'area' and node_second.production.type.name == 'osm':
        prod = grammar.get_prod_by_ctr_name("anony_area_osm")
        var_field_one = RealizedField(prod['one'], node_first)
        var_field_two = RealizedField(prod['two'], node_second)
        ast_node = AbstractSyntaxTree(prod,
                                      [var_field_one, var_field_two])
    return ast_node


def check_unit_production(grammar, node):
    ast_node = None
    if node.production.type.name == 'keyval':
        prod = grammar.get_prod_by_ctr_name("anony_keyval")
        keyval_var_field_one = RealizedField(prod['one'], node)
        ast_node = AbstractSyntaxTree(prod, [keyval_var_field_one])
    elif node.production.type.name == 'nwr':
        prod = grammar.get_prod_by_ctr_name("anony_nwr")
        var_field_one = RealizedField(prod['one'], node)
        ast_node = AbstractSyntaxTree(prod,
                                      [var_field_one])
    elif node.production.type.name == 'osm':
        prod = grammar.get_prod_by_ctr_name("anony_osm")
        var_field_one = RealizedField(prod['one'], node)
        ast_node = AbstractSyntaxTree(prod,
                                      [var_field_one])
    elif node.production.type.name == 'x':
        prod = grammar.get_prod_by_ctr_name('anony_x')
        var_field_one = RealizedField(prod['one'], node)
        ast_node = AbstractSyntaxTree(prod, [var_field_one])
    return ast_node

def semi_CYK_parser(grammar, anony_ast_node_list):
    #nonterminal = ["inner", "osm", "query_u", "s", "meta_req", "keyval", 'nwr', 'osm', 'x', 'meta_pos', "area"]
    """
    meta_req -> meta_req, meta_req
    meta_req -> meta_req, meta_pos   
    query_u -> area, osm
    query_u -> osm
    s > x
    osm -> nwr
    osm -> nwr, osm
    inner -> keyval
    inner -> keyval, inner
    """
    binary_rules = [(4, 4), (4, 9), (10, 7), (6, 7), (5, 0)]
    #num_nonterminal = len(nonterminal)
    len_anony = len(anony_ast_node_list)
    #indicators = [[[False for i in range(num_nonterminal)] for j in range(len_anony)] for k in range(len_anony)]
    parse_tables = [[None for j in range(len_anony)] for k in range(len_anony+1)]
    for i, node in enumerate(anony_ast_node_list):
        parse_tables[0][i] = node
    for i, node in enumerate(anony_ast_node_list):
        prod_node = check_unit_production(grammar, node)
        if prod_node:
            parse_tables[1][i] = prod_node
    for l in range(2, len_anony + 2):
        for s in range(len_anony - l + 1):
            for p in range(2, l + 1):
                if parse_tables[p - 1][s] and parse_tables[l - p - 1][s]:
                    node_first = parse_tables[p - 1][s]
                    node_second = parse_tables[l - p - 1][s]
                    prod_node = check_binary_production(grammar, node_first, node_second)
                    if prod_node:
                        parse_tables[l][s] = prod_node
    result_nodes = []
    for i in range(len_anony + 1):
        temp_node_list = []
        for j in range(len_anony):
                if parse_tables[i][j]:
                    temp_node_list.append(parse_tables[i][j])
        if len(temp_node_list) > 0:
            result_nodes.append(temp_node_list)
    if len(result_nodes) == 0:
        result_nodes.append([])
    return result_nodes

def logical_form_to_ast_helper(grammar, literal_dict, lf_node):
    ast_node = None
    anony_ast_node_list = []
    for lf_child in lf_node.children:
        anony_ast_node_list.append(logical_form_to_ast_helper(grammar, literal_dict, lf_child))
    #print (lf_node.name)
    #anony_ast_node_list = semi_shift_reduce(grammar, anony_ast_node_list)
    matchObj = re.match(r"\'(.+)\'", lf_node.name)
    if matchObj:
        name = matchObj.group(1)
        #print (name)
        if name in literal_dict['key']:
                        # it's a variable literal
            prod = grammar.get_prod_by_ctr_name('anony_key')
            var_field = RealizedField(prod['one'], value=lf_node.name)

            ast_node = AbstractSyntaxTree(prod,
                                      [var_field])
        elif name in literal_dict['cw']:
                        # it's a variable literal
            prod = grammar.get_prod_by_ctr_name('anony_cw')

            var_field = RealizedField(prod['one'], value=lf_node.name)

            ast_node = AbstractSyntaxTree(prod,
                                      [var_field])
        else:
            # it's a variable literal
            prod = grammar.get_prod_by_ctr_name('anony_var')

            var_field = RealizedField(prod['one'], value=lf_node.name)

            ast_node = AbstractSyntaxTree(prod,
                                      [var_field])
    elif lf_node.name in literal_dict['kmmi']:
        # it's a variable literal
        prod = grammar.get_prod_by_ctr_name('anony_kmmi')

        var_field = RealizedField(prod['one'], value=lf_node.name)

        ast_node = AbstractSyntaxTree(prod,
                                      [var_field])
    elif isInt(lf_node.name):

        prod = grammar.get_prod_by_ctr_name('anony_int')

        var_field = RealizedField(prod['one'], value=lf_node.name)

        ast_node = AbstractSyntaxTree(prod,
                                      [var_field])
    elif lf_node.name in literal_dict['dist']:
        # it's a variable literal
        prod = grammar.get_prod_by_ctr_name('anony_dist')

        var_field = RealizedField(prod['one'], value=lf_node.name)

        ast_node = AbstractSyntaxTree(prod,
                                      [var_field])
    elif lf_node.name == 'and' or lf_node.name == 'or':
        ast_node = None
        for i in range(1, len(anony_ast_node_list)):
            arg_ast_node_one_list = semi_shift_reduce(grammar, anony_ast_node_list[:i])
            arg_ast_node_two_list = semi_shift_reduce(grammar, anony_ast_node_list[i:])
            if len(arg_ast_node_one_list) == 1 and len(arg_ast_node_two_list) == 1:
                arg_ast_node_one = arg_ast_node_one_list[0]
                arg_ast_node_two = arg_ast_node_two_list[0]
                if arg_ast_node_one.production.type.name == "val" and arg_ast_node_two.production.type.name == "val":
                    prod = grammar.get_prod_by_ctr_name(lf_node.name + "_val_val")
                    var_field_one = RealizedField(prod['one'], arg_ast_node_one)

                    var_field_two = RealizedField(prod['two'], arg_ast_node_two)
                    ast_node = AbstractSyntaxTree(prod,
                                              [var_field_one, var_field_two])
                elif arg_ast_node_one.production.type.name == "key_lit" and arg_ast_node_two.production.type.name == "key_lit":
                    assert lf_node.name == 'and', "the type with two key arguments should be \'and\'"
                    prod = grammar.get_prod_by_ctr_name("and_key_key")
                    var_field_one = RealizedField(prod['one'], arg_ast_node_one)

                    var_field_two = RealizedField(prod['two'], arg_ast_node_two)
                    ast_node = AbstractSyntaxTree(prod,
                                              [var_field_one, var_field_two])
                elif arg_ast_node_one.production.type.name == "inner" and arg_ast_node_two.production.type.name == "inner":
                    prod = grammar.get_prod_by_ctr_name(lf_node.name + "_inner_inner")
                    var_field_one = RealizedField(prod['one'], arg_ast_node_one)

                    var_field_two = RealizedField(prod['two'], arg_ast_node_two)
                    ast_node = AbstractSyntaxTree(prod,
                                                  [var_field_one, var_field_two])
        if not ast_node:
            raise NotImplementedError
    elif lf_node.name == 'keyval':

        key_arg_ast_node_one = anony_ast_node_list[0]
        val_arg_ast_node_two = anony_ast_node_list[1]
        if not val_arg_ast_node_two.production.type.name == "val":
            prod = grammar.get_prod_by_ctr_name('anony_var')
            var_field_one = RealizedField(prod['one'], value = val_arg_ast_node_two.fields[0].as_value_list[0])
            val_arg_ast_node_two = AbstractSyntaxTree(prod, [var_field_one])
        d = dirname(dirname(abspath(__file__)))
        dir_path = os.path.join(d, "nlmap/")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        f = open(os.path.join(d, "nlmap/variable_phrases.txt"), 'a')
        f.write(str(val_arg_ast_node_two.fields[0].as_value_list[0]) + '\n')
        f.close()
        f = open(os.path.join(d, "nlmap/key_phrase.txt"), 'a')
        f.write(str(key_arg_ast_node_one.fields[0].as_value_list[0]) + '\n')
        f.close()
        prod = grammar.get_prod_by_ctr_name(lf_node.name)
        key_var_field_one = RealizedField(prod['one'], key_arg_ast_node_one)

        val_var_field_two = RealizedField(prod['two'], val_arg_ast_node_two)
        ast_node = AbstractSyntaxTree(prod,
                                      [key_var_field_one, val_var_field_two])
    elif lf_node.name == 'nwr':
        anony_ast_node_list = semi_shift_reduce(grammar, anony_ast_node_list)
        assert len(anony_ast_node_list) == 1
        arg_ast_node_one = anony_ast_node_list[0]
        assert arg_ast_node_one.production.type.name == "inner"
        prod = grammar.get_prod_by_ctr_name('nwr')

        ast_node = AbstractSyntaxTree(prod,
                                      [RealizedField(prod['one'], arg_ast_node_one)])
    elif lf_node.name == 'area':
        anony_ast_node_list = semi_shift_reduce(grammar, anony_ast_node_list)
        assert len(anony_ast_node_list) == 1
        arg_ast_node_one = anony_ast_node_list[0]
        assert arg_ast_node_one.production.type.name == "inner"
        prod = grammar.get_prod_by_ctr_name('area')
        inner_field = RealizedField(prod['one'], arg_ast_node_one)

        ast_node = AbstractSyntaxTree(prod, [inner_field])
    elif lf_node.name == 'topx':
        # expr -> Apply(pred predicate, expr* arguments)
        prod = grammar.get_prod_by_ctr_name('topx')

        int_field = RealizedField(prod['one'], value=anony_ast_node_list[0])

        ast_node = AbstractSyntaxTree(prod, [int_field])
    elif lf_node.name == 'nodup':
        anony_ast_node_list = semi_shift_reduce(grammar, anony_ast_node_list)
        assert len(anony_ast_node_list) == 1
        arg_ast_node_one = anony_ast_node_list[0]
        assert arg_ast_node_one.production.type.name == "meta_req"
        prod = grammar.get_prod_by_ctr_name('nodup')
        ast_node = AbstractSyntaxTree(prod,
                                      [RealizedField(prod['one'], value=arg_ast_node_one)])
    elif lf_node.name == 'least':
        prod = grammar.get_prod_by_ctr_name('least')
        ast_node = AbstractSyntaxTree(prod,
                                      [RealizedField(prod['one'], value=anony_ast_node_list[0])])
    elif lf_node.name == 'latlong':
        if len(anony_ast_node_list) == 0:
            prod = grammar.get_prod_by_ctr_name('latlong')
            ast_node = AbstractSyntaxTree(prod)
        elif len(anony_ast_node_list) == 1:
            prod = grammar.get_prod_by_ctr_name('latlong_meta_topx')
            ast_node = AbstractSyntaxTree(prod,
                                         [RealizedField(prod['one'], value=anony_ast_node_list[0])])
        else:
            raise NotImplementedError
    elif lf_node.name == 'count':
        # expr -> The(var variable, expr body)
        prod = grammar.get_prod_by_ctr_name('count')
        ast_node = AbstractSyntaxTree(prod)
    elif lf_node.name == 'findkey':
        arg_ast_node_one = anony_ast_node_list[0]
        if arg_ast_node_one.production.type.name == "key_lit":
            if len(anony_ast_node_list) == 1:
                prod = grammar.get_prod_by_ctr_name('findkey_key')
                var_field_one = RealizedField(prod['one'], value=arg_ast_node_one)
                ast_node = AbstractSyntaxTree(prod,
                                         [var_field_one])
            elif len(anony_ast_node_list) == 2:
                prod = grammar.get_prod_by_ctr_name('findkey_key_meta_topx')
                var_field_one = RealizedField(prod['one'], value=arg_ast_node_one)
                arg_ast_node_two = anony_ast_node_list[1]
                var_field_two = RealizedField(prod['two'], value=arg_ast_node_two)
                ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two])
            else:
                raise NotImplementedError
        elif arg_ast_node_one.production.type.name == "and_key_key":
            prod = grammar.get_prod_by_ctr_name('findkey_and_key_key')
            var_field_one = RealizedField(prod['one'], value=arg_ast_node_one)
            ast_node = AbstractSyntaxTree(prod, [var_field_one])
        else:
            raise NotImplementedError
    # type or type ?
    elif lf_node.name == 'qtype':
        anony_ast_node_list = semi_shift_reduce(grammar, anony_ast_node_list)
        assert len(anony_ast_node_list) == 1
        arg_ast_node_one = anony_ast_node_list[0]
        if arg_ast_node_one.production.type.name == "meta_req":
            prod = grammar.get_prod_by_ctr_name('qtype_meta_req')
            var_field_one = RealizedField(prod['one'], value=arg_ast_node_one)
            ast_node = AbstractSyntaxTree(prod, [var_field_one])
        elif arg_ast_node_one.production.type.name == "meta_pos":
            prod = grammar.get_prod_by_ctr_name('qtype_meta_pos')
            var_field_one = RealizedField(prod['one'], value=arg_ast_node_one)
            ast_node = AbstractSyntaxTree(prod, [var_field_one])
        else:
            raise NotImplementedError
    elif lf_node.name == 'center':
        anony_ast_node_list = semi_shift_reduce(grammar, anony_ast_node_list)
        assert len(anony_ast_node_list) == 1
        arg_ast_node_one = anony_ast_node_list[0]
        assert arg_ast_node_one.production.type.name == "query_u"
        prod = grammar.get_prod_by_ctr_name('center')
        ast_node = AbstractSyntaxTree(prod,
                                      [RealizedField(prod['one'], value=arg_ast_node_one)])
    elif lf_node.name == 'search':
        anony_ast_node_list = semi_shift_reduce(grammar, anony_ast_node_list)
        assert len(anony_ast_node_list) == 1
        arg_ast_node_one = anony_ast_node_list[0]
        assert arg_ast_node_one.production.type.name == "query_u"
        prod = grammar.get_prod_by_ctr_name('search')
        ast_node = AbstractSyntaxTree(prod,
                                      [RealizedField(prod['one'], value=arg_ast_node_one)])
    elif lf_node.name == 'maxdist':
        anony_ast_node_list = semi_shift_reduce(grammar, anony_ast_node_list)
        prod = grammar.get_prod_by_ctr_name('maxdist')
        ast_node = AbstractSyntaxTree(prod,
                                      [RealizedField(prod['one'], value=anony_ast_node_list[0])])
    elif lf_node.name == 'around':
        if len(anony_ast_node_list) == 3:
            prod = grammar.get_prod_by_ctr_name('around')
            var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
            var_field_two = RealizedField(prod['two'], anony_ast_node_list[1])
            var_field_three = RealizedField(prod['three'], anony_ast_node_list[2])
            ast_node = AbstractSyntaxTree(prod,
                                      [var_field_one, var_field_two, var_field_three])
        elif len(anony_ast_node_list) == 4:
            prod = grammar.get_prod_by_ctr_name('around_meta_topx')
            var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
            var_field_two = RealizedField(prod['two'], anony_ast_node_list[1])
            var_field_three = RealizedField(prod['three'], anony_ast_node_list[2])
            var_field_four = RealizedField(prod['four'], anony_ast_node_list[3])
            ast_node = AbstractSyntaxTree(prod,
                                      [var_field_one, var_field_two, var_field_three, var_field_four])
        else:
            raise NotImplementedError
    elif lf_node.name == 'north':
        anony_ast_node_list = semi_shift_reduce(grammar, anony_ast_node_list)
        assert len(anony_ast_node_list) == 1
        if anony_ast_node_list[0].production.type.name == 'around':
            prod = grammar.get_prod_by_ctr_name('north_around')
            var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
            ast_node = AbstractSyntaxTree(prod, [var_field_one])
        elif anony_ast_node_list[0].production.type.name == 'query_u':
            arg_ast_node_one = anony_ast_node_list[0]
            prod = grammar.get_prod_by_ctr_name('north_query_u')
            var_field_one = RealizedField(prod['one'], arg_ast_node_one)
            ast_node = AbstractSyntaxTree(prod, [var_field_one])
        else:
            raise NotImplementedError
    elif lf_node.name == 'west':
        anony_ast_node_list = semi_shift_reduce(grammar, anony_ast_node_list)
        assert len(anony_ast_node_list) == 1
        if anony_ast_node_list[0].production.type.name == 'around':
            prod = grammar.get_prod_by_ctr_name('west_around')
            var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
            ast_node = AbstractSyntaxTree(prod, [var_field_one])
        elif anony_ast_node_list[0].production.type.name == 'query_u':
            arg_ast_node_one = anony_ast_node_list[0]
            prod = grammar.get_prod_by_ctr_name('west_query_u')
            var_field_one = RealizedField(prod['one'], arg_ast_node_one)
            ast_node = AbstractSyntaxTree(prod, [var_field_one])
        else:
            raise NotImplementedError
    elif lf_node.name == 'south':
        anony_ast_node_list = semi_shift_reduce(grammar, anony_ast_node_list)
        assert len(anony_ast_node_list) == 1
        if anony_ast_node_list[0].production.type.name == 'around':
            prod = grammar.get_prod_by_ctr_name('south_around')
            var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
            ast_node = AbstractSyntaxTree(prod, [var_field_one])
        elif anony_ast_node_list[0].production.type.name == 'query_u':
            arg_ast_node_one = anony_ast_node_list[0]
            prod = grammar.get_prod_by_ctr_name('south_query_u')
            var_field_one = RealizedField(prod['one'], arg_ast_node_one)
            ast_node = AbstractSyntaxTree(prod, [var_field_one])
        else:
            raise NotImplementedError
    elif lf_node.name == 'east':
        anony_ast_node_list = semi_shift_reduce(grammar, anony_ast_node_list)
        assert len(anony_ast_node_list) == 1
        if anony_ast_node_list[0].production.type.name == 'around':
            prod = grammar.get_prod_by_ctr_name('east_around')
            var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
            ast_node = AbstractSyntaxTree(prod, [var_field_one])
        elif anony_ast_node_list[0].production.type.name == 'query_u':
            arg_ast_node_one = anony_ast_node_list[0]
            prod = grammar.get_prod_by_ctr_name('east_query_u')
            var_field_one = RealizedField(prod['one'], arg_ast_node_one)
            ast_node = AbstractSyntaxTree(prod, [var_field_one])
        else:
            raise NotImplementedError
    elif lf_node.name == 'query':
        ast_node = None
        for i in range(1, len(anony_ast_node_list)):
            arg_ast_node_one_list = semi_shift_reduce(grammar, anony_ast_node_list[:i])
            arg_ast_node_two_list = semi_shift_reduce(grammar, anony_ast_node_list[i:])
            if len(arg_ast_node_one_list) == 1 and len(arg_ast_node_two_list) == 1:
                arg_ast_node_one = arg_ast_node_one_list[0]
                arg_ast_node_two = arg_ast_node_two_list[0]
                if arg_ast_node_one.production.type.name == 'direction' and arg_ast_node_two.production.type.name == 'meta':
                    prod = grammar.get_prod_by_ctr_name('query_direction')
                    var_field_one = RealizedField(prod['one'], arg_ast_node_one)
                    var_field_two = RealizedField(prod['two'], arg_ast_node_two)
                    ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two])
                elif arg_ast_node_one.production.type.name == 'around' and arg_ast_node_two.production.type.name == 'meta':
                    prod = grammar.get_prod_by_ctr_name('query_around')
                    var_field_one = RealizedField(prod['one'], arg_ast_node_one)
                    var_field_two = RealizedField(prod['two'], arg_ast_node_two)
                    ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two])
                elif arg_ast_node_one.production.type.name == 'query_u' and arg_ast_node_two.production.type.name == 'meta':
                    prod = grammar.get_prod_by_ctr_name('query_query_u')
                    var_field_one = RealizedField(prod['one'], arg_ast_node_one)
                    var_field_two = RealizedField(prod['two'], arg_ast_node_two)
                    ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two])
        if not ast_node:
            raise NotImplementedError
    elif lf_node.name == 'unit':
        prod = grammar.get_prod_by_ctr_name('unit')
        var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
        ast_node = AbstractSyntaxTree(prod, [var_field_one])
    elif lf_node.name == 'for':
        prod = grammar.get_prod_by_ctr_name('for')
        var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
        ast_node = AbstractSyntaxTree(prod, [var_field_one])
    elif lf_node.name == 'dummy_node':
        assert len(anony_ast_node_list) == 1
        if anony_ast_node_list[0].production.type.name == 'x':
            prod = grammar.get_prod_by_ctr_name('anony_x')
            var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
            ast_node = AbstractSyntaxTree(prod, [var_field_one])
        elif anony_ast_node_list[0].production.type.name == 's':
            ast_node = anony_ast_node_list[0]
        else:
            raise NotImplementedError
    elif lf_node.name == 'dist':
        if len(anony_ast_node_list) == 1:
            prod = grammar.get_prod_by_ctr_name('dist_x')
            var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
            ast_node = AbstractSyntaxTree(prod, [var_field_one])
        elif len(anony_ast_node_list) == 2:
            if anony_ast_node_list[1].production.type.name == 'unit':
                prod = grammar.get_prod_by_ctr_name('dist_x_unit')
                var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
                var_field_two = RealizedField(prod['two'], anony_ast_node_list[1])
                ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two])
            elif anony_ast_node_list[1].production.type.name == 'x':
                prod = grammar.get_prod_by_ctr_name('dist_x_x')
                var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
                var_field_two = RealizedField(prod['two'], anony_ast_node_list[1])
                ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two])
            elif anony_ast_node_list[1].production.type.name == 'for':
                prod = grammar.get_prod_by_ctr_name('dist_x_for')
                var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
                var_field_two = RealizedField(prod['two'], anony_ast_node_list[1])
                ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two])
            else:
                raise NotImplementedError
        elif len(anony_ast_node_list) == 3:
            if anony_ast_node_list[2].production.type.name == 'unit':
                prod = grammar.get_prod_by_ctr_name('dist_x_x_unit')
                var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
                var_field_two = RealizedField(prod['two'], anony_ast_node_list[1])
                var_field_three = RealizedField(prod['three'], anony_ast_node_list[2])
                ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two, var_field_three])
            elif anony_ast_node_list[2].production.type.name == 'for':
                prod = grammar.get_prod_by_ctr_name('dist_x_x_for')
                var_field_one = RealizedField(prod['one'], anony_ast_node_list[0])
                var_field_two = RealizedField(prod['two'], anony_ast_node_list[1])
                var_field_three = RealizedField(prod['three'], anony_ast_node_list[2])
                ast_node = AbstractSyntaxTree(prod, [var_field_one, var_field_two, var_field_three])
            else:
                raise NotImplementedError
    return ast_node

def ast_to_logical_form_helper(ast_tree):
    constructor_name = ast_tree.production.constructor.name
    if constructor_name.startswith("anony"):
        node_name = "anony_node"
    else:
        node_name = constructor_name.split('_')[0]
    children_list = []
    for field in ast_tree.fields:
        if field.value is not None:
            for val_node in field.as_value_list:
                if isinstance(field.type, ASDLCompositeType):
                    children_list.append(ast_to_logical_form_helper(val_node))
                else:
                    children_list.append(Node(val_node))
    return Node(node_name, children_list)

def prune_anony_node(node):
    dummy_node = Node("dummy_node")
    dummy_node.add_child(node)
    queue = []
    queue.append(dummy_node)
    while len(queue) > 0:
        current_node = queue.pop(0)
        index = 0
        while index < len(current_node.children):
            child_of_current_node = current_node.children[index]
            if child_of_current_node.name == "anony_node":
                current_node.children.pop(index)
                remove_index = index
                for child_of_child_of_current_node in child_of_current_node.children:
                    current_node.children.insert(remove_index, child_of_child_of_current_node)
                    remove_index += 1
            else:
                renewed_child_of_current_node = current_node.children[index]
                queue.append(renewed_child_of_current_node)
                index += 1

    return dummy_node.children[0]

def ast_to_logical_form(ast_tree):
    node = ast_to_logical_form_helper(ast_tree)
    return prune_anony_node(node).to_string()

def load_literal_dict():
    import os
    from os.path import dirname, abspath
    d = dirname(dirname(abspath(__file__)))
    literal_dict = {'key':[],
           'cw':['car','walk'],
           'kmmi':['km', 'mi'],
           'dist':['WALKDING_DIST','DIST_INTOWN','DIST_OUTTOWN','DIST_DAYTRIP']}
    with open(os.path.join(d, "nlmap/key_phrases.txt")) as f:
        key_content = f.readlines()
    key_list = [x.strip().split("|||")[1].strip() for x in key_content]
    literal_dict['key'] = key_list
    return literal_dict

def logical_form_to_ast(grammar, code):
    lf_node = parse_nlmap_expr_helper(code.split(' '), 0)[0]
    dummy_node = Node("dummy_node")
    dummy_node.add_child(lf_node)
    literal_dict = load_literal_dict()
    return logical_form_to_ast_helper(grammar, literal_dict, dummy_node)


if __name__ == '__main__':
    asdl_desc = """
int, key, dist, kmmi, cw, var

s = anony_x(x one)
    |dist_x_unit(x one, unit two)
    | dist_x_x_unit(x one, x two, unit three)
    | dist_x(x one)
    | dist_x_x(x one, x two)
    |dist_x_for(x one, for two)
    | dist_x_x_for(x one, x two, for three)

for = for(cw_lit one)

unit = unit(kmmi_lit one)

x = query_direction(direction one, meta two)
    | query_around(around one, meta two)
    | query_query_u(query_u one, meta two)

direction = north_around(around one)
            | north_query_u(query_u one)
            | west_around(around one)
            | west_query_u(query_u one)
            | south_around(around one)
            | south_query_u(query_u one)
            | east_around(around one)
            | east_query_u(query_u one)

around = around_meta_topx(center one, search two, maxdist three, meta_topx four)
        | around(center one, search two, maxdist three)

maxdist = maxdist(dist_lit one)

search = search(query_u one)

center = center(query_u one)

query_u = anony_area_nwr(area one, nwr* two)
        | anony_nwr(nwr* one)

meta = qtype_meta_req(meta_req one)
        | qtype_meta_pos(meta_pos one)

meta_pos = nodup(meta_req one)

meta_req = least(meta_topx one)
            | latlong_meta_topx(meta_topx one)
            | latlong
            | count
            | findkey_key_meta_topx(key_lit one, meta_topx two)
            | findkey_key(key_lit one)
            | findkey_and_key_key(and_key_key one)
            | anony_meta_req_meta_req(meta_req one, meta_req two)
            | anony_meta_req_meta_pos(meta_req one, meta_pos two)

and_key_key = and_key_key(key_lit one, key_lit two)

meta_topx = topx(int_lit one)

area = area(inner one)

nwr = nwr(inner one)

inner = anony_keyval(keyval one)
        | anony_keyval_inner(keyval one, inner two)
        | and_inner_inner(inner one, inner two)
        | or_inner_inner(inner one, inner two)

keyval = keyval(key_lit one, val two)

val = anony_var(var one)
    | or_val_val(val one, val two)
    | and_val_val(val one, val two)

cw_lit = anony_cw(cw one)

kmmi_lit = anony_kmmi(kmmi one)

dist_lit = anony_dist(dist one)
        | anony_dist_int(int_lit one)

key_lit = anony_key(key one)

int_lit = anony_int(int one)
    """

    grammar = ASDLGrammar.from_text(asdl_desc)
    # s = "query ( around ( center ( nwr ( keyval ( 'name' , 'Liverpool' ) ) ) , search ( nwr ( keyval ( 'amenity' , 'post_box' ) ) ) , maxdist ( DIST_INTOWN ) ) , qtype ( count ) )"
    s = "query ( area ( keyval ( 'name' , 'Paris' ) , keyval ( 'is_in:country' , 'France' ) ) , nwr ( keyval ( 'name' , 'Tour_Eiffel' ) ) , qtype ( findkey ( 'name:ja' ) ) )"
    print(parse_nlmap_expr_helper(s.split(' '), 0)[0].to_string())
    # query ( around ( center ( nwr ( keyval ( 'name' , 'Liverpool' ) ) ) , search ( nwr ( keyval ( 'amenity' , 'post_box' ) ) ) , maxdist ( DIST_INTOWN ) ) , qtype ( count ) )
    lf_node = parse_nlmap_expr_helper(s.split(' '), 0)[0]
    # dummy node to deal with special anonymous function case at the top of the sequence
    ast_tree = logical_form_to_ast(grammar, s)
    print (ast_tree.to_string())
    new_lf = ast_to_logical_form(ast_tree)
    print (new_lf)
    assert lf_node.to_string() == new_lf
    ast_tree.sanity_check()
    pass

