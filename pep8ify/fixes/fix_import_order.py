from lib2to3.fixer_base import BaseFix
from lib2to3.pygram import python_symbols as symbols
from lib2to3.fixer_util import is_import, syms, Node

import pdb
from pprint import pprint
pst = pdb.set_trace

def empty_stmt():
    new_expr = Node(syms.expr_stmt, [])
    new_stmt = Node(syms.simple_stmt, [new_expr])
    new_stmt.changed()
    return new_stmt

print symbols.import_name
class FixImportOrder(BaseFix):
    u'''
    Imports should be sorted alphabetically in groups.
    '''
    def start_tree(self, tree, filename):
#        pst()
        # Remove the prefix so header material doesn't get juggled
        prefix_sep = '\n\n'
        original_prefix, _, tail = tree.prefix.rpartition(prefix_sep)
        tree.prefix = tail
        import_nodes = []
        for node in tree.children:
            if not (node.type == symbols.simple_stmt and
                    is_import(node.children[0])):
                        break
            import_nodes.append(node)
        def sortem(node):
            return str(node).replace(node.prefix, '', 1)
        for node in sorted(import_nodes, key=sortem):
            node.prefix = node.prefix.lstrip()
            print node
        # put the old prefix material back
        tree.prefix = original_prefix + prefix_sep + tree.prefix


    def match(self, node):
        return False

    def match2(self, node):
        nodes = []
        cur_node = node
        while (cur_node.type == symbols.simple_stmt and
               is_import(cur_node.children[0])):
            nodes.append(cur_node)
#            pprint(cur_node)
            cur_node = cur_node.next_sibling
            cur_node.prefix = ''
#            cur_node.changed()
        return nodes
    def transform2(self, node, results):
        return node

    def transform2(self, node, results):
        orig_prefix = node.prefix
        node.prefix= ''
        nodes = results
#        pdb.set_trace()
        if nodes:
            print len(nodes)
            def sortem(x):
#                return ''.join(map(str, x.children[0].children[1:]))
                return ''.join(map(str, x.children[0].children))
            sorted_nodes  = sorted(nodes, key=sortem)
            childs = []
            for n in sorted_nodes:
                import pdb;pdb.set_trace()
                print repr(n.children[0].children)
                childs.append(n.children)
            for n, s, c in zip(nodes, sorted_nodes, childs):
                print str(n).strip(), '----', str(s).strip()
                n.children = c
#                if n.prefix == '\n':
#                    n.prefix = ''
            print "------"
        node.prefix = orig_prefix
        return node
