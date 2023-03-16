class clientStreamIngestApp:
    def __init__(self, app, appfile):
        self.app = app
        self.appfile = appfile
    
    def get_app(self):
        return self.app
    
    def get_appfile(self):
        return self.appfile