from datetime import datetime

class datetime(datetime):

    def __init__(self, *args, **kwargs):
        super(datetime, self).__init__(*args, **kwargs)
        self.precision = None
 
