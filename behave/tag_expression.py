class TagExpression(object):
    def __init__(self, tag_expressions):
        self.ands = []
        self.limits = {}
        
        for expr in tag_expressions:
            self.add([e.strip() for e in expr.strip().split(',')])
    
    def check(self, tags):
        if not self.ands:
            return True
        
        params = dict([(tag, True) for tag in tags])
        
        def test_tag(tag):
            if tag.startswith('~'):
                return not params.get(tag[1:], False)
            return params.get(tag, False)
        
        for ors in self.ands:
            if not ors:
                continue
            if True not in [test_tag(tag) for tag in ors]:
                return False
        return True
    
    def add(self, tags):
        negatives = [tag for tag in tags if tag.startswith('~')]
        positives = [tag for tag in tags if not tag.startswith('~')]
        
        self.ands.append(self.store_and_extract_limits(negatives, True))
        self.ands.append(self.store_and_extract_limits(positives, False))
    
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
        
        return tags_with_negation

    def __len__(self):
        return len(self.ands)
        