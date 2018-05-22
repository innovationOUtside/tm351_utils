import subprocess
from IPython.core.display import HTML
import difflib


#Run this cell to create the table_def() function to generate tidy output from pg_dump
#You don't need to know how the Linux command line voodoo works...
def table_def(table,db='tm351', retval=False, noprint=False):
    ''' Helper function defined to display a tidied up version 
        of the table creation statements
        created using pg_dump '''
    
    #The sed commands remove extraneous lines; the cat -s command removes doubled up blank lines
    #Escape the quotes surrounding the table name so we can quote tables with eg underscores in name
    tables = [table] if not isinstance(table, list) else table
    tables = ''.join([' -t \"{}\" '.format(t) for t in tables ] )
    #https://stackoverflow.com/a/7353141/454773
    task = subprocess.Popen("pg_dump -s {} {} | sed  -e '/ *SET .*;/ d' | sed  -e '/-- Dumped .*/ d' | cat -s".format(tables,db), shell=True, stdout=subprocess.PIPE)
    txt,err = task.communicate()
    if not noprint: print(txt.decode('utf-8'))
    if retval or noprint: return txt.decode('utf-8')

#Alternative one liner as a shell command
#!pg_dump -s -t $table $db | sed  -e '/ *SET .*;/ d' | sed  -e '/-- Dumped .*/ d' | sed '/^$/{N;/^\n$/d;}'






#Diff two text strings and generate some coloured HTML to show the diffs

#https://github.com/dsindex/blog/wiki/%5Bpython%5D-difflib,-show-differences-between-two-strings
def show_diff(text, n_text, retval=False):
    """
    Display the difference between two strings.
    http://stackoverflow.com/a/788780
    Unify operations between two compared strings seqm is a difflib.
    SequenceMatcher instance whose a & b are strings
    """
    seqm = difflib.SequenceMatcher(None, text, n_text)
    output= []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append(seqm.a[a0:a1])
        elif opcode == 'insert':
            output.append("<font color=red>^" + seqm.b[b0:b1] + "</font>")
        elif opcode == 'delete':
            output.append("<font color=blue>^" + seqm.a[a0:a1] + "</font>")
        elif opcode == 'replace':
            # seqm.a[a0:a1] -> seqm.b[b0:b1]
            output.append("<font color=green>^" + seqm.b[b0:b1] + "</font>")
        output.append('<br/>')
    txt=''.join(output)
    
    if retval: return txt
    return HTML('<pre>'+txt+'</pre>')
    
    
#Merge notebooks
#https://stackoverflow.com/a/3207973/454773
from nbformat.v4 import new_notebook, new_markdown_cell
import nbformat
import io
import os
import subprocess
import random
import string

#from PyPDF2 import PdfFileMerger, PdfFileReader

def merged_notebooks_in_dir(dirpath,filenames=None):
    ''' Merge all notebooks in a directory into a single notebook '''
    
    if filenames is None: filenames=os.listdir(dirpath)
    
    fns = ['{}/{}'.format(dirpath, fn) for fn in filenames if '.ipynb_checkpoints' not in dirpath and fn.endswith('.ipynb')]
    if fns:
        merged = new_notebook()
        #Identify directory containing merged notebooks
        cell = '\n\n---\n\n# {}\n\n---\n\n'.format(dirpath)
        merged.cells.append(new_markdown_cell(cell))
    else: return
    
    for fn in fns:
        #print(fn)
        notebook_name = fn.split('/')[-1]
        with io.open(fn, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
            #Identify filename of notebook
            cell = '\n\n---\n\n# {}\n\n---\n\n'.format(fn)
            merged.cells.append(new_markdown_cell(cell))
            merged.cells.extend(nb.cells)
            
    if not hasattr(merged.metadata, 'name'):
        merged.metadata.name = ''
        
    merged.metadata.name += "_merged"
    return nbformat.writes(merged)


def merged_notebooks_down_path(path, typ='docx', execute=False):
    ''' Walk a path, creating an output file in each directory that merges all notebooks in the directory  '''
    for (dirpath, dirnames, filenames) in os.walk(path):
        if '.ipynb_checkpoints' in dirpath: continue
        
        #Should we run the execute processor here on each notebook separately,
        # ensuring that images are embedded, and then merge the executed notebook files? 
        merged_nb = merged_notebooks_in_dir(dirpath,filenames)
        if not merged_nb: continue
        
        fn=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        suffix = 'ipynb' if typ=='ipynb' else 'ipynbx'
        fpn = '{}/{}.{}'.format(dirpath,fn, suffix)
        with open(fpn, 'w') as f:
            f.write(merged_nb)
        
        # Execute the merged notebook in its directory so that images are correctly handled
        # Using html_embed seems to cause pandoc to fall over?
        # The pdf conversion requires installation of texlive-xetex and inkscape
        # This adds significant weight to the VM: maybe we need an MT/prouction VM and a student build?
        # Inline code execution generated using python-markdown extension seems to break PDF generation
        #  at the first instance of inline code? Need to add a preprocessor?
        # We could maybe process the notebook inline rather than via the commandline
        # In such a case, the following may be a useful reference:
        #https://github.com/ipython-contrib/jupyter_contrib_nbextensions/blob/master/docs/source/exporting.rst
        execute = '  --ExecutePreprocessor.timeout=600 --ExecutePreprocessor.allow_errors=True --execute' if execute else ''
        if typ=='pdf':
            cmd='jupyter nbconvert --to pdf {exe} "{fn}".ipynbx'.format(exe=execute, fn=fn)
            subprocess.check_call(cmd, shell=True, cwd=dirpath)
        elif typ in ['docx']:
            cmd='jupyter nbconvert --to html {exe} "{fn}".ipynbx'.format(exe=execute, fn=fn)
            subprocess.check_call(cmd, shell=True, cwd=dirpath)
            cmd='pandoc -s "{fn_out}".html -o _merged_notebooks.{typ}'.format(fn_out=fn, typ=typ)
            subprocess.check_call(cmd, shell=True, cwd=dirpath)
            os.remove("{}/{}.html".format(dirpath,fn))
        if typ!='ipynb':
            os.remove(fpn)
