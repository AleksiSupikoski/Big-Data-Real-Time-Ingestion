class clientBatchIngestApp:
    def __init__(self, app, appfile, tenantServiceProfile):
        self.app = app
        self.appfile = appfile
        self.tenantServiceProfile = tenantServiceProfile
        #self.profilefile = profilefile
    
    def get_app(self):
        return self.app
    
    def get_tenantServiceProfile(self):
        return self.tenantServiceProfile
    
    def get_appfile(self):
        return self.appfile
    
    #def get_profilefile(self):
    #    return self.profilefile