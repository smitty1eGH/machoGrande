import os
from   pathlib           import Path
import shutil
import subprocess

from   cookiecutter.main import cookiecutter
from   yaml              import load,Loader

#WARNING: Do not run machoGrande within a virtual
#  environment. Pipenv cannot get over machoGrande
#  running in a venv.
#Just duplicate a session and CD to machoGrande and go

#Assert: virtualenvmanager     installed
#        WORKON_HOME           defined
#        cookiecutter          installed
#        cookiecutter template configured locally
#        inputs entered        via CONFIG_SPEC

ROOT_PATH=os.environ['WORKON_HOME']
TEMPLATE_PATH='/home/osboxes/proj/machoGrande/machoGrande/ccs/'
DEFAULT_CUTTER='cookiecutter-pybase/'

#TODO: get rid of JSON config_spec. Load YAML to obtain PROJ_NAME,
#  then co[y to TEMPLATE_PATH as cookiecutter.yaml.
CONFIG_SPEC=ROOT_PATH + '/machoGrande/machoGrande/machoGrande.yaml'
config={}
with open(CONFIG_SPEC,'r') as f:
    config=load(f.read(),Loader=Loader)
proj_name=config['project_slug']

def adjust_location():
    '''Pipenv's design, while making great sense,
         is not what we prefer. After moving the
         venv to the desired location, eliminate
         the random characters at the end of the
         project path in the various management
         files.
    '''
    fs=['/bin/activate'
       ,'/bin/activate.csh'
       ,'/bin/activate.fish'
       ,'/bin/easy_install'
       ,'/bin/easy_install-3.6'
       ,'/bin/pip'
       ,'/bin/pip3'
       ,'/bin/pip3.6'
       ,'/bin/python-config'
       ,'/bin/wheel'
       ]

    len_pdir=len(str(projdir))
    naughty_chars=str(realdir)[len_pdir:]

    for f in fs:
        with open('%s%s' % (projdir,f),'r') as infile:
            lines=infile.readlines()
        with open('%s%s' % (projdir,f),'w') as outfile:
            for line in lines:
                if line.find(naughty_chars,len_pdir):
                    outfile.write(line.replace(naughty_chars,''))
                else:
                    outfile.write(line)


#Make the virtual envrionment, which arrives in a
#  sort of parallel universe, which we will then inhabit.
projdir=Path(ROOT_PATH,proj_name)
os.mkdir(projdir) #placebo
subprocess.run(['pipenv','--three'],cwd=projdir)

#Globbing returns a generator, we know it's a 1-element
#  comprehension; grab the first element #FTW
realdir=[p for p in Path(ROOT_PATH).glob('%s-*' % proj_name)][0]
print(' the realdir is %s' % realdir)

#Move the Pipfile to realdir; rmdir projdir, rename realdir to projdir
shutil.move('%s/Pipfile' % projdir, realdir)
os.rmdir(projdir)
shutil.move(realdir, projdir)
adjust_location()


#Overwrite the cookiecutter inputs with the machoGrande.yml,
#  then initialize the project.
#TODO: Push JSON to TEMPLATE_PATH instead
#shutil.copy(CONFIG_SPEC,TEMPLATE_PATH)
#import pdb; pdb.set_trace()
cookiecutter(TEMPLATE_PATH+DEFAULT_CUTTER,checkout=None,no_input=True
            ,extra_context=None,replay=False,overwrite_if_exists=True
            ,output_dir=ROOT_PATH)

##Invoke git, and do the first commit.
#subprocess.run(['git','init'      ],cwd=projdir)
#subprocess.run(['git','add'   ,'.'],cwd=projdir)
#subprocess.run(['git','commit','-a'
               #,'-m' ,'Over Macho Grande?'],cwd=projdir)
