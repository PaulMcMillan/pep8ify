from lib2to3.fixer_base import BaseFix
from lib2to3.pygram import python_symbols as symbols
from lib2to3.fixer_util import is_import, syms, Node
import itertools

import pdb
from pprint import pprint
pst = pdb.set_trace
import compiler
import snakefood.find
import pkgutil
import os

def empty_stmt():
    new_expr = Node(syms.expr_stmt, [])
    new_stmt = Node(syms.simple_stmt, [new_expr])
    new_stmt.changed()
    return new_stmt

STANDARD_LIBRARY = ['time', 'os', 'sys', 'math', 're', 'string', 'json']


class FixImportOrder(BaseFix):
    u'''
    Imports should be sorted alphabetically in groups.
    '''
    def start_tree(self, tree, filename):
#        pst()
        # Save the original prefix so we can put it back at the end
        original_prefix = tree.prefix
        tree.prefix = ''

        # Import categories to sort into
        cat_stdlib = []
        cat_external = []
        cat_local = []

        # Build our categorized lists of nodes
        for node in tree.children:
            if not (node.type == symbols.simple_stmt and
                    is_import(node.children[0])):
                        break
            found_imports = snakefood.find.get_ast_imports(
                compiler.parse(str(node)))
            module = found_imports[0][0]
            base_module = module.split('.')[0]

            # Is the node part of the stdlib?
            if base_module in STANDARD_LIBRARY:
                cat_stdlib.append(node)
                continue
            
            # Is the node an import for the local project?
            cwd = os.getcwd()
            loader = pkgutil.ImpImporter(cwd).find_module(base_module)
            if loader:
                filename = loader.get_filename()
                if filename and os.path.abspath(filename).startswith(cwd):
                    cat_local.append(node)
                    continue

            # otherwise, it's external package
            cat_external.append(node)

        def _get_import_sort_key(node):
            """ Given a node, derive a sort key for order comparison. """
            # remove any prefix (comments and whitespace)
            base = str(node).replace(node.prefix, '', 1).strip()
            # put "import"s before "from ..."s
            if base.startswith('import'):
                sort_prefix = '0'
            else:
                sort_prefix = '1'
            return sort_prefix + base

        all_lists = [sorted(lst, key=_get_import_sort_key) for lst in 
                     (cat_stdlib, cat_external, cat_local)]
        cur_list = []
        for i, node in enumerate(itertools.chain(*all_lists)):
            node.prefix = node.prefix.lstrip()
            # add newline separators between lists
            while node not in cur_list:
                cur_list = all_lists.pop(0)
                # don't add a newline before the first group
                if node in cur_list and i != 0:
                    node.prefix = '\n' + node.prefix
            # Assign the node to its new location, overwriting the old
            tree.set_child(i, node)
            
        # put the old prefix material back
        tree.prefix = original_prefix + tree.prefix

    # Required method, even though we do all our fixups in the tree
    def match(self, node):
        return False
