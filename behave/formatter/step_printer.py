class StepPrinter(object):
    def write_step(self, stream, text_format, arg_format, step_name, arguments):
        step_name = unicode(step_name)

        text_start = 0
        for arg in arguments:
            if arg.offset != 0:
                text = step_name[text_start:arg.offset].encode('utf8')
                stream.write(text_format.text(text))
            stream.write(arg_format.text(arg.val))
            text_start = arg.offset + len(unicode(arg.val))

        if text_start != len(step_name):
            text = step_name[text_start:].encode('utf8')
            stream.write(text_format.text(text))
