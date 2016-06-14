from functools import partial


class DockerBuildCommand(object):
    """ Generates a `docker build` command to run in a subprocess.
    """
    def __init__(self, docker_repo, tag, dockerfile='Dockerfile'):
        self.docker_repo = docker_repo
        self.tag = tag
        self.dockerfile = dockerfile

    def build(self):
        def docker_build_command(process_num):
            return "docker build -f {0} -t {1}:{2} .".format(
                self.dockerfile, self.docker_repo, self.tag)
        return docker_build_command

    def full_path(self):
        return "{0}:{1}".format(self.docker_repo, self.tag)


class DockerCommand(object):
    def __init__(self, docker_command, name_prefix):
        self.docker_command = docker_command
        self.name_prefix = name_prefix


class DockerComposeCommand(object):
    """ Generates docker or docker-compose commands to run in a subprocess.
    """

    def __init__(self, docker_compose_file='docker-compose.yml',
                 project_name_base=None, env_vars=None):
        self.docker_compose_file = docker_compose_file
        self.env_vars = env_vars or {}
        self.project_name_base = project_name_base

    def _build_cmd(self, app, cmd_string, docker_compose_command, process_num):
        """ Builds the docker-compose command running cmd_string
            process_num gets appended to the project name which lets you run
            in parallel on separate docker-compose clusters of containers.
        """
        output = self._env_vars_prefix()
        output += self._compose_with_file_and_project_name(process_num)
        output += " {0}".format(docker_compose_command)
        if app:
            output += " {0}".format(app)
        if cmd_string:
            output += " {0}".format(cmd_string)
        return output

    def _cleanup_cmd(self, process_num):
        tmp = self._env_vars_prefix()
        tmp += self._compose_with_file_and_project_name(process_num)
        return "{0} stop && {0} rm --force".format(tmp)

    def _compose_with_file_and_project_name(self, process_num):
        output = "docker-compose"
        output += " -f {0}".format(self.docker_compose_file)
        if self.project_name_base:
            project_name = self.project_name_base
            if process_num:
                project_name += str(process_num)
            output += " -p {0}".format(project_name)
        return output

    def _env_vars_prefix(self):
        output = ""
        if self.env_vars:
            output += ' '.join("{0}={1}".format(k, v) for k, v in self.env_vars.items())
            output += " "
        return output

    def build(self, app, docker_compose_command, cmd_string=None):
        return partial(self._build_cmd, app, cmd_string, docker_compose_command)

    def cleanup(self):
        return self._cleanup_cmd