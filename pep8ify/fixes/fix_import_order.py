from lib2to3.fixer_base import BaseFix
from lib2to3.pygram import python_symbols as symbols
from lib2to3.fixer_util import is_import

import pdb
from pprint import pprint

print symbols.import_name
class FixImportOrder(BaseFix):
    u'''
    Imports should be sorted alphabetically in groups.
    '''

    def match(self, node):
        nodes = []
        cur_node = node
        while (cur_node.type == symbols.simple_stmt and
               is_import(cur_node.children[0])):
            nodes.append(cur_node)
#            pprint(cur_node)
            cur_node = cur_node.next_sibling
        return nodes

    def transform(self, node, results):
        nodes = results
#        pdb.set_trace()
        if nodes:
            print len(nodes)
            def sortem(x):
#                return ''.join(map(str, x.children[0].children[1:]))
                return ''.join(map(str, x.children[0].children[:]))
            sorted_nodes  = sorted(nodes, key=sortem)
#            print ''.join([str(x) for x in sorted_nodes])
            childs = []
            for n in sorted_nodes:
                childs.append(n.children)
            for n, s, c in zip(nodes, sorted_nodes, childs):
                print str(n).strip(), '----', str(s).strip()
                n.children = c
                if n.prefix == '\n':
                    n.prefix = ''
            print "------"
        return node
