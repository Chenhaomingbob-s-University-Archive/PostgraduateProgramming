class RunConfig(object):
    file_name = None
    cache_size = 1024
    block_size = 4
    set_size = 2  # n 路组关联
    block_placement = 'DirectMapped'
    replace_strategy = 'Random'

    # write_strategy = 'WriteThrough'

    def __init__(self):
        self.file_name = './data/gcc.trace'
        self.cache_size = 1024
        self.block_size = 4
        self.set_size = 2  # n 路组关联
        # self.block_placement = 'DirectMapped'
        self.block_placement = 'FullyAssociative'
        # self.block_placement = 'NWaySetAssociative'
        self.replace_strategy = 'Random'
        # self.replace_strategy = 'FIFO'
        # self.replace_strategy = 'LRU'
