import ast
import dataclasses
import typing
from logging import getLogger

user_logger = getLogger('user')


def get_dataclass_common_fields(src, dest, exclude_none: bool = True) -> typing.Dict:
    """
    Extracts fields from a dataclass source object who are also defined on destination object. Useful for situations
    like nested configurations of data class options

    Args:
        src: Source dataclass object
        dest: Dest dataclass object
        exclude_none: When true, values of None will be excluded

    Returns:

    """
    dest_fields = [f.name for f in dataclasses.fields(dest)]
    src_fields = dataclasses.fields(src)
    result = dict()
    for field in src_fields:
        if field.name in dest_fields and (not exclude_none or (exclude_none and getattr(src, field.name, None) is not None)):
            result[field.name] = getattr(src, field.name)
    return result


def as_dict(src, exclude: typing.List[str] = None, exclude_private_fields: bool = True):
    """
    Converts a dataclass to a dict while also obeys rules for exclusion
    Args:
        src:
        exclude: List of fields to exclude
        exclude_private_fields: Should fields that star

    Returns:

    """
    if exclude is None:
        exclude = []

    result = dict()
    # get metadata
    metadata = dataclasses.fields(src.__class__)
    for field in metadata:
        field_metadata = field.metadata
        if (not exclude_private_fields or field.name[0] != '_') and \
                ('exclude_from_metadata' not in field_metadata or not field_metadata['exclude_from_metadata']) and \
                field.name not in exclude:
            result[field.name] = getattr(src, field.name)
    return result


def validate_user_inputs_against_dataclass(field_type, field_value):
    fs_kwargs = set(field_type.keys()).intersection(set(field_value.keys()))
    for fn in fs_kwargs:
        ft = field_type[fn]
        try:
            if ft in (int, float, str):
                field_value[fn] = ft(field_value[fn]) if field_value[fn] is not None else field_value[fn]
            elif ft is bool:
                field_value[fn] = ast.literal_eval(field_value[fn]) if isinstance(field_value[fn], str) else \
                    field_value[fn]
        except ValueError as e:
            user_logger.error(f"The field {fn} requires a value of type {ft.__name__}. You provided <{field_value[fn]}>")
            raise e
    return fs_kwargs


def get_default_tags() -> typing.Dict[str, str]:
    """
    Get common default tags. Currently this is the version of idmtools
    Returns:

    """
    from idmtools import __version__
    return dict(idmtools=__version__)
