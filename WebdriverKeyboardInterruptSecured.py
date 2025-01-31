# Stop the webdriver from closing on keyboard interrupt
# Inspiration from https://stackoverflow.com/a/49323296

import errno
import os
import subprocess
from platform import system
from subprocess import PIPE
from time import sleep
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common import utils
import signal

def preexec_function():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def start(self):
    """
    Starts the Service.
    :Exceptions:
     - WebDriverException : Raised either when it can't start the service
       or when it can't connect to the service
    """
    try:
        cmd = [self.path]
        cmd.extend(self.command_line_args())
        self.process = subprocess.Popen(cmd, env=self.env,
                                        close_fds=system() != 'Windows',
                                        stdout=self.log_file,
                                        stderr=self.log_file,
                                        stdin=PIPE,
                                        preexec_fn=preexec_function if system() != 'Windows' else None,
                                        creationflags = 0 if system() != 'Windows' else subprocess.CREATE_NO_WINDOW)
    except TypeError:
        raise
    except OSError as err:
        if err.errno == errno.ENOENT:
            raise WebDriverException(
                "'%s' executable needs to be in PATH. %s" % (
                    os.path.basename(self.path), self.start_error_message)
            )
        elif err.errno == errno.EACCES:
            raise WebDriverException(
                "'%s' executable may have wrong permissions. %s" % (
                    os.path.basename(self.path), self.start_error_message)
            )
        else:
            raise
    except Exception as e:
        raise WebDriverException(
            "The executable %s needs to be available in the path. %s\n%s" %
            (os.path.basename(self.path), self.start_error_message, str(e)))
    count = 0
    while True:
        self.assert_process_still_running()
        if self.is_connectable():
            break

        count += 1
        sleep(0.5)
        if count == 60:
            raise WebDriverException("Can not connect to the Service %s" % self.path)
