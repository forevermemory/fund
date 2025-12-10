

class Param(object):
    def __init__(self, 
                 _key:str,
                 out_dir:str,
                 enable_fenhong=False, 
                 enable_nianfei=False, 
                 enable_huiche=False):
        
        self._key = _key
        self.out_dir = out_dir
        self.enable_fenhong = enable_fenhong
        self.enable_nianfei = enable_nianfei
        self.enable_huiche = enable_huiche