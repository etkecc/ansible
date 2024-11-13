import hashlib

def sha256(input_string):
    return hashlib.sha256(input_string.encode('utf-8')).hexdigest()

class FilterModule(object):
    def filters(self):
        return {
            'sha256': sha256
        }

