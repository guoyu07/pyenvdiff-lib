# -*- coding: utf-8 -*-

from .version import __version__
from .info import Environment
from .import_macros import import_os, import_json, import_urllib_x

os = import_os()
json = import_json()
Request, urlopen = import_urllib_x()

DEFAULT_SERVER = 'https://osa.pyenvdiff.com'
LOCAL_SERVER = 'http://localhost:8080'
DEFAULT_API_KEY = 'qcjODGX4iw3cEPIQR7Jn77uTKSuQOvwS4Q4z7AwR'
    
def get_api_key():

    api_key = DEFAULT_API_KEY

    try:
        setting = os.environ.get('PYENVDIFF_API_KEY', None)
        if (setting.upper() == 'DEFAULT') or (setting is None):
            pass  # server = DEFAULT_API_KEY
        else:
            api_key = setting
    except:
        pass

    return api_key


def get_server_url():

    server = DEFAULT_SERVER

    try:
        setting = os.environ.get('PYENVDIFF_SERVER', None)
        if (setting.upper() == 'DEFAULT') or (setting is None):
            pass  # server = DEFAULT_SERVER
        elif (setting.upper() == 'LOCAL'):
            server = LOCAL_SERVER
        else:
            server = setting
    except:
        pass

    return server


def send(environment,
         organization=None,
         group=None,
         subgroup=None,
         username=None,
         email=None,
         domain=None,
         application=None,
         version=None,
         tags=None):
    data = {'pyenvdiff_version': __version__}

    data['user_meta'] = {'organization': organization,
                         'group': group,
                         'subgroup': subgroup,
                         'username': username,
                         'email': email,
                         'domain': domain,
                         'application': application,
                         'version': version,
                         'tags': tags}

    data['environment'] = environment.info()

    data = json.dumps(data)
    data = data.encode('utf-8')
    clen = len(data)

    server = get_server_url()
    api_key = get_api_key()

    print("Posting environment information to " + server)
    print("Using API KEY: " + api_key[:6] + "...")

    req = Request(server + "/submit", data, {'x-api-key': api_key,
                                             'Content-Type': 'application/json',
                                             'Content-Length': clen})

    f = urlopen(req)
    response = f.read()

    response = json.loads(response.decode('utf-8'))

    f.close()

    if response['result'] == 'OK':
        iid = response['id']
        return "Successful POST, use ID# %s for reference or comparison." % iid
    else:
        return response


def get_available_parser_name_and_class():
    module_name = None
    Parser = None

    if module_name is None:
        try:
            import argparse
            Parser = argparse.ArgumentParser
            module_name = 'argparse'
        except:
            print("Couldn't find argparse, trying optparse")

    if module_name is None:
        try:
            import optparse
            Parser = optparse.OptionParser
            module_name = 'optparse'
        except:
            print("Couldn't find optparse, trying getopt")

    if module_name is None:
        try:
            import getopt
            module_name = 'getopt'
            Parser = getopt.getopt  # Awkward, but...compatible
        except:
            print("Couldn't find getopt, arguments won't be parsed; ignoring all arguments")

    return module_name, Parser


def execute_parsing_engine(parser_module_name, Parser):
    args_info = [('o', 'organization', "Your organization's name, use quotes for spaces"),
                 ('g', 'group', "Your group's name, spaces okay, use quotes for spaces"),
                 ('s', 'subgroup', "Your subgroup/team's name, use quotes for spaces"),
                 ('u', 'username', 'Your name, spaces okay, use quotes for spaces'),
                 ('e', 'email', 'Your email address.'),
                 ('d', 'domain', 'The domain of your company or application.'),
                 ('a', 'application', 'Your application name, use quotes for spaces'),
                 ('v', 'version', 'Your application version, use quotes for spaces'),
                 ('t', 'tags',  'Tags seperated by commas. Foo,MyApp Dev,Bar,Boo -> [\'Foo\', \'My Dev\', \'Bar\', \'Boo\']')]  # noqa: E501

    arg_char, arg_full, arg_desc = zip(*args_info)

    arg_as_optn = ["-" + a for a in arg_char]
    arg_in_full = ["--" + a for a in arg_full]

    DESCRIPTION = "Send pyenvdiff info to the central comparison and survey server."

    def compatible_arg_parser(adder_method):
        parser = Parser(description=DESCRIPTION)
        for opt, ful, desc in zip(arg_as_optn, arg_in_full, arg_desc):
            getattr(parser, adder_method)(opt, ful, type=str, help=desc)
        return parser

    if parser_module_name == 'argparse':
        parser = compatible_arg_parser('add_argument')
        args = parser.parse_args()
        args = vars(args)
    elif parser_module_name == 'optparse':
        parser = compatible_arg_parser('add_option')
        options, _ = parser.parse_args()
        args = vars(options)
    elif parser_module_name == 'getopt':
        import sys

        # this is getopt.getopt, not a Parser
        args, _ = Parser(sys.argv[1:], "h" +
                         ":".join(arg_char) + ":", ["help"])
        if len(args):
            args_provided, vals_provided = zip(*args)  # noqa: F841
        else:
            args_provided, vals_provided = [], []  # noqa: F841
        if '-h' in args_provided:
            print(DESCRIPTION)
            print("Usage:")
            help_info = list(
                zip(arg_as_optn, [x.upper() for x in arg_full], arg_desc))

            for i in range(int(len(help_info)) // 3):
                start = i * 3
                end = start + 3
                out = "] [".join(((nfo[0] + " " + nfo[1])
                                  for nfo in help_info[start:end]))
                print("[" + out + "]")

            sys.exit(0)

        look_up = dict(zip(arg_as_optn, arg_full))

        # this is for python 2.6 compatibility
        actual_args = {}
        for arg in args:
            if arg[0] != '-h':
                args[look_up[arg[0]]] = arg[1]
        args = actual_args
    else:
        args = {}

    tags = args.get('tags', None)
    if tags:
        args['tags'] = tags.split(",")

    return args


def main():
    parser_details = get_available_parser_name_and_class()
    args = execute_parsing_engine(*parser_details)

    env = Environment()
    resp = send(env, **args)
    print(resp)


if __name__ == '__main__':

    main()
