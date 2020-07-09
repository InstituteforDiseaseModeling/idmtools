import os
import covasim as cv

# Script that configures and runs a Covasim model simulation

if __name__ == '__main__':
    # Get the current directory of the input file so that outputs get written to the same directory
    cwd = os.path.dirname(__file__)

    # Set the output directory path
    outputs = "outputs"

    # Configure the sim -- can also just use a normal dictionary
    pars = dict(
        pop_size     = 10000,    # Population size
        pop_infected = 10,       # Number of initial infections
        n_days       = 120,      # Number of days to simulate
        rand_seed    = 1,        # Random seed
        pop_type     = 'hybrid'  # Population to use -- "hybrid" is random with household, school,and work structure
    )

    # Add an intervention
    pars['interventions'] = cv.change_beta(days=45, changes=0.5)

    # Make, run, and plot the sim and get results as JSON and XSLX spreadsheet
    sim = cv.Sim(pars=pars)
    sim.initialize()
    sim.run(
        do_plot=True,                               # Enable plotting
        do_show=False,                              # Do not attempt to open/view the plot
        do_save=True,                               # Save the plot as a file
        fig_path=os.path.join(outputs,"plot.png")   # Set the plot image output path
    )
    # Save the results as JSON and Excel spreadsheet
    sim.to_json(filename=os.path.join(outputs, "results.json"))
    sim.to_excel(filename=os.path.join(outputs, "results.xlsx"))
