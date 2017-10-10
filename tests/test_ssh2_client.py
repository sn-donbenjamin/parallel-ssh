import unittest
import os
import logging
import time

from gevent import socket

from .base_ssh2_test import SSH2TestCase
from .embedded_server.openssh import OpenSSHServer
from pssh.ssh2_client import SSHClient, logger as ssh_logger
from pssh.exceptions import AuthenticationException, ConnectionErrorException


ssh_logger.setLevel(logging.DEBUG)
logging.basicConfig()


class SSH2ClientTest(SSH2TestCase):

    def test_execute(self):
        channel, host, stdout, stderr, stdin = self.client.run_command(
            self.cmd)
        output = list(stdout)
        stderr = list(stderr)
        expected = [self.resp]
        exit_code = channel.get_exit_status()
        self.assertEqual(exit_code, 0)
        self.assertEqual(expected, output)

    def test_stderr(self):
        channel, host, stdout, stderr, stdin = self.client.run_command(
            'echo "me" >&2')
        self.client.wait_finished(channel)
        output = list(stdout)
        stderr = list(stderr)
        expected = ['me']
        self.assertListEqual(expected, stderr)
        self.assertTrue(len(output) == 0)

    def test_long_running_cmd(self):
        channel, host, stdout, stderr, stdin = self.client.run_command(
            'sleep 2; exit 2')
        self.client.wait_finished(channel)
        exit_code = channel.get_exit_status()
        self.assertEqual(exit_code, 2)

    def test_manual_auth(self):
        client = SSHClient(self.host, port=self.port,
                           pkey=self.user_key,
                           num_retries=1)
        client.session.disconnect()
        del client.session
        del client.sock
        client.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client._connect()
        client._init()

    def test_identity_auth_failure(self):
        self.assertRaises(AuthenticationException,
                          SSHClient, self.host, port=self.port, num_retries=1,
                          allow_agent=False)

    def test_agent_auth_failure(self):
        self.assertRaises(AuthenticationException,
                          SSHClient, self.host, port=self.port, num_retries=1,
                          allow_agent=True)

    def test_password_auth_failure(self):
        self.assertRaises(AuthenticationException,
                          SSHClient, self.host, port=self.port, num_retries=1,
                          password='blah blah blah')

    def test_retry_failure(self):
        self.assertRaises(ConnectionErrorException,
                          SSHClient, self.host, port=12345,
                          num_retries=2)
