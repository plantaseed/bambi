import time
from cli_std_lib import Bambi


def create_test_bambi():
    bambi = Bambi()
    bambi.name = "pytest"
    return bambi


def check_workspace_existance(bambi):
    workspaces = bambi.list_all_workspaces()
    name = bambi.namespace + "-" + bambi.name
    for workspace in workspaces:
        if name in workspace:
            return True

    return False


def test_init_params():
    """ Test so that bambi is initialized with params. """

    bambi = Bambi()
    assert bambi.name
    assert bambi.namespace


def test_create_workspace():
    """ Test that a new workspace can be created. """

    bambi = create_test_bambi()
    bambi.create_workspace(bambi.name)
    success = check_workspace_existance(bambi)

    assert success


def test_get_address():
    """ Test that the address to the workspace can be fetched. """

    # Wait for workspace to be initialized
    time.sleep(40)
    bambi = create_test_bambi()
    address = bambi.get_address_to_workspace()
    assert address


def test_get_password():
    bambi = create_test_bambi()
    password = bambi.get_password_to_workspace()
    assert password


def test_delete_workspace():
    bambi = create_test_bambi()
    bambi.delete_workspace()
    success = check_workspace_existance(bambi)
    assert success
