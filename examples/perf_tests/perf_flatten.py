from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform


def comps_flatten_demo():
    platform = Platform('CALCULON')

    # Monique Case
    suite_id = "399600fe-ca4a-ef11-aa16-b88303911bc1"
    exp_id = "78d76b24-cb4a-ef11-aa16-b88303911bc1"  # 6 simulations

    # Kurt case
    # suite_id = "03015682-6b2c-f011-aa20-b88303911bc1"
    exp_id = "ba7f8051-77ed-ef11-aa1c-b88303911bc1"  # Kfrey: 1400

    # EXPERIMENT CASE
    exp = platform.get_item(exp_id, ItemType.EXPERIMENT, raw=False)  # Test two cases: True/False
    exp.platform = platform  # Double check if need for raw=True case
    print("exp:", exp)
    print(exp.tags)  # key, value are single-quoted
    # print(exp.get_directory())

    sims = platform.flatten_item(exp, raw=True)
    print("sims:", len(sims), type(sims[0]))

    # Compare with this case
    # sims = platform.flatten_item(exp, raw=False)
    # print("sims:", len(sims), type(sims[0]))


def profiler_demo():
    # 1: cProfile
    import cProfile
    # cProfile.run("exp_demo()")   # print out
    # cProfile.Profile.dump_stats("simple_experiment.pstat")
    # exit()

    # with cProfile.Profile() as pr:
    #     comps_flatten_demo()
    # pr.dump_stats("simple_experiment_2.pstat")
    # #pr.print_stats()
    # exit()

    # 2: pyinstrument
    from pyinstrument import Profiler
    profiler = Profiler()
    with profiler:
        comps_flatten_demo()
    profiler.write_html("comps_flatten_profiler.html")
    #profiler.print()


if __name__ == '__main__':
    # comps_flatten_demo()
    # exit()

    profiler_demo()
    exit()