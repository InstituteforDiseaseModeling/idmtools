from flask_restful import abort


def validate_tags(tags):
    # validate the tags
    if tags is not None:
        for i in range(len(tags)):
            if ',' in tags[i]:
                tags[i] = tags[i].split(',')

            if type(tags[i]) not in [list, tuple] or len(tags[i]) > 2:
                abort(400, message='Tags needs to be in the format "name,value"')
