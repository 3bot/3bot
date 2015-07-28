import zmq
from copy import deepcopy
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.utils import timezone
from threebot.utils import render_template, order_workflow_tasks, importCode
from threebot.botconnection import BotConnection
from threebot.models import WorkflowLog
import threebot_crypto
from background_task import background

import logging

logger = logging.getLogger('3bot')


FLAGS = 0


@background(schedule=1)
def run_workflow(workflow_log_id):
    """
    expects an empty workflow_log,
    performes its tasks on the given worker(s) and
    returns updated workflow_log
    """
    outputs = {}
    protocol = "tcp"

    workflow_log = WorkflowLog.objects.get(id=workflow_log_id)
    worker = workflow_log.performed_on

    WORKER_ENDPOINT = "%s://%s:%s" % (protocol, worker.ip, str(worker.port))
    WORKER_SECRET_KEY = worker.secret_key

    conn = BotConnection(WORKER_ENDPOINT, WORKER_SECRET_KEY)
    conn.connect()

    # Make a JSON
    request_header = {'workflow_log_id': workflow_log.id,
                      'workflow': slugify(workflow_log.workflow.title),
                      'workflow_log_time': workflow_log.date_created.strftime('%Y%m%d-%H%M%S'),
                      'script': {},
                      'hooks': {},  # see doc/HOOKS.md
                      }

    # hooks for this workflow
    if workflow_log.workflow.pre_task:
        request_header['hooks']['pre_task'] = workflow_log.workflow.pre_task

    if workflow_log.workflow.post_task:
        request_header['hooks']['post_task'] = workflow_log.workflow.post_task

    ordered_workflows = order_workflow_tasks(workflow_log.workflow)

    workflow_log.date_started = timezone.now()
    for idx, workflow_task in enumerate(ordered_workflows):
        template = render_template(workflow_log, workflow_task)

        if workflow_task.task.is_builtin:
            m = importCode(template, "test")
            output = {}
            output['stdout'] = str(m.run())
            output['exit_code'] = workflow_log.SUCCESS
        else:
            request = request_header
            request['script']['id'] = idx
            request['script']['body'] = template

            output = send_script(request, conn)

        outputs['%i_%s' % (workflow_task.id, workflow_task.task.title)] = output

        # loop over all next wf_tasks and add this scripts output to inputs
        current = workflow_task
        while current.next_workflow_task:
            current = current.next_workflow_task

            # deepcopy dict to prevent runtime error
            inp = deepcopy(workflow_log.inputs)
            # loop key, value pairs and look if this output needs to be set as input
            for key, value in inp[str(current.id)]['string'].iteritems():
                if value == 'output_%s' % str(workflow_task.id):
                    workflow_log.inputs[str(current.id)]['string'][key] = output['stdout']

        if 'exit_code' not in output or output['exit_code'] is not workflow_log.SUCCESS:
            workflow_log.exit_code = workflow_log.ERROR
            workflow_log.save()
            break
        else:
            workflow_log.exit_code = workflow_log.SUCCESS

    conn.close()

    workflow_log.date_finished = timezone.now()
    workflow_log.outputs = outputs
    workflow_log.save()

    # Notify user in case of failure
    if workflow_log.exit_code == workflow_log.ERROR:
        subject = "[3BOT] Workflow '%s' has failed" % (workflow_log.workflow.title)
        message = "Your workflow %s%s has failed.\n -- 3bot" % (Site.objects.get_current(), workflow_log.get_absolute_url())
        workflow_log.performed_by.email_user(subject, message)


def send_script(request, conn, REQUEST_TIMEOUT=-1, REQUEST_RETRIES=1):
    request = threebot_crypto.encrypt(request, secret_key=conn.secret_key)
    retries_left = REQUEST_RETRIES
    response = {}

    while retries_left:
        # conn.client.send_json(request)
        conn.client.send(request, flags=FLAGS)

        expect_reply = True
        while expect_reply:
            socks = dict(conn.poll.poll(REQUEST_TIMEOUT))

            if socks.get(conn.client) == zmq.POLLIN:
                # response = conn.client.recv_json()
                response = conn.client.recv(FLAGS)
                response = threebot_crypto.decrypt(response, secret_key=conn.secret_key)
                if not response:
                    retries_left = 0
                    break
                else:
                    retries_left = 0
                    break

            else:
                retries_left -= 1
                conn.reconnect()
                # conn.client.send_json(request)
                conn.client.send(request, flags=FLAGS)

                if retries_left == 0:
                    retries_left = 0
                    conn.reconnect()
                    break
    return response
