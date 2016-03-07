import json
import sys

from micall.monitor import qai_helper
from micall import settings
from collections import Counter


def check_key_positions(projects, warning_file):
    """ Complain if a coordinate region has two sets of key positions in the
    same project.

    @param projects: a dictionary of project definitions
    @param warning_file: an open file to write any warnings in
    """
    key_warning = ("WARNING: project {} has multiple sets of key positions for "
                   "coordinate region {}.\n")
    seed_warning = "WARNING: project {} has duplicate seed and coordinate: {}, {}\n"
    warnings = []
    for project_name, project in projects.iteritems():
        key_position_coordinates = Counter()
        seed_coordinate_pairs = Counter()
        for region in project['regions']:
            coordinate_name = region['coordinate_region']
            if region['key_positions']:
                key_position_coordinates[coordinate_name] += 1
            for seed_name in region['seed_region_names']:
                seed_coordinate_pairs[(seed_name, coordinate_name)] += 1
        sorted_counts = key_position_coordinates.most_common()
        for coordinate_name, count in sorted_counts:
            if count > 1:
                warnings.append(key_warning.format(project_name,
                                                   coordinate_name))
            else:
                break
        sorted_counts = seed_coordinate_pairs.most_common()
        for (seed_name, coordinate_name), count in sorted_counts:
            if count > 1:
                warnings.append(seed_warning.format(project_name,
                                                    seed_name,
                                                    coordinate_name))
            else:
                break
    for warning in sorted(warnings):
        warning_file.write(warning)


def dump_json(json_object, filename):
    with open(filename, "w") as f:
        json.dump(json_object,
                  f,
                  sort_keys=True,
                  indent=2,
                  separators=(',', ': '))
        f.write('\n')


def main():
    dump = {}
    with qai_helper.Session() as session:
        session.login(settings.qai_project_path,
                      settings.qai_project_user,
                      settings.qai_project_password)

        dump['regions'] = session.get_json("/lab_miseq_regions?mode=dump",
                                           retries=0)
        dump['projects'] = session.get_json(
            "/lab_miseq_projects?mode=dump&pipeline=" +
            settings.pipeline_version,
            retries=0)
        for project in dump['projects'].itervalues():
            project['regions'].sort()
        errors = dump['projects'].get('errors')
        if errors:
            raise StandardError('\n'.join(errors))
        check_key_positions(dump['projects'], sys.stdout)

    dump_json(dump, "../projects.json")

    for project in dump['projects'].itervalues():
        for region in project['regions']:
            name = region['coordinate_region']
            seq = ''.join(dump['regions'][name]['reference'])
            region['coordinate_region_length'] = len(seq)
    del dump['regions']
    dump_json(dump, "../project_scoring.json")

    print "Done."

if __name__ == "__main__":
    main()
