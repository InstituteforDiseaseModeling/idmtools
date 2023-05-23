"""
There are 2 ways to run this example.
- Option1: run "python3 example1.py": This will trigger a Slurm job to run example1.py script on head node.
- Option2, run "sbatch sbatch_for_example1.sh". This will trigger a Slurm job to run example1.py script on computation
  node.
"""

def add(a, b):
    return a + b

result = add(2, 3)
print(result)