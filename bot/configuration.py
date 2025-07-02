class Config:

    def __init__(self, path='configuration.yaml'):
        """
        read a configuration file in yaml format
        args:
            path: the path of the configuration file
            dev: development mode
                'True' or 'False'
        """
        import yaml
        with open(path, 'r') as stream:
            self.config = yaml.safe_load(stream)
        stream.close()
        self.mode = self.config['mode']
        self.token = self.config[self.mode][0]['token']
        self.botname = self.config[self.mode][0]['botname']
        self.username = self.config[self.mode][0]['username']

    def get_mode(self):
        return self.mode

    def get_token(self):
        """return token from the configuration file
        """
        return self.config[self.mode][0]['token']

    def get_botname(self):

        return self.config[self.mode][0]['botname']

    def get_username(self):

        return self.config[self.mode][0]['username']

    def show_label(self):
        from ansimarkup import ansiprint as print
        from pyfiglet import figlet_format
        print("<yellow>"+figlet_format(self.botname)+"</yellow>")
        print("<yellow>@"+ self.username +"</yellow>\n<green>https://t.me/" + self.username+'</green>' )
        if self.mode == 'dev':
            print('<red>'+ self.mode + '-mode</red>')