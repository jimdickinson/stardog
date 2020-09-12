import os
import subprocess
import time

context_str = """kube1
kube2
kube3"""

contexts = context_str.split('\n')

for kubecontext in contexts:
    print("working on {}".format(kubecontext))
    os.mkdir("/tmp/{}".format(kubecontext))

    filename = "/tmp/{}/pods.json".format(kubecontext)
    print("writing to {}".format(filename))
    subprocess.run(args=[
        "bash", "-c",
        "kubectl --context={} get pods -A -o json > {}".format(kubecontext, filename)
        ])
    time.sleep(2)

    filename = "/tmp/{}/namespaces.json".format(kubecontext)
    print("writing to {}".format(filename))
    subprocess.run(args=[
        "bash", "-c",
        "kubectl --context={} get namespaces -A -o json > {}".format(kubecontext, filename)
        ])
    time.sleep(2)    

    filename = "/tmp/{}/deployments.json".format(kubecontext)
    print("writing to {}".format(filename))
    subprocess.run(args=[
        "bash", "-c",
        "kubectl --context={} get deployments -A -o json > {}".format(kubecontext, filename)
        ])
    time.sleep(2)
