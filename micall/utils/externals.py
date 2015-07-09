import subprocess
import os
import sys

class AssetWrapper(object):
    """ Wraps a packaged asset, and finds its path. """
    def __init__(self, path):
        self.path = os.path.join(getattr(sys, '_MEIPASS', ''), path)

class CommandWrapper(AssetWrapper):
    """ Wraps an external tool, and builds the command lines for it. """
    def __init__(self, version, execname, logger=None, *args, **kwargs):
        super(CommandWrapper, self).__init__(path=execname, *args, **kwargs)
        self.version = version
        self.logger = logger
        
    def check_output(self, args=[], *popenargs, **kwargs):
        """ Run command with arguments and return its output as a byte string.
        
        See subprocess.check_output() for details.
        @param args: a list of program arguments
        @param popenargs: other positional arguments to pass along
        @param kwargs: keyword arguments to pass along
        @return the command's output
        """
        return subprocess.check_output([self.path] + args, *popenargs, **kwargs)
    
    def create_process(self, args=[], *popenargs, **kwargs):
        """ Execute a child program in a new process.
        
        See subprocess.Popen class for details.
        @param args: a list of program arguments
        @param popenargs: other positional arguments to pass along
        @param kwargs: keyword arguments to pass along
        @return the new Popen object 
        """
        return subprocess.Popen([self.path] + args, *popenargs, **kwargs)
    

    def check_logger(self):
        """ Raise an exception if no logger is set for this command. """
        if self.logger is None:
            raise RuntimeError('logger not set for command {}'.format(self.path))

    def log_call(self, args, format_string='%s'):
        """ Launch a subprocess, and log any output to the debug logger.
        
        Raise an exception if the return code is not zero. This assumes only a
        small amount of output, and holds it all in memory before logging it.
        Logged output includes both stdout and stderr.
        @param args: A list of arguments to pass to check_output().
        @param logger: the logger to log to
        @param format_string: A template for the debug message that will have
        each line of output formatted with it.
        """
        self.check_logger()
        output = self.check_output(args, stderr=subprocess.STDOUT)
        for line in output.splitlines():
            self.logger.debug(format_string, line)

    def redirect_call(self, args, outpath, format_string='%s'):
        """ Launch a subprocess, and redirect the output to a file.
        
        Raise an exception if the return code is not zero.
        Standard error is logged to the debug logger.
        @param args: A list of arguments to pass to subprocess.Popen().
        @param outpath: a filename that stdout should be redirected to. If you 
        don't need to redirect the output, then just use subprocess.check_call().
        @param format_string: A template for the debug message that will have each
        line of standard error formatted with it.
        """
        self.check_logger()
        with open(outpath, 'w') as outfile:
            p = self.create_process(args, stdout=outfile, stderr=subprocess.PIPE)
            for line in p.stderr:
                self.logger.debug(format_string, line.rstrip())
            if p.returncode:
                raise subprocess.CalledProcessError(p.returncode, args)
    
    def validate_version(self, version_found):
        if self.version != version_found:
            message = '{} version incompatibility: expected {}, found {}'.format(
                self.path, 
                self.version, 
                version_found)
            raise RuntimeError(message)

class Samtools(CommandWrapper):
    def __init__(self, version, execname='samtools', logger=None, *args, **kwargs):
        super(Samtools, self).__init__(version, execname, logger, *args, **kwargs)
        p = self.create_process(stderr=subprocess.PIPE)
        _stdout, stderr = p.communicate()
        version_lines = filter(lambda x: x.startswith('Version:'), stderr.split('\n'))

        version_fields = version_lines and version_lines[0].split() or []
        version_found = version_fields and version_fields[1] or 'unreadable'
        self.validate_version(version_found)

class Bowtie2(CommandWrapper):
    def __init__(self, version, execname='bowtie2', logger=None, *args, **kwargs):
        super(Bowtie2, self).__init__(version, execname, logger, *args, **kwargs)
        stdout = self.check_output(['--version'])
        version_found = stdout.split('\n')[0].split()[-1]
        self.validate_version(version_found)

class Bowtie2Build(CommandWrapper):
    def __init__(self,
                 version,
                 execname='bowtie2-build',
                 logger=None,
                 *args,
                 **kwargs):
        super(Bowtie2Build, self).__init__(version,
                                           execname,
                                           logger,
                                           *args,
                                           **kwargs)
        stdout = self.check_output(['--version'])
        version_found = stdout.split('\n')[0].split()[-1]
        self.validate_version(version_found)
