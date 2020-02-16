class UserInformation:
    def __init__(self):
        pass

class PlatformInformation:
    def __init__(self):
        pass

class Eregec:
    def __init__(self, host):
        self.host = "http://" + host
        self.errorMessage = ""

    def login(self, userName, password):
        return False

    def logout(self):
        pass

    def getUserId(self):
        return None

    def getErrorMessage(self):
        return self.errorMessage

    def getIntegerPlatformData(self, name):
        return None

    def getFloatPlatformData(self, name):
        return None

    def getStringPlatformData(self, name):
        return None

    def getPlatformInformation(self): 
        return None

    def getUserInformation(self):
        return None

    def isLogin(self):
        return False

    def sendCommand(self, command):
        return False

    def downloadPlatformData(self):
        return False
