class BaseModel():
    def populate(self, data):
        for key, value in data.iteritems():
            if hasattr(self, key):
                # If this is a field of the class, set it
                setattr(self, key, value)