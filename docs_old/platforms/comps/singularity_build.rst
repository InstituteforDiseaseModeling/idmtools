Singularity build
=================

The |COMPS_s| platform supports building singularity images remotely with 
:py:class:`~idmtools_platform_comps.utils.singularity_build.SingularityBuildWorkItem`.

The workitem supports a few different scenarios for creating Singularity images:

Building from definition files
------------------------------

You can build from a Singularity definition file. See `Definition Document <https://sylabs.io/guides/3.5/user-guide/definition_files.html>`_.

To build using a definition file, you need to set the `definition_file` parameter to
the path of a definition file. You can specify inputs to be consumed in the build by
adding them to the `assets` or `transient_assets` fields. It is generally best to
use the `assets` since they take advantage of caching. Remember that the resulting path
of any files added to `assets` will need to be references with `Assets/filename`
in your definition file.

Building from definition string
-------------------------------

You can build from a definition that is in script(as a string) using
the `definition_content`. Be sure the `is_template` parameter is false.

Building from definition template
---------------------------------

The :py:class:`~idmtools_platform_comps.utils.singularity_build.SingularityBuildWorkItem`
can also build using jinja templates. The template should produce a singularity definition
file when rendered.

To use a template, specify the template using `definition_content` and also by
setting `is_template` to `True`. You can also use the `template_args` to define
items to be passed to the template when rendered. In addition to those items, the
current executing environment variables are accessible as `env` and the workitem is
accessible as `sbi`.

For details on `Jinja's <https://jinja.palletsprojects.com/>`_ syntax
see https://jinja.palletsprojects.com/