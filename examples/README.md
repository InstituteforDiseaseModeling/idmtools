# Examples

These are examples of idmtools work. It is best to download these examples through the `idmtools examples` command. If you do checkout the repo to run examples **do not** run the make setup-dev to install development environment. You should use normal install method through pip

## For Dev/Test

When developers or test want to run examples, you should use staging environments. The `bootstrap.py`/`setup-dev` step will write an `idmtools.ini` file that redirects any calls from production environments to staging. These means some examples could need alteration to effectively run in staging. For example, some examples have experiment ids that may not exist in staging, so you will have to update those.