#qtable.py 

table_md = '''
| Queue Name         | Min nodes/job| Min cores/job |Max nodes/job  | Max cores/job  | Max jobs in Q   | Max jobs running   |  Max time (h) |   Notes  | Access  |
| ---                | ---          | ---           |---            | ---            | ---             | ---                | ---           |  ---     |   ---   |
| serial             |    1         |    1          |   1           |     23         |  24 |  10       |  48 | For single-node non-parallel jobs.  |  |
| seriallong         |    1         |    1          |   1           |     12         |  24 |  10       | 144 | For very long sub 1-node jobs.  |  |
| smp                |    1         |   24          |   1           |     24         |  20 |  10       |  96 | For single-node parallel jobs.  |  |
| **:green[normal]** |    2         |   25          |  10           |    240         |  20 |  10       |  48 | The standard queue for parallel jobs   |
| large              |   11         |  264          |1000           |   2400         |  10 |  5        |  96 | For large parallel runs  | Restricted  |
| xlarge             | 1001         | 2424          | 250           |   6000         |  2  |  1        |  96 | For extra-large parallel runs  | Restricted  |
| bigmem             |    1         |   28          |   5           |    280         |  4  |  1        |  48 | For the large memory (1TiB RAM) nodes. | Restricted  |
| vis                |    1         |    1          |   1           |     12         |  1  |  1        |  3  | Visualisation node  |  |
| test               |    1         |    1          |   1           |     24         |  1  |  1        |  3  | Normal nodes, for testing only  |  |
| gpu_1              |    1         |    1          |   1           |     10         |     |  2        |  12 | Up to 10 cpus, 1 GPU        |  |
| gpu_2              |    1         |    1          |   1           |     20         |     |  2        |  12 | Up to 20 cpus, 2 GPUs        |  |
| gpu_3              |    1         |    1          |   1           |     36         |     |  2        |  12 | Up to 36 cpus, 3 GPUs        |  |
| gpu_4              |    1         |    1          |   1           |     40         |     |  2        |  12 | Up to 40 cpus, 4 GPUs        |  |
| gpu_long           |    1         |    1          |   1           |     20         |     |  1        |  24 | Up to 20 cpus, 1 or 2 GPUs        |  Restricted |
| **:red[express]**  |    2         |   25          | 100           |   2400         |     | 100 nodes |  96 | For paid commercial use only  | Restricted  |
'''
