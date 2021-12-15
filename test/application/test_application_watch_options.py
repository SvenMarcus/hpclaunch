from unittest.mock import Mock, call
from hpcrocket.ui import UI

from test.application.launchoptions import main_connection, proxy_connection, watch_options
from test.slurm_assertions import assert_job_polled
from test.slurmoutput import DEFAULT_JOB_ID, completed_slurm_job, running_slurm_job
from test.testdoubles.executor import FailedSlurmJobCommandStub, LongRunningSlurmJobExecutorSpy, SlurmJobExecutorSpy
from test.testdoubles.filesystem import DummyFilesystemFactory

from hpcrocket.core.application import Application
from hpcrocket.core.launchoptions import WatchOptions


def make_sut(executor, ui=None):
    return Application(executor, DummyFilesystemFactory(), ui or Mock())


def test__given_watch_options__when_running__should_poll_job_until_done():
    executor = LongRunningSlurmJobExecutorSpy()
    sut = make_sut(executor)

    sut.run(watch_options())

    assert_job_polled(executor, command_index=0)
    assert_job_polled(executor, command_index=1)
    assert_job_polled(executor, command_index=2)


def test__given_watch_options__when_running__should_update_ui_with_job_status():
    executor = LongRunningSlurmJobExecutorSpy()

    ui = Mock(spec=UI)
    sut = make_sut(executor, ui)

    sut.run(watch_options())

    assert ui.update.mock_calls[0] == call(running_slurm_job())
    assert ui.update.mock_calls[-1] == call(completed_slurm_job())


def test__given_watch_options__when_running_with_successful_job__should_exit_with_0():
    executor = SlurmJobExecutorSpy()
    sut = make_sut(executor)

    actual = sut.run(watch_options())

    assert actual == 0


def test__given_watch_options__when_running_with_failing_job__should_exit_with_1():
    executor = SlurmJobExecutorSpy(sacct_cmd=FailedSlurmJobCommandStub())
    sut = make_sut(executor)

    actual = sut.run(watch_options())

    assert actual == 1
