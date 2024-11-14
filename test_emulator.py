import unittest
from unittest.mock import patch
import io
from emulator import Emulator

class TestEmulator(unittest.TestCase):
    def setUp(self):
        self.user = "heragromov"
        self.host = "Heras-MacBook-Pro"
        self.fs_path = "vfc_archive_new.tar"
        self.log_path = "log.json"
        self.emulator = Emulator(self.user, self.host, self.fs_path, self.log_path)

    def test_ls_root_directory(self):
        with patch('builtins.input', side_effect=["ls", "exit"]), patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            self.emulator.run()
            output = mock_stdout.getvalue()
            self.assertIn("Contents of directory '.'", output)
            self.assertIn("vfc", output)

    def test_cd_command(self):
        with patch('builtins.input', side_effect=["cd vfc", "ls", "exit"]), patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            self.emulator.run()
            output = mock_stdout.getvalue()
            self.assertIn("Contents of directory 'vfc'", output)
            self.assertIn("bin", output)

    def test_wc_command(self):
        with patch('builtins.input', side_effect=["wc vfc/bin/usr/3.txt", "exit"]), patch('sys.stdout',
                                                                                          new_callable=io.StringIO) as mock_stdout:
            self.emulator.run()
            output = mock_stdout.getvalue()
            self.assertIn("3 21 124 vfc/bin/usr/3.txt", output)

    def test_tac_command(self):
        with patch('builtins.input', side_effect=["tac vfc/bin/usr/3.txt", "exit"]), patch('sys.stdout',
                                                                                           new_callable=io.StringIO) as mock_stdout:
            self.emulator.run()
            output = mock_stdout.getvalue()
            self.assertIn("Этот файл добавлен для расширенного тестирования команд ls, wc и tac.", output)

    def test_exit_command(self):
        with patch('builtins.input', side_effect=["exit"]), patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            self.emulator.run()
            output = mock_stdout.getvalue()
            self.assertIn("Exiting emulator.", output)

if __name__ == "__main__":
    unittest.main()
