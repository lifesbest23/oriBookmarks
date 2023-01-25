import shlex
import struct
import subprocess


def notify(text, time=1000):
    args = shlex.split("notify-send -t " + str(time) + " '" + text + "'")
    subprocess.run(args)


class Rofi:
    """Reusable rofi Prompter with persistent settings

    The different request* functions open rofi with specific settings."""
    # ToDo: init
    # - more functions
    #   - one for requesting and returning a default if no input was given
    #   - one for looping in case of canceling
    #   - one that exits system if None was returned
    #   - one that lets you input numbers in a specific range
    #   - one for receiving already present text and returning an edited string
    # - add setting for exit on cancel rofi with esc

    def getRofiCommand(self, additional_options=[]):
        rofi_command = ['rofi', '-dmenu']
        rofi_command += ['-lines', '10', '-i']
        additional_options.extend(['-sep', '\\0'])
        return rofi_command + additional_options

    def requestInput(self, text, options: list):
        args = self.getRofiCommand(["-p", text])
        proc = subprocess.Popen(args,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)

        for e in options:
            proc.stdin.write((e).encode('utf-8'))
            proc.stdin.write(struct.pack('B', 0))
        proc.stdin.close()

        ret = proc.stdout.read().decode("utf-8")
        exit_code = proc.wait()

        print("Exit Code of rofi: " + str(exit_code))
        if ret == "":
            return None

        ret = ret.split("\n", 1)[0]

        return ret


if __name__ == "__main__":
    opts = ["Line1", "Line2", "Line3"]
    rofiPrompter = Rofi()
    ret = rofiPrompter.requestInput("Select some line", opts)
    print(f"The return value was {ret}")
