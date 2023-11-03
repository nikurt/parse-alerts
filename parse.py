import sys

def add_object(obj, k, v):
    if not k in obj:
        obj[k] = []
    obj[k].append(v)

def parse_rule(lines):
    indent = 0
    stack = [(None,{})]
    i = 0
    while i < len(lines):
        l = lines[i]
        print(i,len(stack),l)
        parts = [part for part in l.split(' = ', maxsplit = 1)]
        if len(parts) == 2:
            if parts[1] == '{':
                stack.append((parts[0].strip(), {}))
                indent += 2
            elif parts[1] == 'jsonencode({':
                stack.append((parts[0].strip(), {}))
                indent += 2
            elif parts[1] == '[{':
                i += 1
                while lines[i].strip() != '}]':
                    i += 1
            else:
                stack[-1][1][parts[0].strip()] = parts[1].strip()
        elif len(parts) == 1 and parts[0].strip() == '}' and parts[0].find('}') == indent:
            assert len(stack) > 1
            add_object(stack[-2][1], stack[-1][0], stack[-1][1])
            stack = stack[:-1]
            indent -= 2
        elif len(parts) == 1 and parts[0].strip() == '})' and parts[0].find('})') == indent:
            assert len(stack) > 1
            add_object(stack[-2][1], stack[-1][0], stack[-1][1])
            stack = stack[:-1]
            indent -= 2
        else:
            parts = [part for part in l.split() if part]
            assert len(parts) == 2
            if parts[1] == '{':
                stack.append((parts[0].strip(), {}))
                indent += 2
            else:
                assert False
        i += 1
    assert len(stack) == 1
    return stack[0][1]


def get_resource(lines):
    while lines and not lines[0]:
        lines = lines[1:]

    if not lines:
        return None,None

    parts = lines[0].split()
    assert parts[0] == "resource"
    group = parts[1]
    name = parts[2]
    assert parts[3] == '{'
    closing = 0
    while lines[closing] != "}":
        # print(lines[closing])
        closing += 1

    resource = parse_rule(lines[1:closing])
    resource['group'] = group
    resource['name'] = name

    return resource, lines[closing+1:]



def parse_terraform_file(file_path):
  resources = []
  with open(file_path, 'r') as file:
      lines = []
      for l in file:
          lines.append(l[:-1])

  while True:
    resource, rest = get_resource(lines)
    if resource is None:
      break
    resources.append(resource)
    lines = rest

  return resources

resources = parse_terraform_file(sys.argv[1])
for r in resources:
    print(r['group'],r['name'],r['folder_uid'])
    for rule in r['rule']:
        print(rule['name'],rule['no_data_state'],rule['exec_err_state'])
    for annotations in rule['annotations']:
        print(annotations['__dashboardUid__'],annotations['__panelId__'],annotations.get('message'))
    for labels in rule['labels']:
        print(labels['pagerduty'],labels.get('severity'))
    for data in rule['data']:
        print(data.get('ref_id'), data.get('model'))
        for model in data.get('model'):
            print(model.get('expression'),model.get('reducer'))
