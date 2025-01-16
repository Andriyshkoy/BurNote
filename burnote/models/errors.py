
class PasswordRequiredError(Exception):
    def __init__(self):
        self.message = 'Password is required'
        super().__init__(self.message)
