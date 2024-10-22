import re

with open('db/start.sql', 'r') as f:
    sql = ' '.join([line[:line.find('--')] for line in f.readlines()])

result = 'from dataclasses import dataclass\nfrom db.objects import DBObject\n'

for table in re.finditer('CREATE TABLE IF NOT EXISTS ([a-zA-Z_]*)\(([^;]*)\);', sql):
    table_name = table.group(1)
    result += f'\n@dataclass\nclass {table_name}(DBObject):\n'
    table_content = table.group(2)
    for field in re.finditer('(,|\() *([a-zA-Z_]*)', table_content):
        field_name = field.group(2)
        result += f'\t{field_name} = None\n'

with open('db/types.py', 'w') as f:
    f.write(result)