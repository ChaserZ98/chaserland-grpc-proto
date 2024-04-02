import os
import re
import subprocess
import sys

import click_extra as click

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROTO_DIR = os.path.join(BASE_DIR, "protos")

OUT_DIR = os.path.join(BASE_DIR, "chaserland_grpc_proto", "protos")

if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)


@click.extra_group(params=None)
def grpc_cli():
    pass


@grpc_cli.command(help="Create Python files from proto file")
@click.argument("proto_file", type=str)
@click.option(
    "-I",
    "--proto_path",
    default=PROTO_DIR,
    help="Path to search for proto files",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)
@click.option(
    "--python_out",
    default=OUT_DIR,
    help="Output directory for generated Python files",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)
@click.option(
    "--grpc_python_out",
    default=OUT_DIR,
    help="Output directory for generated gRPC Python files",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)
@click.option(
    "--pyi_out",
    default=OUT_DIR,
    help="Output directory for generated Python stub files",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)
def create(proto_file, proto_path, python_out, grpc_python_out, pyi_out):
    if not os.path.exists(os.path.join(proto_path, proto_file)):
        click.secho("Error: ", fg="red", nl=False)
        click.echo(f"File {click.style(proto_file, fg='yellow')} does not exist")
        return

    command = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        f"-I={proto_path}",
        f"--python_out={python_out}",
        f"--grpc_python_out={grpc_python_out}",
        f"--pyi_out={pyi_out}",
        proto_file,
    ]

    click.echo(
        f"Generating Python files from {click.style(proto_file, fg='yellow')}...",
        nl=False,
    )

    res = subprocess.run(command)

    if res.returncode != 0:
        click.secho("Failed", fg="red")
        return

    click.secho("Done", fg="green")

    click.echo(
        f"Fixing import issue for {click.style(os.path.basename(proto_file).replace('.proto', '_pb2_grpc.py'), fg='yellow')}...",
        nl=False,
    )
    fix_import_issue(proto_file, grpc_python_out)
    click.secho("Done", fg="green")

    click.echo(
        f"Formatting generated files in {click.style(OUT_DIR, fg='yellow')}...",
    )
    # ruff format generated files
    command = [
        "ruff",
        "check",
        "--no-cache",
        "--fix",
        "--select",
        "I",
        OUT_DIR,
    ]
    res = subprocess.run(command)
    click.secho("Done", fg="green")


def fix_import_issue(proto_file: str, grpc_python_out: str) -> None:
    filename = os.path.basename(proto_file).replace(".proto", "")
    # regular expression to match the import statement "from filename import ..."
    import_statement = rf"from {filename}"
    # replace with "from . import ..."
    with open(
        os.path.join(grpc_python_out, proto_file.replace(".proto", "_pb2_grpc.py")), "r"
    ) as f:
        content = f.read()
        content = re.sub(import_statement, f"from .", content)

    with open(
        os.path.join(grpc_python_out, proto_file.replace(".proto", "_pb2_grpc.py")), "w"
    ) as f:
        f.write(content)


@grpc_cli.command(help="Clean generated Python files")
@click.argument("proto_file", type=str)
@click.option(
    "-I",
    "--proto_path",
    default=PROTO_DIR,
    help="Path to search for proto files",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)
def clean(proto_file, proto_path):
    abs_proto_file = os.path.abspath(os.path.join(proto_path, proto_file))

    if os.path.isdir(abs_proto_file) or not os.path.exists(abs_proto_file):
        click.secho("Error: ", fg="red", nl=False)
        click.echo(
            f"File {click.style(proto_file, fg='yellow')} does not exist under {click.style(proto_path, fg='yellow')}"
        )
        return

    python_files = [
        f"{proto_file.replace('.proto', '_pb2.py')}",
        f"{proto_file.replace('.proto', '_pb2_grpc.py')}",
        f"{proto_file.replace('.proto', '_pb2.pyi')}",
    ]

    click.echo(
        f"Cleaning generated Python files from {click.style(proto_file, fg='yellow')}...",
    )

    for file in python_files:
        if os.path.exists(os.path.join(OUT_DIR, file)):
            click.echo(f"Removing {click.style(file, fg='yellow')}...", nl=False)

            os.remove(os.path.join(OUT_DIR, file))

            click.secho("Done", fg="green")
        else:
            click.echo(
                f"File {click.style(file, fg='yellow')} not found. {click.style('Skipped.', fg='yellow')}"
            )

    dirname = os.path.dirname(proto_file)
    abs_dir = os.path.abspath(os.path.join(OUT_DIR, dirname))

    # Remove empty directory
    if dirname and os.path.isdir(abs_dir) and not os.listdir(abs_dir):
        click.echo(
            f"Removing empty {click.style(dirname, fg='yellow')} directory...", nl=False
        )

        os.rmdir(os.path.join(OUT_DIR, dirname))

        click.secho("Done", fg="green")

    click.secho("Done", fg="green")


if __name__ == "__main__":
    grpc_cli()
