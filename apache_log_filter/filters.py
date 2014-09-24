from collections.abc import Sequence
import logging
import re

logger = logging.getLogger(__name__)


class DictFilter(dict):
    def __init__(self, arg={}):
        super().__init__(arg)
        self.lt_keys, self.gt_keys, self.re_keys = ([], [], [])
        self._updateKeyIndex()

    def __setitem__(self, *args, **kwargs):
        super().__setitem__(args, kwargs)
        self._updateKeyIndex

    def __eq__(self, value):
        for key in value.keys() & self.re_keys:
            if not self[key].search(value[key]):
                return False

        for key in value.keys() & self.lt_keys:
            if not self[key] < value[key]:
                return False

        for key in value.keys() & self.gt_keys:
            if not self[key] > value[key]:
                return False

        return True

    def fromkeys(self, *args, **kwargs):
        super().fromkeys(*args, **kwargs)
        self._updateKeyIndex()

    def update(self, arg):
        super().update(arg)
        self._updateKeyIndex()

    def _updateKeyIndex(self):
        #TODO also call after item deletion
        for index in [ self.lt_keys, self.gt_keys, self.re_keys ]:
            index.clear()

        for key in self.keys():
            if key.startswith('lt_'):
                self.lt_keys.append(key)
            elif key.startswith('gt_'):
                self.gt_keys.append(key)
            else:
                self.re_keys.append(key)

    def _compile(self):
        compiled = {}
        for key, value in self.items():
            if not (key.startswith('lt_') or key.startswith('gt_')) \
               and isinstance(value, str):
                   compiled[key] = re.compile(value)
        self.update(compiled)


class FilterSet(list):
    """A set of filters that will be evaluated in order.

    Args:
        filterItems: a sequence of two-value-tuples:
                     the first value is a bool; if True a matching item is
                     considered white-, if False blacklisted
                     the second value is a filter_object, either a compiled
                     re.matchobject or directory that includes these as values;
                     any string will be compiled to a re.matchobject
    """

    def __init__(self, arg=[]):
        self._setType()
        try:
            if not isinstance(arg, Sequence):
                raise ValueError("I'm expecting a sequence of two-value tuples.")
            checked_arg = []
            for value in arg:
                checked_arg.append(self._checkType(value))
        except:
            raise
        else:
            super().__init__(checked_arg)

    def __call__(self, line):
        for rv, filter_object in self:
            if not rv and self.test(filter_object, line):
                logger.debug("Blacklisted ({})".format(filter_object.__str__()))
                return False    # skip blacklisted
            else:
                logger.debug("Not blacklisted ({})".format(filter_object.__str__()))
            if rv and not self.test(filter_object, line):
                logger.debug("Not whitelisted ({})".format(filter_object.__str__()))
                return False    # skip if not whitelisted
            else:
                logger.debug("Whitelisted ({})".format(filter_object.__str__()))
        return True             # matched all criteria

    def __setitem__(self, key, value):
        super().insert(key, self._checkType(value))

    def append(self, value):
        super().append(self._checkType(value))

    def extend(self, sequence):
        if not isinstance(sequence, Sequence):
            raise ValueError("I'm expecting a sequence of two-value tuples.")
        checked_sequence = []
        for value in sequence:
            checked_sequence.append(self._checkType(value))
        super().extend(checked_sequence)

    def insert(self, index, value):
        super().insert(index, self._checkType(value))

    def _setType(self):
        raise NotImplementedError("A subclass of FilterSet must implement a _setType method.")

    def _checkType(self, value):
        if not ( isinstance(value, tuple) and len(value) == 2 ):
            raise ValueError("{} is not a (two, value) tuple.".format(value))

        if not isinstance(value[0], bool):
            raise ValueError("First value of {} must be a bool.".format(value))

        compiled_value = self._compileFilter(value[1])

        if not isinstance(compiled_value, self.type):
            raise ValueError(("{} is not a valid filter-type; " +
                  "expecting a {}.").format(type(compiled_value), self.type))
        return (value[0], compiled_value)

    def __compileFilter(self, arg):
        raise NotImplementedError("A subclass of FilterSet must implement a _compileFilter method.")
        return arg

    def test(self, rule, line):
        raise NotImplementedError("A subclass of FilterSet must implement a test method.")


class RegExFilterSet(FilterSet):

    def _setType(self):
        self.type = type(re.compile(''))

    def _compileFilter(self, value):
        if isinstance(value, str):
            value = re.compile(value)
        return value

    def test(self, rule, line):
        if not isinstance (line, str):
            raise ValueError("{} ist not an instance of str.".format(line))
        return rule.search(line)


class DictFilterSet(FilterSet):

    def _setType(self):
        self.type = DictFilter

    def _compileFilter(self, value):
        if not isinstance(value, DictFilter):
            value = DictFilter(value)
        value._compile()
        return value

    def test(self, rule, parsed_line):
        return rule == parsed_line
