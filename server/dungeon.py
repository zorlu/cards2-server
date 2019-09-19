class Dungeon(object):
    deck_dbid = None
    name = None
    cardback = None
    stage = None
    next_stage = None
    boss = {
        'name': None,
        'portrait': None,
        'hp': None
    }

    def __repr__(self):
        return "<Dungeon {0} stage {1}>".format(self.name, self.stage)
