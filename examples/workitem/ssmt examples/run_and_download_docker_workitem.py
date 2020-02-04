import time, os, shutil, sys, uuid

from COMPS import Client
from COMPS.Data import WorkItem, WorkItemFile, QueryCriteria
from COMPS.Data.WorkItem import WorkItemState, WorkerOrPluginKey, RelationType

compshost = 'https://comps2.idmod.org'
compsenv = 'Bayesian'

wi_name = 'Hello WoRld - SSMT'

wi_tags = {
        'SSMT': None,
        'WorkItem type': 'DockerWorker'
}

workorder_string = \
"""{
    "WorkItem_Type" : "DockerWorker",
    "Execution": {
        "ImageName": "ubuntu18.04_r3.5.0",
        "Command": "/usr/bin/Rscript HelloWoRld.R"
    }
}"""

additional_files = [
                       # filename   strip_carriage_returns
                       # ('run.sh',     1),
                       ('HelloWoRld.R'),
                       ('data.csv')
                   ]

out_filenames = [ "new_data.csv" ]

###############################################################

Client.login(compshost)

if len(sys.argv) == 2:
    try:
        wi_id = uuid.UUID(sys.argv[1])
    except ValueError:
        print('')
        print('Usage:')
        print('\t{0} [workitemId]'.format(sys.argv[0]))
        print('')
        print('If no \'workitemId\' is specified, the script will create a new workitem, poll')
        print('  until the workitem is complete, and then download output files.')
        print('If a \'workitemId\' is specified, the script will poll until the workitem is')
        print('  complete and then download output files.')
        exit()

    # restart polling for existing/running WorkItem
    wi = WorkItem.get(wi_id)
else:
    # Create a work-item (locally)
    wi = WorkItem(wi_name, WorkerOrPluginKey('DockerWorker', '1.0.0.0_RELEASE'), compsenv)

    wi.set_tags(wi_tags)

    wi.add_work_order(data=bytes(workorder_string, 'utf-8'))


    # add the linked files
    for tup in additional_files:
        if tup is tuple and len(tup) == 2 and tup[1] == 1:   # strip carriage returns
            with open(os.path.join('files', tup[0]), 'rb') as f:
                wi.add_file(WorkItemFile(tup[0], 'input', ''), data=f.read().replace('\r\n', '\n'))
        else:
            wi.add_file(WorkItemFile(tup, 'input', ''), file_path=os.path.join('files', tup))

    # Save the work-item to the server
    wi.save()
    wi.refresh()

    print('Created work-item {0}'.format(wi.id))
    print('Commissioning...')

    wi.commission()

    print('Commissioned')
    print('Refreshing WorkItem state until it completes')

print('State -> {}'.format(wi.state.name))

# wait in a loop here until the WorkItem finishes
while wi.state not in [WorkItemState.Succeeded, WorkItemState.Failed, WorkItemState.Canceled]:
    time.sleep(5)
    wi.refresh()
    print('State -> {}'.format(wi.state.name))

if wi.state is not WorkItemState.Succeeded:
    print('WorkItem didn\'t succeed; skipping output file retrieval')
    exit(-1)

print('Retrieving output')

foo = wi.retrieve_output_files(out_filenames)

for ofi in zip( out_filenames, foo ):
    print("\tWriting file: " + ofi[0])

    with open(ofi[0], 'wb') as outfile:
        outfile.write(ofi[1])
