"""Python modules and distribution encryption tool"""
import ast
import base64
from collections import defaultdict
import hashlib
import logging
import os
import re
import shutil
import tempfile
import zipfile
import zlib

try:
    import astunparse
except ImportError:
    astunparse = None

import pyaes
import fire


MODULE_TEMPLATE = os.path.join(os.path.dirname(__file__), "module_template.txt")
KEY_SIZE = 16
MAX_LINE_LENGTH = 80

template = None

logging.basicConfig(format="%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def tag(*names):
    return lambda function: function


def _is_matching_decorator(node, removal_expression):
    if not hasattr(node, "decorator_list"):
        return False
    else:
        calls_list = [
            call for call in node.decorator_list
            if type(call) is ast.Call
        ]
        private_tag_call = [
            call for call in calls_list
            if call.func.value.id == __name__
            and call.func.attr == tag.__name__
        ]

        if len(private_tag_call) == 0:
            return False
        elif len(private_tag_call) > 1:
            raise ValueError("More then one call to tag decorator")

        private_tag_call, = private_tag_call

        tags = {arg.s: True for arg in private_tag_call.args}
        expression_globals = defaultdict(lambda: False, **tags)
        return eval(removal_expression, expression_globals)


def _remove_tagged_source(source, removal_expression):
    ast_tree = ast.parse(source)
    if hasattr(ast_tree, "body"):
        ast_tree.body = [
            sub_node for sub_node in ast_tree.body
            if not _is_matching_decorator(sub_node, removal_expression)
        ]
        for sub_node in ast_tree.body:
            _remove_tagged_source(sub_node, removal_expression)
    return astunparse.unparse(ast_tree)


def _chunks(data, chunk_size):
    """Returns generator that yields chunks of chunk size of data"""
    return (data[i:i + chunk_size] for i in range(0, len(data), chunk_size))


def encrypt_module(module_path, output_path, key, removal_expression=None):
    """Encrypts python file with into output path"""

    with open(module_path, "r") as module_file:
        module_content = module_file.read()

    if removal_expression is not None:
        module_content = _remove_tagged_source(module_content, removal_expression)

    module_content = zlib.compress(module_content)
    # The hash is calculated on the compressed module to detect wrong key
    # before trying to decompress the code
    code_hash = hashlib.sha256(module_content).hexdigest()

    encryptor = pyaes.AESModeOfOperationCTR(key)
    encrypted_module = base64.b64encode(encryptor.encrypt(module_content))
    # format the encrypted code to sepreate lines
    encrypted_module = os.linesep + os.linesep.join(_chunks(encrypted_module, MAX_LINE_LENGTH))

    global template
    if template is None:
        with open(MODULE_TEMPLATE, "r") as template_file:
            template = template_file.read()

    with open(output_path, "w") as output_file:
        output_file.write(
            template.format(
                module_name=__name__,
                encryped_code=encrypted_module,
                code_hash=code_hash
            )
        )
    logger.debug("Encrypted file {} into {}".format(module_path, output_path))


def load_module_content(encrypted_module, key, code_hash):
    """Decrypt encrypted code and validates against hash.
    It should only be used internally by encrypted modules."""
    decryptor = pyaes.AESModeOfOperationCTR(key)
    decrypted_module = decryptor.decrypt(
        base64.b64decode(encrypted_module.strip().replace(os.linesep, ""))
    )
    if hashlib.sha256(decrypted_module).hexdigest() != code_hash:
        raise ValueError("Decrypted code hash mismatch! Key may be wrong")
    decrypted_module = zlib.decompress(decrypted_module)
    return decrypted_module


def encrypt_directory(input_directory, output_directory, key, removal_expression=None):
    for root, _, files in os.walk(input_directory):
        encrypted_path = os.path.join(output_directory, (os.path.relpath(root, input_directory)))
        if not os.path.exists(encrypted_path):
            os.makedirs(encrypted_path)
        for file_name in files:
            source_file = os.path.join(root, file_name)
            destionation_file = os.path.join(encrypted_path, file_name)
            if file_name.endswith(".py"):
                encrypt_module(
                    source_file,
                    destionation_file,
                    key,
                    removal_expression=removal_expression
                )
            else:
                shutil.copy2(source_file, destionation_file)
                logger.debug("Copying {} to {}".format(source_file, destionation_file))


def _generate_record_file(directory):
    records = set()
    for root, _, files in os.walk(directory):
        for current_file_name in files:
            if current_file_name == "RECORD":
                continue
            current_file_path = os.path.join(root, current_file_name)
            with open(current_file_path, "r") as current_file:
                file_content = current_file.read()
            file_hash = hashlib.sha256(file_content).digest()
            record = [
                os.path.relpath(current_file_path, directory),
                "sha256=" + base64.urlsafe_b64encode(file_hash).replace("=", ""),
                str(len(file_content))
            ]
            records.add(",".join(record))
    return "\n".join(records)


def encrypt_wheel(wheel_path, output_dir, key, removal_expression=None):
    """Encrypts wheel package with key into output directory"""
    unzipped_dir = tempfile.mkdtemp()
    encrypted_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(wheel_path, "r") as wheel_file:
        wheel_file.extractall(unzipped_dir)

    logger.info("Encrypting wheel {}".format(wheel_path))
    encrypt_directory(
        unzipped_dir,
        encrypted_dir,
        key,
        removal_expression=removal_expression
    )

    record_content = _generate_record_file(encrypted_dir)
    dist_info_directory, = [
        path for path in os.listdir(encrypted_dir)
        if re.match(".*\.dist-info", path)
    ]
    record_file_path = os.path.join(dist_info_directory, "RECORD")
    logger.info("Rewriting " + record_file_path)
    record_content += "\n{},,".format(record_file_path)
    with open(os.path.join(encrypted_dir, record_file_path), "w") as record_file:
        record_file.write(record_content)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, os.path.basename(wheel_path))
    shutil.make_archive(output_path, "zip", root_dir=encrypted_dir)
    os.rename(output_path + ".zip", output_path)


def private(*paths, **kwargs):
    """Private encrypts python files and wheel packages.
    To use the encrypted code, export the key to PRIVATE_KEY variable"""
    key = kwargs.pop("key", None)
    output = kwargs.pop("output", "output")
    removal_expression = kwargs.pop("predicate", None)

    if removal_expression is not None and astunparse is None:
        logger.error("Cannot remove source code by tag without astunparse, please install it")
        exit(1)

    for argument in kwargs.keys():
        if argument not in ["key", "output"]:
            logger.warning('Unknown argument "{}"'.format(argument))
            return

    if key is None:
        key = os.urandom(KEY_SIZE)
    else:
        if type(key) is not str:
            key = str(key)
        try:
            key = key.decode("hex")
        except TypeError:
            logger.warning("The key must be hexadecimal string!")
            return
        if len(key) != KEY_SIZE:
            logger.warning("The key must be of length {}, current length is {}".format(KEY_SIZE, len(key)))
            return

    if not os.path.exists(output):
        os.makedirs(output)

    logger.info("Using key {}".format(key.encode("hex")))
    with open(os.path.join(output, "key.txt"), "w") as key_file:
        key_file.write(key.encode("hex"))

    for path in paths:
        if not os.path.exists(path):
            logger.warning("Path {} does not exists, skipping".format(path))
            continue
        _, extension = os.path.splitext(path)
        if os.path.isdir(path):
            encrypt_directory(
                path,
                os.path.join(output, os.path.basename(path)),
                key,
                removal_expression=removal_expression
            )
        elif extension == ".whl":
            encrypt_wheel(path, output, key, removal_expression=removal_expression)
        elif extension == ".py":
            encrypt_module(
                path,
                os.path.join(output, path),
                key,
                removal_expression=removal_expression
            )
        else:
            logging.warning("Path {} must have extension .whl or .py, skipping".format(path))


def main():
    fire.Fire(private)


if __name__ == '__main__':
    main()
