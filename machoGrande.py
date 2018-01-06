import os
from   pathlib           import Path
import shutil
import subprocess

from   cookiecutter.main import cookiecutter
from   yaml              import load,Loader

#WARNING: Do not run machoGrande within a virtual
#  environment. Pipenv cannot get over machoGrande
#  running in a venv.
#TODO: detect venv and bomb out if in one.
#Just duplicate a session and CD to machoGrande and go

#Assert: virtualenvmanager     installed
#        WORKON_HOME           defined
#        cookiecutter          installed
#        cookiecutter template configured locally
#        inputs entered        via CONFIG_SPEC

ROOT_PATH     =os.environ['WORKON_HOME']
TEMPLATE_PATH =ROOT_PATH + 'machoGrande/machoGrande/ccs/'
DEFAULT_CUTTER='cookiecutter-pybase/'
CONFIG_SPEC   =ROOT_PATH + '/machoGrande/machoGrande/machoGrande.json'

def step_zero_obtain_project_name():
    '''Peek at machoGrande.json for the name of the project.
    '''
    config        ={}
    with open(CONFIG_SPEC,'r') as f:
        config=load(f.read(),Loader=Loader)
    return config['project_slug']

def step_one_create_project_directory():
    '''Here we go to our WORKON_HOME location and make the
       project directory.
       TODO: test for its existence, and either bomb out or
         blow away the directory, optionally tarballing it
         if desired.
       Here we're going to browbeat pipenv and return the
         directory it *actually* created.
    '''
    projdir=Path(ROOT_PATH,proj_name)
    os.mkdir(projdir) #placebo
    subprocess.run(['pipenv','--three'],cwd=projdir)

    #Globbing returns a generator, we know it's a 1-element
    #  comprehension; grab the first element #FTW
    realdir=[p for p in Path(ROOT_PATH).glob('%s-*' % proj_name)][0]
    return realdir

def step_two_adjust_project_location(realdir):
    '''Move the Pipfile to realdir; rmdir projdir, rename
       realdir to projdir
       Pipenv's design, while making great sense,
         is not what we prefer. After moving the
         venv to the desired location, eliminate
         the random characters at the end of the
         project path in the various management
         files.
    '''
    fs=['/bin/activate'         ,'/bin/activate.csh'
       ,'/bin/activate.fish'    ,'/bin/easy_install'
       ,'/bin/easy_install-3.6' ,'/bin/pip'
       ,'/bin/pip3'             ,'/bin/pip3.6'
       ,'/bin/python-config'    ,'/bin/wheel'
       ]
    shutil.move('%s/Pipfile' % projdir, realdir)
    os.rmdir(projdir)
    shutil.move(realdir, projdir)

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

def step_three_invoke_cookiecutter():
    '''Overwrite the cookiecutter inputs with the
         machoGrande.json, then initialize the project.
       Let's admit that this approach understands cookiecutter
         about as well as it understands pipenv
    '''
    shutil.copy(CONFIG_SPEC
               ,TEMPLATE_PATH+DEFAULT_CUTTER+'cookiecutter.json')
    cookiecutter(TEMPLATE_PATH+DEFAULT_CUTTER
                ,checkout=None,no_input=True
                ,extra_context=None,replay=False
                ,overwrite_if_exists=True
                ,output_dir=ROOT_PATH)

def step_four_gittify_project():
    '''Invoke git, and do the first commit.
    '''
    subprocess.run(['git','init'      ],cwd=projdir)
    subprocess.run(['git','add'   ,'.'],cwd=projdir)
    subprocess.run(['git','commit','-a'
                   ,'-m' ,'Over Macho Grande?'],cwd=projdir)

if __name__=='__main__':
    proj_name=step_zero_obtain_project_name()
    real_dir =step_one_create_project_directory(proj_name)
    step_two_adjust_project_location(real_dir)
    step_three_invoke_cookiecutter()
    step_four_gittify_project()
    #TODO
    #setp_six_push_to_github
