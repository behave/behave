class TagExpression(object):
    def __init__(self, tag_expressions):
        self.ands = []
        self.limits = {}

        for expr in tag_expressions:
            self.add([e.strip() for e in expr.strip().split(',')])

    def check(self, tags):
        if not self.ands:
            return True

        params = set(tags)

        def test_tag(tag):
            if tag.startswith('-'):
                return tag[1:] not in params
            return tag in params

        return all(any(test_tag(tag) for tag in ors)
            for ors in self.ands)

    def add(self, tags):
        negatives = []
        positives = []

        for tag in tags:
            if tag.startswith('@'):
                positives.append(tag[1:])
            elif tag.startswith('-@'):
                negatives.append('-' + tag[2:])
            elif tag.startswith('-'):
                negatives.append(tag)
            else:
                positives.append(tag)

        self.store_and_extract_limits(negatives, True)
        self.store_and_extract_limits(positives, False)

    def store_and_extract_limits(self, tags, negated):
        tags_with_negation = []

        for tag in tags:
            tag = tag.split(':')
            tag_with_negation = tag.pop(0)
            tags_with_negation.append(tag_with_negation)

            if tag:
                limit = int(tag[0])
                if negated:
                    tag_without_negation = tag_with_negation[1:]
                else:
                    tag_without_negation = tag_with_negation
                if tag_without_negation in self.limits and \
                    self.limits[tag_without_negation] != limit:
                    msg = "Inconsistent tag limits for {0}: {1:d} and {2:d}"
                    msg = msg.format(tag_without_negation,
                                     self.limits[tag_without_negation], limit)
                    raise Exception(msg)
                self.limits[tag_without_negation] = limit

        if tags_with_negation:
            self.ands.append(tags_with_negation)

    def __len__(self):
        return len(self.ands)
