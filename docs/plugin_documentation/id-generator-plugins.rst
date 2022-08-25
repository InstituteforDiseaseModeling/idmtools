=====================
ID Generation Plugins
=====================

**1. Create a file to host the plugin callback for generator (under idmtools_core/idmtools/plugins). The plugin must have the following format**::

    from idmtools.core.interfaces.ientity import IEntity

    from idmtools.registry.hook_specs import function_hook_impl

    @function_hook_impl

    def idmtools_generate_id(item: IEntity) -> str:
        Args:
            item: Item for which ID is being generated
        Returns:
        return <your id implementation here>


The key things in this file are::

    @function_hook_impl
    def idmtools_generate_id(item: 'IEntity') -> str:

This registers the plugin type with idmtools. By using the name idmtools_generate_id, we know you are defining a callback for ids.
The callback must match the expected signature.


**2. Modify setup.py 'idmtools_hooks' to include the new id generation plugin**::

    entry_points=dict(
        idmtools_hooks=[
            "idmtools_id_generate_<name> = <path to plugin>"
        ]
    ),

The *label* of the id plugin must start with **idmtools_id_generate_**
The letters after **idmtools_id_generate_** will be used to select generator in the config.

**3. Modify .ini config file to specify the desired id generator.**

In the .ini configuration file under the 'COMMON' section, use the 'id_generator' option to specify the desired id plugin.

For example, if you want to use the uuid generation plugin ('idmtools_id_generate_uuid'), in the .ini file, you would set the following::

    [COMMON]
    id_generator = uuid

Similarly, if you want to use the item_sequence plugin ('idmtools_id_generate_item_sequence'), you would specify the following in the .ini file::

    [COMMON]
    id_generator = item_sequence

The item_sequence plugin allows you to use sequential ids for items in your experiment (experiments themselves as well as simulations, etc).
You can customize use of this plugin by defining an 'item_sequence' section in the .ini file and using the variables:

    * *sequence_file*: Json file that is used to store the last-used numbers for item ids. For example, if we have one experiment that was defined with two simulations, this file would keep track of the most recently used ids with the following: {"Simulation": 2, "Experiment": 1}. The default for this value is item_sequences.json, and this file will be created in the user's home directory. Also to note: the sequences start at 0.
    * *id_format_str*: This defines the desired format of the item ids (using the sequential id numbers stored in the sequence_file). In this string, one may access the sequential ids by using 'data[item_name]' (which would resolve to the next id #) as well as the 'item_name' (i.e. 'Simulation', 'Experiment'). The default for this value is '{item_name}{data[item_name]:07d}' (which would yield ids of 'Simulation0000000', 'Simulation0000001', etc).

Configuration format::

    [item_sequence]
    sequence_file = <custom file name>.json
    id_format_str = '<custom string format>'
