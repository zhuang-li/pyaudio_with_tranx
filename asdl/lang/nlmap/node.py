try:
    from cStringIO import StringIO
except:
    from io import StringIO
from collections import Iterable
class Node(object):
    def __init__(self, name, children=None):
        self.name = name
        self.parent = None
        self.children = list()
        if children:
            if isinstance(children, Iterable):
                for child in children:
                    self.add_child(child)
            elif isinstance(children, Node):
                self.add_child(children)
            else:
                raise ValueError('Wrong type for child nodes')

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def __hash__(self):
        code = hash(self.name)

        for child in self.children:
            code = code * 37 + hash(child)

        return code

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.name != other.name:
            return False

        if len(self.children) != len(other.children):
            return False

        return self.children == other.children

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Node[%s, %d children]' % (self.name, len(self.children))

    @property
    def is_leaf(self):
        return len(self.children) == 0

    def to_string(self, sb=None):
        is_root = False
        if sb is None:
            is_root = True
            sb = StringIO()

        if self.is_leaf:
            sb.write(self.name)
        else:
            sb.write(self.name)
            sb.write(' (')
            first_child = self.children[0]
            sb.write(' ')
            first_child.to_string(sb)

            for child in self.children[1:]:
                sb.write(' , ')
                child.to_string(sb)

            sb.write(' )')

        if is_root:
            return sb.getvalue()
