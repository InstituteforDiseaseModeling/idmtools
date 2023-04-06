"""
There are 2 ways to run this example.
1. Option1: run "python3 example.py". This will run python script on head node
2. Option2, run "sbatch sbatch_for_example1.sh". This will trigger a slurm job for 'example1.py' script in slurm cluster.
"""

def add(a, b):
    return a + b

result = add(2, 3)
print(result)