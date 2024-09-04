import jinja2
import yaml
import os

def renderiza_template():
    with open('redshift.yml.j2','r') as f:
        readshift_yml = f.read()

    with open('config.yaml','r') as f:
        config = yaml.safe_load(f)

    redshift_template = jinja2.Template(redshift_yml)
    rendshift_rendered = redshift_template.render({**config,**os.environ})

    with open('redshift.yml', r) as f:
        f.write(rendshift_rendered)

renderiza_template()