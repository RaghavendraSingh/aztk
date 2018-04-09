import os
from aztk.utils import ssh
from aztk.utils.command_builder import CommandBuilder
from aztk import models as aztk_models
import azure.batch.models as batch_models

def run(spark_client, cluster_id, output_directory):
    # copy debug program to each node
    spark_client.cluster_copy(cluster_id, os.path.abspath("./aztk/spark/utils/debug.py"), "/tmp/debug.py", host=True)
    ssh_cmd = _build_diagnostic_ssh_command()
    run_output = spark_client.cluster_run(cluster_id, ssh_cmd, host=True)
    local_path = os.path.join(os.path.abspath(output_directory), "debug", "debug.zip")
    remote_path = "/tmp/debug.zip"
    output = spark_client.cluster_download(cluster_id, remote_path, local_path, host=True)
    # write run output to debug/ directory
    with open(os.path.join(os.path.dirname(local_path), "debug-output.txt"), 'w', encoding="UTF-8") as f:
        [f.write(line + '\n') for node_id, result in run_output for line in result]
    return output


def _build_diagnostic_ssh_command():
    return "sudo rm -rf /tmp/debug.zip; "\
           "sudo apt-get install -y python3-pip; "\
           "sudo -H pip3 install --upgrade pip; "\
           "sudo -H pip3 install docker; "\
           "sudo python3 /tmp/debug.py"
