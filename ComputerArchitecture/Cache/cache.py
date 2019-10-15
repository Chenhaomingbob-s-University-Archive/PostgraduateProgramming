from const import CONST
import runConfig
import random
import inspect
import sys
import fileinput
import getopt

Replace_Strategy = ['Random', 'LRU', 'FIFO']
Write_Strategy = ['WriteThrough', 'WriteBack']
Block_Placement = ['DirectMapped', 'FullyAssociative', 'NWaySetAssociative']


class Block(object):
    is_valid = False
    tag = -1
    data = "I am data"
    add_time = 0  # 添加的时间- 用文件的序号来表示
    not_use_time = 0  # 使用次数

    # 定义构造方法
    def __init__(self, vaild=False, tag=-1):
        self.is_valid = vaild
        self.tag = tag


class Cache(object):
    cache_size = block_size = set_size = set_count = hits = reads = writes = replaces = total = total_time = 0
    blocks = list()

    # 定义构造方法
    def __init__(self, config):
        self.cache_size = config.cache_size  # cache 大小
        self.block_size = config.block_size  # 块的大小
        self.set_size = config.set_size  # 组大小
        self.block_number = int(self.cache_size / self.block_size)

        self.replace_strategy = config.replace_strategy
        self.block_placement = config.block_placement

        if self.block_placement == 'NWaySetAssociative':
            self.set_count = int(self.cache_size / self.block_size / self.set_size)  # 组数
        elif self.block_placement == 'FullyAssociative':
            self.set_count = 1
            self.set_size = self.block_number

        # block的总数
        for i in range(self.block_number):
            block = Block()
            self.blocks.append(block)
        print("——————运行参数————————")
        print('file', config.file_name)
        for key in vars(self):
            if key != 'blocks':
                print(key, eval('self.' + key))

    def read(self, address, time):
        print("--read from")
        self.reads += 1
        self.total += 1

        if self.block_placement == 'DirectMapped':
            # 一对一
            # find
            tag = int(address / self.block_size)
            index = tag % self.block_number
            if self.blocks[index].is_valid == True and self.blocks[index].tag == tag:
                self.hits += 1
                print("hit")
                return
            # load
            print("miss")
            self.total_time += CONST.MEM_READ_TIME
            if self.blocks[index].is_valid == False:
                # load from memory
                self.blocks[index].is_valid = True
                self.blocks[index].tag = tag
                print("memory loaded")
            else:
                # load from memory and block replace
                print("cache is full! Need replace!")
                self.replaces += 1
                self.blocks[index].is_vaild = True
                self.blocks[index].tag = tag
            return
        elif self.block_placement == 'NWaySetAssociative' or self.block_placement == 'FullyAssociative':
            # found the block
            tag = int(address / self.block_size)  # tag
            # index = tag % self.set_count
            index = int((tag / self.set_size) % self.set_count)  # index- 所在组的第一个
            # read
            self.total_time += CONST.CACHE_READ_TIME
            for i in range(index, index + self.set_size):
                if self.blocks[i].is_valid and self.blocks[i].tag == tag:
                    # hit
                    self.hits += 1
                    if self.replace_strategy == 'LRU':
                        for m in range(index, index + self.set_size):
                            self.blocks[m].not_use_time += 1
                        self.blocks[i].not_use_time = 0
                    print("hit")
                    return
            # load from memory
            print("miss")
            self.total_time += CONST.MEM_READ_TIME
            for i in range(index, index + self.set_size):
                if self.blocks[i].is_valid == False:
                    # find a free block
                    self.blocks[i].is_valid = True
                    self.blocks[i].tag = tag
                    if self.replace_strategy == 'LRU':
                        for m in range(index, index + self.set_size):
                            self.blocks[m].not_use_time += 1
                        self.blocks[i].not_use_time = 0
                    elif self.replace_strategy == 'FIFO':
                        self.blocks[i].add_time = time
                    print("memory loaded")
                    return
            # 块替换
            print("cache is full! Need replace!")
            if self.replace_strategy == 'Random':
                # random replace
                r = random.randint(0, self.set_size - 1) + index
                self.replaces += 1
                self.blocks[r].is_valid = True
                self.blocks[r].tag = tag
            elif self.replace_strategy == 'LRU':
                # 同一组之内的替换 找 not_use_time 最大的
                j = index
                for i in range(index, index + self.set_size):
                    if self.blocks[j].not_use_time < self.blocks[i].not_use_time:
                        j = i
                self.blocks[j].is_valid = True
                self.blocks[j].tag = tag
                self.blocks[j].not_use_time = 0
            elif self.replace_strategy == 'FIFO':
                # 同一组之内的替换 找 add_time 最小的
                j = index
                for i in range(index, index + self.set_size):
                    if self.blocks[j].add_time > self.blocks[i].add_time:
                        j = i
                self.blocks[j].is_valid = True
                self.blocks[j].tag = tag
                self.blocks[j].add_time = time
        return

    def write(self, address, time):
        print("write to")
        self.writes += 1
        self.total += 1

    def show_statistics(self):
        print("————————STATISTICS————————")
        print('Cache size', self.cache_size)
        print('block size', self.block_size)
        print('set size', self.set_size)
        print('total r/w', self.total)
        print('hit r/w', self.hits)
        print('replace', self.replaces)

        total = 1 if self.total == 0 else self.total
        print('hit rate:', self.hits / total)
        print('total time', self.total_time)
        print('average time', self.total_time / total)


def adjust_arg(argv, config):
    opts, args = getopt.getopt(argv, 'hf:c:b:s:r:p:',
                               ['help', 'file=', 'cache=', 'block=', 'set=', 'replace=', 'placement='])
    for opt, arg in opts:
        # TODO 参数类型检查？
        if opt in ('-h', '--help'):
            print('tips:\n-f <file_path> ')
            print('-c <cache_size>')
            print('-b <block_size>')
            print('-s <set_size>')
            print('-r [random,FIFO,LRU]')
            print('-p [d(直接映射),f（全关联）,n(n路关联)]')
            return
        elif opt in ('-f', '--file'):
            config.file_name = arg
        elif opt in ('-c', '--cache'):
            config.cache_size = arg
        elif opt in ('-b', '--block'):
            config.block_size = arg
        elif opt in ('-s', '--set'):
            config.set_size = arg
        elif opt in ('-r', '--replace'):
            config.Replace_Strategy = arg
        elif opt in ('-p', '--placement'):
            if arg in ['d', 'D', 'DirectMapped']:
                # 直接映射
                config.Block_Placement = Block_Placement[0]
            elif arg in ['f', 'F', 'FullyAssociative']:
                # 全关联
                config.Block_Placement = Block_Placement[1]
            elif arg in ['n', 'N', 'NWaySetAssociative']:
                # n路关联
                config.Block_Placement = Block_Placement[2]
    return config


def main(argv):
    config = runConfig.RunConfig()
    config = adjust_arg(argv, config)
    if config == None:
        return
    cache = Cache(config)

    file = open(config.file_name)
    for time, line in enumerate(file.readlines()):
        address, rw = line.split(maxsplit=1)
        rw = rw.replace('\n', "")
        if rw == 'R':
            cache.read(int('0x' + address, 16), time)
        elif rw == 'W':
            cache.write(int('0x' + address, 16), time)
        else:
            raise Exception("data format error")
    cache.show_statistics()


if __name__ == '__main__':
    main(sys.argv[1:])
