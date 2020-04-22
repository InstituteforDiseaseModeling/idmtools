# TODO:
# ini file writing (def write): there are required blocks (logging) that are not actual platforms. How to write these to ini files?
# Have all the non-user-facing fields on the platforms been excluded?
# incorporate into cli interface of idmtools

import argparse
import dataclasses
import json
import os
import re
from configparser import ConfigParser

from idmtools.core.platform_factory import Platform
from idmtools.registry.platform_specification import PlatformPlugins
from idmtools.utils.entities import validate_user_inputs_against_dataclass
from idmtools.utils.file import get_idmtools_root

# TODO:
# SUBCOMMANDS
# working as of initial testing
# set
# show
# add_section
# sections
# platforms
# reset
# wizard

# to test/check:
# write

SUBCOMMANDS = ['platforms', 'sections', 'show', 'set', 'reset', 'write', 'add_section', 'wizard']
USER_OVERRIDES_FILE = os.path.join(str(get_idmtools_root()), 'user_overrides.json')
HIDDEN_FIELD_REGEX = re.compile('^_.+$')
FIELD_BLACKLIST = ['platform_type_map', 'supported_types', 'plugin_key', 'docker_image']  # TODO complete?


class Defaults:

    @staticmethod
    def available_platforms():
        return PlatformPlugins().get_plugin_map().keys()

    @staticmethod
    def available_sections():
        platforms = [p.lower() for p in Defaults.available_platforms()]
        user_override_sections = Defaults.load_user_overrides().keys()
        all_sections = list(set(platforms + list(user_override_sections)))
        return all_sections

    @staticmethod
    def load_user_overrides(section_name=None):
        user_overrides = {}
        if os.path.exists(USER_OVERRIDES_FILE):
            with open(USER_OVERRIDES_FILE, 'r') as f:
                file_data = json.load(f)
                if section_name is None:
                    user_overrides = file_data
                else:
                    if section_name in file_data:
                        user_overrides = {section_name: file_data[section_name]}

        return user_overrides

    @staticmethod
    def write_user_overrides(user_overrides):
        with open(USER_OVERRIDES_FILE, 'w') as f:
            json.dump(user_overrides, f)
        print('Section defaults updated.')


    @staticmethod
    def apply_user_overrides(factory_defaults, user_overrides):
        user_overrides.pop('type', None)  # non-built-in sections will have 'type',but it is NOT a settable option
        options = factory_defaults
        mapping = {opt.name: opt for opt in factory_defaults.keys()}
        for option_name, value in user_overrides.items():
            options[mapping[option_name]] = value
        return options

    @staticmethod
    def get_options_for_section(section_name):
        if section_name not in Defaults.available_sections():
            raise Exception(f'Unknown section: {section_name}')
        user_overrides = Defaults.load_user_overrides(section_name=section_name)

        # 'type' in the overrides indicates a user-defined section. Otherwise, an in-built section for a platform.
        platform_name = user_overrides[section_name]['type'] if 'type' in user_overrides[section_name] else section_name.upper()
        factory_defaults = Defaults.get_factory_defaults_for_platform(platform_name=platform_name)

        options = Defaults.apply_user_overrides(factory_defaults, user_overrides[section_name])
        return options

    @staticmethod
    def _set_option_for_section(section_name, platform_options, option_name, value,
                                user_overrides):
        """
        Modify the specified platform option in the user_overrides dict with the supplied value.
        Args:
            section_name: platform name, string
            platform_options: dict of {dataclass field: value}
            option_name: the name of the option to change, string
            value: the new default value of the specified option (type depends on option)
            user_overrides: dict of existing user default overrides to put new name/value in

        Returns:
            Nothing
        """
        platform_option = [option for option in platform_options if option.name == option_name]
        if len(platform_option) != 1:
            raise Exception(f'No such option {option_name} on platform: {section_name}')
        platform_option = platform_option[0]
        # validate_type(platform_option, value)  # expected to return exception if NOT valid type for this option
        value_dict = {platform_option.name: value}  # value here will be updated after proper cleaning
        validate_user_inputs_against_dataclass({platform_option.name: platform_option.type}, value_dict)
        if section_name not in user_overrides:
            user_overrides[section_name] = {}
        user_overrides[section_name][option_name] = value_dict[platform_option.name]
        return user_overrides

    @staticmethod
    def set_options_for_section(section_name, new_user_overrides):
        if section_name not in Defaults.available_sections():
            raise Exception(f'Unknown section: {section_name}')
        existing_user_overrides = Defaults.load_user_overrides()

        platform_name = section_name
        if section_name in existing_user_overrides.keys():
            if 'type' in existing_user_overrides[section_name]:
                platform_name = existing_user_overrides[section_name]['type']

        platform_options = Defaults.get_factory_defaults_for_platform(platform_name=platform_name)
        exceptions = list()
        for option_name, value in new_user_overrides.items():
            try:
                user_overrides = Defaults._set_option_for_section(section_name, platform_options, option_name, value,
                                                                  existing_user_overrides)
            except Exception as e:
                exceptions.append(e)
        if len(exceptions) == 0:
            Defaults.write_user_overrides(user_overrides)
        else:
            print(exceptions)
        return exceptions

    @staticmethod
    def get_factory_defaults_for_platform(platform_name):
        """

        Args:
            platform_name:

        Returns:
            a dict of {dataclass field object keys: field value}
        """
        platform = Platform(platform_name)
        fields = dataclasses.fields(platform)
        options = {field: getattr(platform, field.name) for field in fields}

        # filter out non-user-facing fields
        options = {opt: value for opt, value in options.items() if opt.name not in FIELD_BLACKLIST}
        options = {opt: value for opt, value in options.items() if not HIDDEN_FIELD_REGEX.match(opt.name)}
        return options

    @staticmethod
    def show_overrides_for_section(section_name):
        options = Defaults.get_options_for_section(section_name=section_name)
        print('-'*80)
        print(f'{section_name} DEFAULT SETTINGS')
        print('-'*80)
        for option, value in options.items():
            print(f'{option.name}: {value}')
        print('-'*80)

    @staticmethod
    def write_configuration_file(output_path):
        cp = ConfigParser()
        # user_overrides = load_user_overrides()
        for section_name in Defaults.available_sections():
            options = Defaults.get_options_for_section(section_name=section_name)
            cp.add_section(section=section_name)
            for option, value in options.items():
                cp.set(section=section_name, option=option.name, value=str(value))

        with open(output_path, 'w') as f:
            cp.write(f)

    #
    # top-level subcommands
    #

    @staticmethod
    def sections(args):
        available = sorted(Defaults.available_sections())
        print('-'*80)
        print('Available sections:')
        print('-'*80)
        print('\n'.join(available))
        print('-'*80)

    @staticmethod
    def platforms(args):
        available = sorted(Defaults.available_platforms())
        print('-'*80)
        print('Available platforms:')
        print('-'*80)
        print('\n'.join(available))
        print('-'*80)

    @staticmethod
    def show(args):
        Defaults.show_overrides_for_section(section_name=args.section)

    @staticmethod
    def set(args):
        # handle the multi-option input of 'set' subcommand
        option_values = {}
        for option_value in args.option_value:
            option, value = option_value.strip().split('=')
            option_values[option] = value
        Defaults.set_options_for_section(section_name=args.section, new_user_overrides=option_values)

    @staticmethod
    def reset(args):
        user_overrides = Defaults.load_user_overrides()
        if args.section not in Defaults.available_sections():
            raise Exception(f'Section {args.section} does not exist. Section not removed.')
        user_overrides.pop(args.section, None)
        Defaults.write_user_overrides(user_overrides)

    @staticmethod
    def write(args):
        destination_path = os.path.join(args.dest_dir, 'idmtools.ini')
        Defaults.write_configuration_file(output_path=destination_path)


    @staticmethod
    def add_section(args):
        overwrite = True if hasattr(args, 'overwrite') and getattr(args, 'overwrite') is True else False
        if not overwrite:
            if args.section in Defaults.available_sections():
                raise Exception(f'Section {args.section} already exists. Section not added.')
        if args.platform not in Defaults.available_platforms():
            raise Exception(f'Platform of type {args.platform} does not exist. Section not added.')
        user_overrides = Defaults.load_user_overrides()

        # add 'type' only if the section is not the built-in section for the platform; condition needed for wizard calls
        if args.section != args.platform.lower():
            user_overrides[args.section] = {'type': args.platform}
        Defaults.write_user_overrides(user_overrides=user_overrides)

    @staticmethod
    def wizard(args):
        args.overwrite = True
        Defaults.add_section(args)
        section_options = Defaults.get_options_for_section(section_name=args.section)

        print('-'*80)
        print(f'Section configuration wizard for section: {args.section}')
        print('Press Enter with no input to keep the current value')
        print('New value: BLANK indicates a blank value for an option')
        print('-'*80)
        new_section_options = {}
        for option, current_value in section_options.items():
            new_value = input(f'Option: {option.name} Current value: {current_value} New value: ')
            if new_value.upper() == 'BLANK':
                new_section_options[option.name] = ''
            elif len(new_value) == 0:
                pass
            else:
                new_section_options[option.name] = new_value
        Defaults.set_options_for_section(section_name=args.section, new_user_overrides=new_section_options)


#
# arg parsers
#


def parse_args_add_section(subparsers, subcommand):
    types = ', '.join(Defaults.available_platforms())
    subparser = subparsers.add_parser(subcommand.__name__, help='Add a new default configuration section.')
    subparser.add_argument('section', type=str, help='Name of new section.')
    subparser.add_argument('platform', type=str, help=f'Name of section platform type [{types}].')
    subparser.set_defaults(func=subcommand)


def parse_args_platforms(subparsers, subcommand):
    subparser = subparsers.add_parser(subcommand.__name__, help='List available platforms for section type.')
    subparser.set_defaults(func=subcommand)


def parse_args_sections(subparsers, subcommand):
    subparser = subparsers.add_parser(subcommand.__name__, help='List available sections for option setting.')
    subparser.set_defaults(func=subcommand)


def parse_args_show(subparsers, subcommand):
    subparser = subparsers.add_parser(subcommand.__name__, help='List available section options.')
    subparser.add_argument('section', type=str, help='Section to list options for.')
    subparser.set_defaults(func=subcommand)


def parse_args_set(subparsers, subcommand):
    subparser = subparsers.add_parser(subcommand.__name__, help='Set default options for an idmtools section.')
    subparser.add_argument('section', type=str, help='Section to set options for.')
    subparser.add_argument('option_value', type=str, nargs='+', help='Option(s) to set, <option>=<value> format. '
                                                                     'Separate options by spaces.')
    subparser.set_defaults(func=subcommand)


def parse_args_reset(subparsers, subcommand):
    subparser = subparsers.add_parser(subcommand.__name__, help='Reset all section options to factory defaults.')
    subparser.add_argument('section', type=str, help='Section to reset options for.')
    subparser.set_defaults(func=subcommand)


def parse_args_write(subparsers, subcommand):
    subparser = subparsers.add_parser(subcommand.__name__, help='Write a new idmtools configuration file.')
    subparser.add_argument('-d', '--dir', dest='dest_dir', type=str, default=os.getcwd(),
                           help='Write a configuration file to this directory.')
    subparser.set_defaults(func=subcommand)


def parse_args_wizard(subparsers, subcommand):
    types = ', '.join(Defaults.available_platforms())
    subparser = subparsers.add_parser(subcommand.__name__, help='Add or edit a configuration section.')
    subparser.add_argument('section', type=str, help='Name of new section.')
    subparser.add_argument('platform', type=str, help=f'Name of section platform type [{types}].')
    subparser.set_defaults(func=subcommand)


def parse_args(program_name):
    parser = argparse.ArgumentParser(prog=program_name)
    subparsers = parser.add_subparsers()

    # call the per-subcommand subparser setup methods
    for subcommand in SUBCOMMANDS:
        subcommand = subcommand.lower().replace('-', '_')
        parser_method_name = 'parse_args_%s' % subcommand
        globals()[parser_method_name](subparsers, getattr(Defaults, subcommand))
    args = parser.parse_args()

    # lowercase section name for all subcommands, if present
    if hasattr(args, 'section'):
        args.section = args.section.strip().lower()

    # uppercase for all platform names
    if hasattr(args, 'platform'):
        args.platform = args.platform.strip().upper()

    return args


if __name__ == '__main__':
    script_args = parse_args(program_name='cfg')
    script_args.func(script_args)
