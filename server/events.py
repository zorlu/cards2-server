from app.settings import logger


class Event(object):
    type = None
    card = None
    data = None
    callback = None
    unregister_callback = None

    def __init__(self, key, card, callback, unregister_callback=None):
        self.type = key
        self.card = card
        self.callback = callback
        self.unregister_callback = unregister_callback

    def __repr__(self):
        return "<Event {0} {1}>".format(self.type, self.card.title)

    def run(self, data):
        logger.info("Events> Running trigger:{0} card:{1}".format(self.type, self.card.title))
        tailored = self.callback(data)
        """
        for spell in self.card.spells:
            if spell.trigger == self.type:
                
                tailored += spell.cast(data)
        """
        return [] if not tailored else tailored



class GameEvents(object):
    events = []
    tailored = []

    def __init__(self):
        self.events = []
        self.tailored = []

    def register(self, key, card, callback, unregister_callback=None):
        # logger.info("GameEvents.register key:{0} card:{1}".format(key, card.title))
        self.events.append(Event(key, card, callback, unregister_callback=unregister_callback))
        logger.info("Events> Registered {0} {1} callback={2}".format(key, card.title, callback))

    def unregister(self, card, key=None):
        removed = []
        for event in self.events:
            if event.card.uuid == card.uuid:
                if key:
                    if event.type == key:
                        removed.append(event)
                else:
                    removed.append(event)

        for rem in removed:
            logger.info("Events> Unregistered key:{0} {1}".format(key, rem.card.title))
            rem.unregister_callback()  # TODO maybe some params?
            self.events.remove(rem)

    def fire(self, key, data):
        logger.info("Events> Firing {0} {1}".format(key, data))
        tailored = []
        triggered = 0
        for event in self.events:
            if event.type == key:
                tailored += event.run(data)
                triggered += 1

        if triggered > 0:
            logger.info("Events> Fired: {0} {1} events triggered!".format(key, triggered))

        return tailored
