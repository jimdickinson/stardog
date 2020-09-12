import os
import pathlib
import subprocess
import time
import fire

def fetch_contexts(*contexts):
    '''
    loop through the contexts passed in as varargs, and extract data from kube for each
    '''

    for kubecontext in contexts:
        print("working on {}".format(kubecontext))
        pathlib.Path("/tmp/{}".format(kubecontext)).mkdir(parents=True, exist_ok=True)

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

if __name__ == '__main__':
    fire.Fire(fetch_contexts)
