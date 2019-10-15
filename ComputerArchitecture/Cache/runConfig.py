class RunConfig(object):
    file_name = None
    cache_size = 1024
    block_size = 4
    set_size = 2  # n 路组关联
    block_placement = 'DirectMapped'
    replace_strategy = 'Random'
    write_strategy = 'WriteThrough'

    def __init__(self):
        self.file_name = './data/bzip.trace'
