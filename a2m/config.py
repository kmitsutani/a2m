import json
from pathlib import Path
from yaml import load, dump
from a2m.processes.buildin import alias_to_processor
from a2m.inputs import Feed, category_names
from a2m.outputs import method_dict as omethod_dict

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def parse_config(config_path, debug=False):
    with config_path.expanduser().open('r') as fin:
        config = load(fin, Loader=Loader)
    inputs = parse_inputs(config['inputs'])
    processes = parse_processes(config['processes'], inputs)
    outputs = parse_outputs(config['outputs'])
    return dict(
        inputs=inputs,
        processes=processes,
        outputs=outputs,
    )

def parse_inputs(inputs_config):
    inputs = list()
    for elm in inputs_config:
        if isinstance(elm, str):
            label = category = elm
            if category not in category_names:
                raise
            inputs.append(Feed(label, category))
        elif isinstance(elm, dict):
            for k, v in elm.items():
                if v not in category_names:
                    raise
                inputs.append(Feed(k, v))
    return inputs

def parse_processes(config, inputs):
    labels = [x.label for x in inputs]
    processes = list()
    for proc_info in config:
        proc_label = list(proc_info.keys())[0]
        proc_config = proc_info[proc_label]
        if proc_label in alias_to_processor:
            processes.append(
                alias_to_processor[proc_label](proc_config, labels)
            )
        else:
            raise Exception(f"unkwnon process {proc_label}")
    return processes

def parse_outputs(outputs_config):
    outputs = list()
    for method, method_config in outputs_config.items():
        outputs.append(omethod_dict[method](**method_config))
    return outputs
