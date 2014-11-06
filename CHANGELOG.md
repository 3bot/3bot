# Changelog


### 0.0.16 - 31.10.2014

*   Added @python_2_unicode_compatible for Python 2 - Python 3 compatibility
*   Fix wrong install url in worker-manual
*   Set correct urlname for workflow reorder view
*   Improved admin sites
*   better __str__ method for WorkflowLog Model
*   Fixied typo wokflow -> workflow
*   smart include hook urls

### 0.0.15 - 29.10.2014

*    CSS indicators for pending workflows
*    Fix for wrong redirect after creating a new Workflow


### 0.0.14 - 23.10.2014

*    3bot now depends on [django-background-task](https://github.com/lilspikey/django-background-task) for asynchronous workflow performance. Visit the Repository to see how to set up django-background-task.
*    The Timeout to perform a Task on a worker was increased to 3 minutes.
*    Parameter and Parameter lists are now editable in a FormSet
*    Workers can be muted to prevent accessibility checks and improve performance.
*    Parameter and Parameter lists are now editable in a FormSet
*    UI changes in the detailview for Workflows, Tasks and Workers
