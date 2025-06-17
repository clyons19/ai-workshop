"""Run this file to check your environment setup."""

import importlib
import os
import re
import sys
from functools import partial
from typing import Union

import pkg_resources
from packaging.version import Version


def run_env_check(env_path: Union[os.PathLike[str], str],
                  alt_package_names: Union[dict[str, str], None]=None,
                  raise_exc: bool=False):
    """
    Check that the packages we need are installed and, if necessary,
    whether the Python version is correct. If env_path is a yaml file
    a conda environment is assumed, otherwise a pip environment is
    assumed.

    INPUT:
        env_path (os.PathLike):
            Path to environment requirements file (i.e., requirements.txt
            for pip environments and environment.yml for conda
            environments)
        alt_package_names (dict[str, str]): Default None
            Dictionary of alternative package names used to import the
            package. Dict should be KEY=colloquially known package name
            with VALUE=import name. Only required for checking conda envs
        raise_exc (bool): Default False
            Whether to raise an `Exception` if any of the packages
            do not match the requirements (used for GitHub Action
            currently and for only conda environments).
    """
    use_conda = os.path.splitext(env_path)[-1].lower() == '.yml'
    env = _preprocess_env(_load_env(env_path))
    if use_conda:
        _conda_env_check(env, alt_package_names=alt_package_names, raise_exc=raise_exc)
        return
    _pip_env_check(env)

def _load_env(env_path):
    try:
        env = _readlines(env_path)
    except FileNotFoundError:
        try:
            env = _readlines(os.path.join('..', env_path))
        except FileNotFoundError:
            try:
                env = _readlines(os.path.join(os.path.dirname(os.path.abspath(__file__)), env_path))
            except FileNotFoundError:
                raise FileNotFoundError(f"Could not find: {env_path}")
    return env

def _readlines(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()
    return content

def _preprocess_env(env):
    env = [line.strip() for line in env]
    env = [line.replace('-', '', 1) if line.startswith('-') else line for line in env]
    env = [line.strip() for line in env]
    env = [line for line in env if line and not line.startswith('#') and ':' not in line]
    return env

def _pip_env_check(env: list[str],
                   raise_exc: bool=False):
    """
    Check if packages in env are installed and meet version specs.

    INPUT:
        env (list[str]):
            List of packages and their version constraints
    """
    failures = []
    env_ = {re.split(r'[^a-zA-Z0-9_-]', line, maxsplit=1)[0]: line for line in env}
    status = {pkg: _pip_req_check(line) for pkg, line in env_.items()}
    for pkg, check in status.items():
        if check is None:
            _print_version_ok(pkg)
            continue
        failures.append(pkg)
        _print_version_failure(f'{pkg}: {check}')
  
    if failures and raise_exc:
        raise Exception(
            'Environment failed inspection due to incorrect versions '
            f'of {len(failures)} item(s): {", ".join(failures)}.'
        )

def _pip_req_check(reqs_line): # Parse the requirement using pkg_resources
    try:
        req = pkg_resources.Requirement.parse(reqs_line)
        assert pkg_resources.require is not None
        pkg_resources.require(str(req))  # will raise exception if not satisfied
        return None
    except Exception as e:
        return e

def _conda_env_check(env: list[str],
                     alt_package_names: Union[dict[str, str], None]=None,
                     raise_exc: bool=False):
    failures = []
    _failure_msg = partial(_create_failure_msg, failures=failures)
    alt_package_names = {} if alt_package_names is None else alt_package_names

    requirements = {}
    for line in env:
        try:
            if '>=' in line:
                pkg, versions = line.split('>=')
                if ',<=' in versions:
                    version = versions.split(',<=')
                else:
                    version = [versions, None]
            else:
                pkg, version = line.split('=')
        except ValueError:
            pkg, version = line, None
        requirements[pkg.split('::')[-1]] = version

    ### check the python version, if provided ##
    try:
        required_version = requirements.pop('python')
        python_version = sys.version_info
        base_python_version = Version(
            f'{python_version.major}.{python_version.minor}.{python_version.micro}'
        )
        if required_version is None:
            _print_version_ok('python')
        elif isinstance(required_version, list):
            versions = [v if v is None else Version(v) for v in required_version]
            min_version, max_version = versions
            if (
                (min_version and min_version > base_python_version)
                or
                (max_version and base_python_version > max_version)
            ):
                print(f'Using Python at {sys.prefix}:\n-> {sys.version}')
                msg = _failure_msg(
                        'python',
                        f'>= {min_version}{f" and <= {max_version}" if max_version else ""}',
                        base_python_version
                      )
                _print_version_failure(msg)
            else:
                _print_version_ok('python')
        else:
            for component, value in zip(
                ['major', 'minor', 'micro'], required_version.split('.')
            ):
                if getattr(python_version, component) != int(value):
                    print(f'Using Python at {sys.prefix}:\n-> {sys.version}')
                    msg = _failure_msg(
                            'python',
                            required_version,
                            f'{python_version.major}.{python_version.minor}'
                          )
                    _print_version_failure(msg)
                    break
            else:
                _print_version_ok('python')
    except KeyError:
        pass

    ## check additional package versions ##
    for pkg, req_version in requirements.items():
        try:
            import_name = alt_package_names[pkg]
        except KeyError:
            import_name=pkg
        try:
            mod = importlib.import_module(import_name)
            if req_version:
                try:
                    version = mod.__version__
                    installed_version = Version(version).base_version
                except AttributeError:
                    _print_version_ok(f'{pkg} is installed, but exact version could not be determined')
                    continue
                if isinstance(req_version, list):
                    min_version, max_version = req_version
                    if (
                        installed_version < Version(min_version).base_version
                        or (
                            max_version and
                            installed_version > Version(max_version).base_version
                        )
                    ):
                        msg = _failure_msg(
                                pkg,
                                f'>= {min_version}{f" and <= {max_version}" if max_version else ""}',
                                version
                              )
                        _print_version_failure(msg)
                        continue
                elif Version(version).base_version != Version(req_version).base_version:
                    msg = _failure_msg(pkg, req_version, version)
                    _print_version_failure(msg)
                    continue
            _print_version_ok(pkg)
        except ImportError:
            msg = _failure_msg(pkg, req_version, None)
            _print_version_failure(msg)

    if failures and raise_exc:
        raise Exception(
            'Environment failed inspection due to incorrect versions '
            f'of {len(failures)} item(s): {", ".join(failures)}.'
        )

def _print_version_ok(item):
    """
    Print an OK message for version check.

    Parameters
    ----------
    item : str
        The item being inspected (package, tool, etc.).
    """
    print('\x1b[42m[ OK ]\x1b[0m', '%s' % item)

def _create_failure_msg(item, req_version, version, failures):
    """
    Creates a failure message for version check.

    Parameters
    ----------
    item : str
        The item being inspected (package, tool, etc.).
    msg: str
        Failure message.
    failures : list
        The list of items currently failing the environment check.
    """
    failures.append(item)
    if version:
        msg = '%s version %s is required, but %s installed.'
        values = (item, req_version, version)
    else:
        msg = '%s is not installed.'
        values = item
    return msg % values

def _print_version_failure(msg):
    print('\x1b[41m[FAIL]\x1b[0m', '%s' % msg)

def _pip_conda_check(conda_env_path: Union[os.PathLike[str], str, None]=None,
                     pip_env_path: Union[os.PathLike[str], str, None]=None):
    use_conda, use_pip = False, False
    try:
        _ = _load_env(conda_env_path)
    except FileNotFoundError:
        pass
    else:
        print('Conda environment.yml file found in project')
        use_conda = True
    try:
        _ = _load_env(pip_env_path)
    except FileNotFoundError:
        pass
    else:
        print('Pip requirements.txt file found in project')
        use_pip = True
    return use_conda, use_pip

if __name__ == '__main__':
    alt_package_names = {
        'pillow' : 'PIL',
        'scikit-learn' : 'sklearn'
    }
    conda_env_path = os.path.join('environment.yml')
    pip_env_path = os.path.join('requirements.txt')
    raise_exc = True


    print(f'Using Python\n\t{sys.version}\nat\n\t{sys.prefix}')
    use_conda, use_pip = _pip_conda_check(conda_env_path=conda_env_path, pip_env_path=pip_env_path)
    if use_conda and use_pip:
        msg = (
            "Both conda and pip envs found. "
            "Specify which you want to check ['conda', 'pip', 'both']. "
            "(Default='both'):"
        )
        msg = input(msg)
        if msg.lower() == 'conda':
            use_pip = False
        elif msg.lower() == 'pip':
            use_conda = False
    if use_conda:
        print('Checking conda environment:')
        run_env_check(env_path=conda_env_path,
                      alt_package_names=alt_package_names,
                      raise_exc=raise_exc)
    if use_pip:
        print('Checking pip environment:')
        run_env_check(env_path=pip_env_path, raise_exc=raise_exc)
