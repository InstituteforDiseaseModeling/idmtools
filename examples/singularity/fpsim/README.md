<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Overview](#overview)
  - [Getting Started](#getting-started)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

Overview
========

This directory contains an example using containers and the fpsim image.


Getting Started
---------------

1. It is recommended you create a virtualenv
2. In ..\ubuntu-20-04, run create_ubuntu_sif.py.  If the image needs to be created, check comps2's WorkItem browser.
3. In fpsim, run create_fpsim_sif.py.  This should automatically detect the ubuntu.id file in the ubuntu folder and build the singularity image.
4. Next, run run_fpsim_sample.py and check COMPS to see if this worked.
