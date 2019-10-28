#!/usr/bin/env Rscript
suppressPackageStartupMessages(library("argparse"))
## Load deSolve package
library(deSolve)
library(jsonlite)

## Create an SIR function
sir <- function(time, state, parameters) {

  with(as.list(c(state, parameters)), {

    dS <- -beta * S * I
    dI <-  beta * S * I - gamma * I
    dR <-                 gamma * I

    return(list(c(dS, dI, dR)))
  })
}

parser <- ArgumentParser()
parser$add_argument("--susceptible", default=1-1e-6, type="double",
    help="Initial proportion of susceptibles. Should be between 0 and 1 [default %(default)s]")
parser$add_argument("--infected", default=1e-6, type="double",
    help="Initial proportion number of infected. Should be between 0 and 1 [default %(default)s]")
parser$add_argument("--recovered", default=1e-6, type="double",
    help="Initial proportion number of recovered. Should be between 0 and 1 [default %(default)s]")
parser$add_argument("--beta", default=1.4247, type="double",
    help="beta value [default %(default)s]")
parser$add_argument("--gamma", default=0.14286, type="double",
    help="gamma value [default %(default)s]")
parser$add_argument("--timeframe", default=70, type="integer",
    help="Timeframe of simulation [default %(default)s]")
parser$add_argument("--config-file", default=NULL, type="character")
# get command line options, if help option encountered print help and exit,
# otherwise if options not found on command line then set defaults,
args <- parser$parse_args()

if (!is.null(args$config_file) && length(args$config_file) > 0) {
    content <- fromJSON(readLines(args$config_file, warn = FALSE))
    opts <- c('susceptible','infected','recovered','beta','gamma', 'timeframe')
    print(content)
    for(opt in opts) {
        # only load the configuration options that are defined
        if (any(names(content) == opt)) {
            args[opt] <- content[opt]
        }
    }

}

print("Config:")
print(args)
### Set parameters
## Proportion in each compartment: Susceptible 0.999999, Infected 0.000001, Recovered 0
init       <- c(S = args$susceptible, I = args$infected, R = args$infected)
## beta: infection parameter; gamma: recovery parameter
parameters <- c(beta = args$beta, gamma = args$gamma)
## Time frame
times      <- seq(0, args$timeframe, by = 1)

## Solve using ode (General Solver for Ordinary Differential Equations)
out <- ode(y = init, times = times, func = sir, parms = parameters)
## change to data frame
out <- as.data.frame(out)
## Delete time variable
out$time <- NULL
write.csv(out, file="output.csv")