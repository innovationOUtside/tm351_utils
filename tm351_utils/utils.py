

#Run this cell to create the table_def() function to generate tidy output from pg_dump
#You don't need to know how the Linux command line voodoo works...
def table_def(table,db='tm351test', retval=False, noprint=False):
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
from IPython.core.display import HTML
import difflib
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