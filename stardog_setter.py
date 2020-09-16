import fire
import requests
import os
import re
from stardog_loader import process as loader_process
import json
from os import path

INVALID_CHAR_REGEX = r"('|,|\.|\[|\]|\*)"
FAILED = []

def delete_then_put(item, ctx, ns, kind, astra_proxy_url):
    # Delete it if it's already there
    try:
        name = f'{ctx}-{ns or ""}-{item["metadata"]["name"]}'
        resp = requests.delete(astra_proxy_url + f'/api/rest/v2/namespaces/stardog/collections/{kind}/{name}')
        first_time_putting = resp.status_code == 500 and resp.text == f'table stardog.{kind} does not exist'  
        delete_fail = False
        if resp.status_code != 204 and not first_time_putting:
            delete_fail = True
            print(f'Delete failed: {resp.text} {resp.status_code}')
            return False

        resp = requests.put(astra_proxy_url + f'/api/rest/v2/namespaces/stardog/collections/{kind}/{name}', json=item)
        if resp.status_code != 200:
            print(f'Put failed: {resp.text} {resp.status_code} {item}')
            return False
    except KeyError as e:
        raise RuntimeError(f'The key {e} was not found in {item}')
    
    print(f'Successfully put the data for {kind[:-1]} {name}')
    return True

def sub_bad_chars(data):
    if isinstance(data, dict):
        return {re.sub(INVALID_CHAR_REGEX, '_', k): sub_bad_chars(v) for (k, v) in data.items()}
    else:
        return data


KINDS = ["namespaces", "pods", "deployments"]
DONEFILE = "dirsdone.json"


def process(stardog_data_dir, astra_proxy_url):
    done = []
    if path.exists(DONEFILE):
        with open(DONEFILE) as json_file:
            done = json.load(json_file)
    fails = []
    for directory in os.listdir(stardog_data_dir):
        if directory.startswith('.'):
            continue
        if directory in done:
            print(f"already completed: {directory}")
            continue
        for kind in KINDS:
            for (ctx, namespace, data) in loader_process(os.path.join(stardog_data_dir, directory), kind):
                success = delete_then_put(sub_bad_chars(data), ctx, namespace, kind, astra_proxy_url)
                if not success:
                    fails.append((ctx, namespace, kind, data['metadata']['name']))
        done.append(directory)
        with open(DONEFILE, "w") as json_file:
            json.dump(done, json_file)

    print(f"The following {len(fails)} items failed: {fails}")

if __name__ == '__main__':
    fire.Fire(process)
