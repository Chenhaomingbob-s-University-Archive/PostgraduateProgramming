# 模拟Cache
````
python cache.py -h # 查看帮助
-f <file_path> -c <cache_size> -b <block_size> -s <set_size>
````
| name | 命令| (缩写)可选值 |
| ---- | ----| ----|
| Block_Placement |-p|['(d) DirectMapped' , '(f) FullyAssociative' , '(n) NWaySetAssociative']  |
| Replace_Strategy|-s|['Random', 'LRU', 'FIFO']|