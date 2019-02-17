#!/usr/bin/python3

from ansibleautodoc.Utils import SingleLog


class TestLog(object):

    def test_default_log_level(self):
        log = SingleLog()
        assert log.log_level == 1

    def test_set_log_level_debug(self):
        log = SingleLog()
        log.set_level(0)
        log.set_level("debug")
        assert log.log_level == 0

    def test_print_in_info(self,capsys):
        log = SingleLog()
        log.set_level("info")
        log.debug("test message")
        log.info("test message")
        captured = capsys.readouterr()
        assert captured.out == "*INFO*: test message\n"

    def test_print_list(self,capsys):
        SingleLog.print("msg",["item1"])
        captured = capsys.readouterr()
        assert captured.out == 'msg\n  [0]: item1\n'