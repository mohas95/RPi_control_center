




class Relay():
    __init__(self, pin, name, state = False):
        self.state = state
        self.pin = pin
        self.name = name

    @property
    def name(self):
        '''
        '''
        return self._name

    @name.setter
    def name(self, value):
        '''
        '''
        self._name = value

    @property
    def pin(self):
        '''
        '''
        return self._pin

    @pin.setter
    def pin(self, value):
        '''
        '''
        self._pin = value

    @property
    def state(self):
        '''
        '''
        return self._pin

    @state.setter
    def state(self, value):
        '''
        '''
        self._state = value
