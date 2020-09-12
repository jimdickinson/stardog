import fire
import json
import os

def handle_data(*dirs):
    """
    handle_data takes a varargs list of directories and loops through it printing a
    summary of the k8s resources
    """
    for d in dirs:
        for kubecontext, ns, pod in process(d, "pods"):
            print(kubecontext, ns, pod["metadata"]["name"])

        for kubecontext, ns, namespace in process(d, "namespaces"):
            print(kubecontext, ns, namespace["metadata"]["name"])

        for kubecontext, ns, deployment in process(d, "deployments"):
            print(kubecontext, ns, deployment["metadata"]["name"])


def process(thedir, kind):
    """
    process takes a directory on disk, and a k8s kind, and makes a generator to emit
    tuples that have the kubecontext, namespace, and k8s resource
    """
    kubecontext = os.path.basename(os.path.normpath(thedir))
    print(kubecontext)
    filename = os.path.join(thedir, "{}.json".format(kind))
    print(filename)
    with open(filename) as json_file:
        items_wrapper = json.load(json_file)
        for item in items_wrapper["items"]:
            # could be None, this is OK
            ns = item.get("metadata").get("namespace")
            yield kubecontext, ns, item

if __name__ == '__main__':
    fire.Fire(handle_data)
