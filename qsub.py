import subprocess
import os


# todo consider constructing this from module lists
modules = {'python': 'apps/python/2.7', 'java': 'apps/java/1.7', 'gatk': 'apps/binapps/GATK', 'R': 'apps/R/3.2.1'}


def float2qsubtime(time_float):
    hours = str(int(time_float))
    minutes = str(int((time_float - int(time_float)) * 60))
    if len(minutes) == 1:
        minutes = '0' + minutes
    return hours + ':' + minutes + ':00'


def q_script(cmd, out, mo='NONE', t=8.0, rmem=2, mem=6, hold='NONE',
             jid='DEFAULT', tr=1, evolgen=False, node='0', array='no_array'):

    """
    function that returns the contents a bash script suitable for submission to the son of grid engine, using qsub

    :param cmd: list
    :param out: str
    :param mo: list
    :param t: float
    :param rmem: int
    :param mem: int
    :param hold: list
    :param jid: str
    :param tr: int
    :param evolgen: bool
    :param node: str
    :param array: list
    :return:
    """

    # check options
    if type(cmd) is not list:
        raise TypeError('cmd must be a list')

    if type(cmd[0]) is not str or type(node) is not str:
        raise TypeError('entries in cmd list and node must be str')

    if not mo == 'NONE':
        if type(mo) is not list:
            raise TypeError('mo must be a list')
        for m in mo:
            if m not in modules.keys():
                raise KeyError(m + ' not a valid module')

    if not hold == 'NONE':
        if type(hold) is not list:
            raise TypeError('hold must be a list')

    if type(t) is int:
        t = float(t)

    if type(t) is not float:
        raise TypeError('t must be a float')

    if type(rmem) is not int or type(mem) is not int \
            or type(tr) is not int:

        raise TypeError('rmem, mem, tr and node must be integers')

    if array != 'no_array' and type(array) is not list:
        raise TypeError('array must be a list')

    # set variables
    run_time = '#$-l h_rt=' + float2qsubtime(t) + '\n'
    memory = '#$-l mem='+str(mem)+'G\n#$-l rmem='+str(rmem)+'G\n'
    file_pos = out.rfind('/')+1  # identifies position of file name in path string
    if jid == 'DEFAULT':
        output_name = out[0:file_pos] + out[file_pos:] + '_job.sh'
    else:
        output_name = out[0:file_pos] + jid
    outs = '\n#$-N ' + output_name[output_name.rfind('/')+1:] + '\n#$-o '+out+'.out\n#$-e '+out+'.error\n'
    out_dir_path = out[:out.rfind('/') + 1]
    if not os.path.isdir(out_dir_path):
        os.makedirs(out_dir_path)
    node_str = ''
    if node != '0':
        node_str = '#$-l h=node' + node + '\n'

    # construct shell contents
    shell_contents = '#!/bin/bash\n\nsource ~/.bash_profile\n'
    if not mo == 'NONE':
        for m in mo:
            shell_contents += 'module load  ' + modules[m] + '\n'
    if array != 'no_array':
        shell_contents += '\n#$-t ' + str(array[0]) + '-' + str(array[1]) + '\n'
    shell_contents += '\n#$-l arch=intel*\n' + run_time + memory + '\n'
    if tr != 1:
        shell_contents += '#$-pe openmp ' + str(tr) + '\n'
    if evolgen is True:
        shell_contents += '#$-P evolgen\n#$-q evolgen.q\n'
    shell_contents += node_str
    shell_contents += outs + '\n'
    if hold is not 'NONE':
        hold = ','.join(hold)
        shell_contents += '#$-hold_jid ' + hold + '\n\n'
    for x in cmd:
        shell_contents += x + '\n'

    # output shell script string
    return shell_contents, output_name


def s_script(cmd, out, mo='NONE', t=8.0, rmem=2, mem=6, hold='NONE',
             jid='DEFAULT', tr=1, evolgen=False, node='0', array='no_array'):

    """
    function that returns the contents of a bash script suitable for submission to slurm, using sbatch

    :param cmd: list
    :param out: str
    :param mo: list
    :param t: float
    :param rmem: int
    :param mem: int
    :param hold: list
    :param jid: str
    :param tr: int
    :param evolgen: bool
    :param node: str
    :param array: list
    :return:
    """

    # check options
    if type(cmd) is not list:
        raise TypeError('cmd must be a list')

    if type(cmd[0]) is not str or type(node) is not str:
        raise TypeError('entries in cmd list and node must be str')

    if not mo == 'NONE':
        if type(mo) is not list:
            raise TypeError('mo must be a list')

    if not hold == 'NONE':
        if type(hold) is not list:
            raise TypeError('hold must be a list')

    if type(t) is int:
        t = float(t)

    if type(t) is not float:
        raise TypeError('t must be a float')

    if type(rmem) is not int or type(mem) is not int \
            or type(tr) is not int:

        raise TypeError('rmem, mem, tr and node must be integers')

    if array != 'no_array' and type(array) is not list:
        raise TypeError('array must be a list')

    # set variables
    run_time = '#SBATCH --time=' + float2qsubtime(t) + '\n'
    memory = '#SBATCH --mem-per-cpu=' + str(rmem) + 'G\n'
    file_pos = out.rfind('/')+1  # identifies position of file name in path string
    if jid == 'DEFAULT':
        output_name = out[0:file_pos] + out[file_pos:] + '_job.sh'
    else:
        output_name = out[0:file_pos] + jid
    outs = ('\n#SBATCH --account=project_2002047\n'
            '\n#SBATCH --job-name=' + output_name[output_name.rfind('/')+1:] +
            '\n#SBATCH --output='+out+'.out'
            '\n#SBATCH --error='+out+'.error\n')
    out_dir_path = out[:out.rfind('/') + 1]
    if not os.path.isdir(out_dir_path):
        os.makedirs(out_dir_path)
    node_str = ''
    if node != '0':
        node_str = '#SBATCH -w ' + node + '\n'

    # determine queues and constraints
    partitions = []
    if tr == 1 and t <= 3*24:
        partitions.append('small')
    elif tr <= 4000 and t <= 3*24:
        partitions.append('large')
    elif tr <= 40 and t <= 14*24:
        partitions.append('longrun')
    elif tr <= 160 and t <= 3*24 and rmem > 382:
        partitions.append('hugemem')
    else:
        partitions.append('hugemem_longrun')

    part_str = '#SBATCH --partition=' + ','.join(partitions) + '\n'

    # construct shell contents
    shell_contents = '#!/bin/bash\n\n'
    if not mo == 'NONE':
        for m in mo:
            shell_contents += 'module load  ' + m + '\n'
    if array != 'no_array':
        shell_contents += '#SBATCH --array=' + str(array[0]) + '-' + str(array[1]) + '\n'
    shell_contents += run_time + memory + '\n'
    if tr != 1:
        tr_str = ('#SBATCH -N {tr}\n'
                  '#SBATCH --cpus-per-task=1\n'
                  '#SBATCH --ntasks={tr}\n').format(tr=tr)
        shell_contents += tr_str

    shell_contents += part_str
    shell_contents += node_str
    shell_contents += outs + '\n'
    # if hold is not 'NONE':
    #     hold = ','.join(hold)
    #     shell_contents += '#$-hold_jid ' + hold + '\n\n'
    for x in cmd:
        shell_contents += x + '\n'

    # output shell script string
    return shell_contents, output_name


def q_print(cmd, out, mo='NONE', t=8.0, rmem=2, mem=6, hold='NONE', jid='DEFAULT', tr=1, evolgen=False,
            node='0', array='no_array', scheduler='SGE'):

    """
    function that prints a bash script suitable for submission to the son of grid engine or slurm, using qsub or sbatch

    :param cmd: list
    :param out: str
    :param mo: list
    :param t: float
    :param rmem: int
    :param mem: int
    :param hold: list
    :param jid: str
    :param tr: int
    :param evolgen: bool
    :param node: str
    :param array: list
    :param scheduler: str
    :return:
    """

    sched_opts = {'SGE', 'SLURM'}
    if scheduler not in sched_opts:
        raise ValueError('Only SGE and SLURM schedulers are supported at present!')

    if scheduler == 'SGE':
        script = q_script(cmd, out, mo=mo, t=t, rmem=rmem, mem=mem, hold=hold,
                          jid=jid, tr=tr, evolgen=evolgen, node=node, array=array)[0]
    else:
        script = s_script(cmd, out, mo=mo, t=t, rmem=rmem, mem=mem, hold=hold,
                          jid=jid, tr=tr, evolgen=evolgen, node=node, array=array)[0]
    print(script)


def q_write(cmd, out, mo='NONE', t=8.0, rmem=2, mem=6, hold='NONE', jid='DEFAULT', tr=1, evolgen=False,
            node='0', array='no_array', scheduler='SGE'):

    """
    function that prints a bash script suitable for submission to the son of grid engine or slurm, using qsub or sbatch

    :param cmd: list
    :param out: str
    :param mo: list
    :param t: float
    :param rmem: int
    :param mem: int
    :param hold: list
    :param jid: str
    :param tr: int
    :param evolgen: bool
    :param node: str
    :param array: list
    :param scheduler: str
    :return:
    """

    sched_opts = {'SGE', 'SLURM'}
    if scheduler not in sched_opts:
        raise ValueError('Only SGE and SLURM schedulers are supported at present!')

    if scheduler == 'SGE':
        script_data = q_script(cmd, out, mo=mo, t=t, rmem=rmem, mem=mem, hold=hold,
                               jid=jid, tr=tr, evolgen=evolgen, node=node, array=array)
    else:
        script_data = s_script(cmd, out, mo=mo, t=t, rmem=rmem, mem=mem, hold=hold,
                               jid=jid, tr=tr, evolgen=evolgen, node=node, array=array)

    script = script_data[0]
    output_name = script_data[1]

    # output shell script
    output = open(output_name, 'w')
    output.write(script)
    output.close()


def q_sub(cmd, out, mo='NONE', t=8.0, rmem=2, mem=6, hold='NONE', jid='DEFAULT', tr=1, evolgen=False,
          node='0', array='no_array', scheduler='SGE'):

    """
    function that prints a bash script suitable for submission to the son of grid engine or slurm, using qsub or sbatch

    :param cmd: list
    :param out: str
    :param mo: list
    :param t: float
    :param rmem: int
    :param mem: int
    :param hold: list
    :param jid: str
    :param tr: int
    :param evolgen: bool
    :param node: str
    :param array: list
    :param scheduler: str
    :return:
    """

    sched_opts = {'SGE', 'SLURM'}
    if scheduler not in sched_opts:
        raise ValueError('Only SGE and SLURM schedulers are supported at present!')

    if scheduler == 'SGE':
        script_data = q_script(cmd, out, mo=mo, t=t, rmem=rmem, mem=mem, hold=hold,
                               jid=jid, tr=tr, evolgen=evolgen, node=node, array=array)
        sub_cmd = 'qsub '
    else:
        script_data = s_script(cmd, out, mo=mo, t=t, rmem=rmem, mem=mem, hold=hold,
                               jid=jid, tr=tr, evolgen=evolgen, node=node, array=array)
        sub_cmd = 'sbatch '

    script = script_data[0]
    output_name = script_data[1]

    # output shell script
    output = open(output_name, 'w')
    output.write(script)
    output.close()

    # submit script
    subprocess.call(sub_cmd + output_name, shell=True)
