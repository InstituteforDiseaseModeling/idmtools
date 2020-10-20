for i in range(100):
    with open(f"{i}.out", 'w') as out:
        out.write(str(i))
