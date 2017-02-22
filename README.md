# A python qsub wrapper
Henry Juho Barton

# Introduction

This repository contains a small python module, ```qsub.py``` which provides functionally to write and submitted shell scripts to the 'Son of grid engine'. This developmental branch also contains initial compatibility with the SLURM system as well. Also included is a standalone script ```qsub_gen.py``` which provides similar functionality from the command line.

# qsub.py
## Installation 

The module can be used by adding its location to your ```.bash_profile```, as follows:

```
emacs ~/.bash_profile
```

and then adding the lines: 

```bash
PYTHONPATH=${PYTHONPATH}:/path/to/module_directory
export PYTHONPATH
```

before finally running:

```
source ~/.bash_profile
```

## Examples
### Importing

The module can be imported as follows:

```python
from qsub.py import *
```

The module use three main functions ```q_print```, ```q_write``` and ```q_sub```. All these functions have take the same arguments, only the output differs, as they print, write and submit bash scripts respectively.

For ease of explanation examples are provided for ```q_print``` only.

### Simple submission script - SGE

To print a simple submission script you need only specify a command and an output location and prefix for job error and output messages:

```python
from qsub import *

q_print(['example_command -a 1 -b 2 -c 3'], out='example/output/location/prefix')
```

This gives:

```bash
#!/bin/bash

source ~/.bash_profile

#$-l arch=intel*
#$-l h_rt=8:00:00
#$-l mem=6G
#$-l rmem=2G


#$-N prefix_job.sh
#$-o example/output/location/prefix.out
#$-e example/output/location/prefix.error

example_command -a 1 -b 2 -c 3
```

### Simple submission script - SLURM

To print a simple submission script you need only specify a command and an output location and prefix for job error and output messages:

```python
from qsub import *

q_print(['example_command -a 1 -b 2 -c 3'], out='example/output/location/prefix', scheduler='SLURM')
```

This gives:

```python
#!/bin/bash

source ~/.bash_profile

#SBATCH -t 8:00:00
#SBATCH --mem_per_cpu 2G


#SBATCH -J prefix_job.sh
#SBATCH -o example/output/location/prefix.out
#SBATCH -e example/output/location/prefix.error

example_command -a 1 -b 2 -c 3

```

### Complicated submission script

A job with to commands to run, a precursor job to wait for, a job id specified, time increased to 78 hours and 20GB of memmory requested:

```python
from qsub import *

q_print(['process1 -a 1 -b 2 -c 3', 'process2 -d 4 -e 5 -f 5'],
        out='example/out/location/prefix',
        t=78,
        mem=20, rmem=20,
        hold=['precursor_job'],
        jid='name_of_job')
```

This yields:

```bash
#!/bin/bash

source ~/.bash_profile

#$-l arch=intel*
#$-l h_rt=78:00:00
#$-l mem=20G
#$-l rmem=20G


#$-N name_of_job
#$-o example/out/location/prefix.out
#$-e example/out/location/prefix.error

#$-hold_jid precursor_job

process1 -a 1 -b 2 -c 3
process2 -d 4 -e 5 -f 5
```

### Array job submission

Array jobs can be specied with the ```array=``` option. This is an example of running a script on 20 input files numbered 1 to 20 using an array (note the use of $SGE_TASK_ID in the command):

```python
from qsub import *

example_process = './example_script.py -in input_file$SGE_TASK_ID.txt -out output_file$SGE_TASK_ID.txt'
number_of_files = 20

q_print([example_process],
        out='example/out/location/prefix',
        t=72,
        jid='name_of_job',
        array=[1, number_of_files])
```

This gives the following submission script:

```bash
#!/bin/bash

source ~/.bash_profile

#$-t 1-20

#$-l arch=intel*
#$-l h_rt=72:00:00
#$-l mem=6G
#$-l rmem=2G


#$-N name_of_job
#$-o example/out/location/prefix.out
#$-e example/out/location/prefix.error

./example_script.py -in input_file$SGE_TASK_ID.txt -out output_file$SGE_TASK_ID.txt
```

## Parameters

```python
q_print(cmd, out, mo='NONE', t=8, rmem=2, mem=6, hold='NONE', jid='DEFAULT', 
        tr=1, evolgen=False, array='no_array')
```

### cmd: list

  List of commands (strings) to call in the submission job.

### out: str

  Location and file prefix for output and error files.
    
### mo: list

  List of modules required to run jobs. Options: 'python' , 'java', 'gatk' ', 'R', module locations will need to be updated when not running on Sheffield cluster.
    
### t: int

   Time requested for job.

### rmem: int

  Amount of real memmory requested.

### mem: int

  Amount of virtual memmory requested.

### hold: list

  List of job names to wait for untill starting job.

### jid: str

  ID for the job.
    
### tr: int

  Number of cores requested.

### evolgen: bool

  If True will submit jobs to the Zeng Lab queue on the Sheffield cluster (requires access rights).

### array: list

  List of two intergers specifying the start and end of the array
