from lib2to3.fixer_base import BaseFix
from lib2to3.pygram import python_symbols as symbols
from lib2to3.fixer_util import is_import, syms, Node

import pdb
from pprint import pprint
pst = pdb.set_trace
import compiler
from snakefood import find
from StringIO import StringIO
import pkgutil
import os

def empty_stmt():
    new_expr = Node(syms.expr_stmt, [])
    new_stmt = Node(syms.simple_stmt, [new_expr])
    new_stmt.changed()
    return new_stmt
BUILTINS = ['time', 'os', 'sys', 'math', 're', 'string', 'json']
print symbols.import_name
class FixImportOrder(BaseFix):
    u'''
    Imports should be sorted alphabetically in groups.
    '''
    def start_tree(self, tree, filename):
#        pst()
        # Trim the prefix so header comments don't get juggled
        prefix_sep = '\n\n'
        original_prefix, _, tail = tree.prefix.rpartition(prefix_sep)
        tree.prefix = tail
        cat_builtins = []
        cat_external = []
        cat_local = []

        for node in tree.children:
            if not (node.type == symbols.simple_stmt and
                    is_import(node.children[0])):
                        break
            found_imports = find.get_ast_imports(
                compiler.parse(str(node)))
            module = found_imports[0][0]
            base_module = module.split('.')[0]
            if base_module in BUILTINS:
                cat_builtins.append(node)
                continue

            loader = pkgutil.ImpImporter(os.getcwd()).find_module(base_module)
            if loader:
                filename = loader.get_filename()
                if filename and os.path.abspath(filename
                                                ).startswith(os.getcwd()):
                    cat_local.append(node)
                    continue

            # otherwise, it's external package
            cat_external.append(node)

        def sortem(node):
            return str(node).replace(node.prefix, '', 1)
        cur_list = cat_builtins
        all_lists = [cat_external, cat_local]
        for i, node in enumerate(sorted(cat_builtins, key=sortem) +
                                 sorted(cat_external, key=sortem) +
                                 sorted(cat_local, key=sortem)
                                 ):
            node.prefix = node.prefix.lstrip()
            while node not in cur_list:
                node.prefix = '\n' + node.prefix
                cur_list = all_lists.pop(0)
            tree.set_child(i, node)
            
        # put the old prefix material back
        tree.prefix = original_prefix + prefix_sep + tree.prefix


    def match(self, node):
        return False

    def transform2(self, node, results):
        orig_prefix = node.prefix
        node.prefix= ''
        nodes = results
#        pdb.set_trace()
        if nodes:
            def sortem(x):
                return ''.join(map(str, x.children[0].children))
            sorted_nodes  = sorted(nodes, key=sortem)
            childs = []
            for n in sorted_nodes:
                childs.append(n.children)
            for n, s, c in zip(nodes, sorted_nodes, childs):
                print str(n).strip(), '----', str(s).strip()
                n.children = c
#                if n.prefix == '\n':
#                    n.prefix = ''
            print "------"
        node.prefix = orig_prefix
        return node
