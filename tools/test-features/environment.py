
def before_all(context):
    context.testing_stuff = False
    context.stuff_set_up = False

def before_feature(context, feature):
    context.is_spammy = 'spam' in feature.tags

