import pandas as pd
import os
import subprocess

import openFF.common.handles as hndl

#################### utils used within notebooks ########################

def make_sandbox(dirname=hndl.sandbox_dir):
    # make output location
    try:
        os.mkdir(dirname)
    except:
        print(f'{dirname} already exists')

def add_favicon(fn):
    # also adds favicon to browser tab
    with open(fn,'r',encoding='utf-8') as f:
        alltext = f.read()
    alltext  = alltext.replace('</title>',
                               '</title>\n<link rel="icon" href="https://storage.googleapis.com/open-ff-common/favicon.ico">',1)
    with open(fn,'w',encoding='utf-8') as f:
        f.write(alltext)

def hide_map_warning(fn):
    # also adds favicon to browser tab
    with open(fn,'r',encoding='utf-8') as f:
        alltext = f.read()
    text = """<div class="jp-OutputArea-child">

<div class="jp-RenderedText jp-OutputArea-output" data-mime-type="application/vnd.jupyter.stderr">
<pre>WARNING:fiona.ogrext:Skipping field geo_point_2d: invalid type 3
</pre>
</div>
</div>"""
    alltext  = alltext.replace(text,'')
    with open(fn,'w',encoding='utf-8') as f:
        f.write(alltext)

def fix_nb_title(fn,new_title):
    """used to change the name that goes into browser tabs into something more useful than
    the filename (which needs to stay unchanged because of backwards compatibility to existing
    links).  Also add favicon."""
    old_title = os.path.basename(fn)[:-5] # drop the .html
    with open(fn,'r',encoding='utf-8') as f:
        alltext = f.read()
    alltext  = alltext.replace(f'<title>{old_title}</title>',
                                f'<title>{new_title}</title>\n<link rel="icon" href="https://storage.googleapis.com/open-ff-common/favicon.ico">',1)
    with open(fn,'w',encoding='utf-8') as f:
        f.write(alltext)


def make_notebook_output(nb_fn,output_fn, basic_output=False):
    res = os.path.split(output_fn)
    out_dir = res[0]
    out_fn = res[1] 
    assert out_fn[-5:]=='.html', f'Expecting .html ext on {output_fn}'
    b_text = ''
    if basic_output:
        b_text = ' --template=basic '
    s= f'jupyter nbconvert --no-input {b_text}--ExecutePreprocessor.allow_errors=True --ExecutePreprocessor.timeout=-1 --execute {nb_fn} --to=html --output="{out_fn[:-5]}" --output-dir="{out_dir}"'
    subprocess.run(s)
    hide_map_warning(output_fn)


def get_common_header(title = '',line2 ='', subtitle = '',imagelink='',
              incl_links=True,link_up_level=0,repo_name='',cat_creation_date='',
              show_source=True,use_remote=False):
    #print(f'{cat_creation_date:%B %d, %Y}')
    local_prefix = ''
    if link_up_level>0:
        for i in range(link_up_level):
            local_prefix+= '../'
    if use_remote:
        local_prefix = hndl.browser_root
        
    logo = """<center><a href="https://frackingchemicaldisclosure.wordpress.com/" title="Open-FF home page, tour and blog"><img src="https://storage.googleapis.com/open-ff-common/openFF_logo.png" alt="openFF logo" width="100" height="100"><h2>Open-FF</h2></a></center>"""
    logoFT = """<center><a href="https://www.fractracker.org/" title="FracTracker Alliance"><img src="https://storage.googleapis.com/open-ff-common/2021_FT_logo_icon.png" alt="FracTracker logo" width="100" height="100"><br><h4>Sponsored by FracTracker Alliance</h4></a></center>"""

    if show_source:
        source = f"""This file was generated on {cat_creation_date:%B %d, %Y} <br>from data repository: {repo_name}."""
    else:
        source = ''

    cat_links = f"""<p style="text-align: center; font-size:100%"> Links: 
                      <a href="{local_prefix}Open-FF_Catalog.html" title="Local Navigator"> Navigator Page </a>|
                      <a href="{local_prefix}Open-FF_Chemicals.html" title="OpenFF Chemical index"> Chemical Index </a>|
                      <a href="{local_prefix}Open-FF_States_and_Counties.html" title="OpenFF States index"> State Index </a>|
                      <a href="{local_prefix}Open-FF_Operator_Index.html" title="OpenFF Operator index"> Operator Index </a>
                    </p>
                """

    if incl_links: cat_txt = cat_links
    else: cat_txt = ''
    line2_alt = ''
    if line2:
        line2_alt = f'<p style="text-align: center; font-size:250%">{line2}</p><br>'
    subtitle_alt = ''
    if subtitle:
        subtitle_alt = f'<p style="text-align: center; font-size:180%">{subtitle}</p>'
    image_alt = ''
    if imagelink:
        image_alt = f'<center>{imagelink}</center>'
    
    table = f"""<style>
                </style>{cat_txt}<hr>
                <table style='margin: 0 auto' >
                <tr>
                <td width=15%>{logo}</td>
                <td><p style="text-align: center; font-size:300%">{title}</p><br> 
                    {line2_alt} 
                    {subtitle_alt} 
                    {image_alt}
                    <p style="text-align: center; font-size:100%">{source}
                </td>
                <td width=15%>{logoFT}</td>
                </tr>
            </table><hr>"""
    return table


def compile_std_page(fn,nb_title='empty title',
                     headtext=[],
                     bodytext=[],
                     incFavIcon=True,des_content=None, use_std_css_and_scripts=True):
    """Use this to create a standard browser webpage based on a template and sections passed here. 
    The optional additions are:
        - favicon
        - a meta tag with a file description for seo
    Currently, this is just used for a disclosure report.
        """
    # with open(fn,'r',encoding='utf-8') as f:
    #     inputtext = f.read()

    # standard css and scripts
    css_js = ''
    if use_std_css_and_scripts:
        css_js = """<link href="https://cdn.datatables.net/v/dt/jq-3.7.0/dt-1.13.7/b-2.4.2/b-colvis-2.4.2/datatables.min.css" rel="stylesheet">
                <script src="https://cdn.datatables.net/v/dt/jq-3.7.0/dt-1.13.7/b-2.4.2/b-colvis-2.4.2/datatables.min.js"></script>
                """       
        # """  <link href="https://cdn.datatables.net/v/dt/jq-3.7.0/dt-1.13.7/fh-3.4.0/datatables.min.css" rel="stylesheet">
        # <script src="https://cdn.datatables.net/v/dt/jq-3.7.0/dt-1.13.7/fh-3.4.0/datatables.min.js"></script>
        # """
    # favicon setting
    favicon = ''
    if incFavIcon: # goes in head
        favicon = '<link rel="icon" href="https://storage.googleapis.com/open-ff-common/favicon.ico">'

    # file description
    des_cont = ''
    if des_content:
        des_cont = f'<meta name="description" content="{des_content}">'
    

    s = f"""<!DOCTYPE html>
    <html lang="en">
        <head>
            
            <title>{nb_title}</title>
            {favicon}
            {des_cont}
            {css_js}
    """
    s += """<style>
            * {
                font-family: sans-serif;
            }
            </style>
            """
    for item in headtext:
        s+= f'    {item}\n'

    s+= """</head>
    <body>
    """
    for item in bodytext:
        s+= f'    {item}\n'

    s+= """</body>
    </html>
    """
    with open(fn,'w',encoding='utf-8') as f:
        f.write(s)
    
def compile_nb_page(fn,nb_title='empty title',header='',incFavIcon=True,incBootStrap=True,des_content=None):
    """Use this to transform the output of a jupyter nbconvert (template=basic) to a more complete webpage - typically
    for the browser pages. With the basic template, no head or body tags are included, 
    so this provides that and situates various code sections
    in their proper location. The process is done in-place. 
    The optional additions are:
        - favicon
        - bootstrap styling
        - a meta tag with a file description for seo
        """
    with open(fn,'r',encoding='utf-8') as f:
        inputtext = f.read()

    # favicon setting
    favicon = ''
    if incFavIcon: # goes in head
        favicon = '<link rel="icon" href="https://storage.googleapis.com/open-ff-common/favicon.ico">'

    # bootstrap settings
    bscss = ''
    bsscript = ''
    if incBootStrap:
        bscss = """            <!-- Required meta tags -->
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">

            <!-- Bootstrap CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
             """
        bsscript = """        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous"></script>
                """

    # file description
    des_cont = ''
    if des_content:
        des_cont = f'<meta name="description" content="{des_content}">'

    s = f"""<!DOCTYPE html>
    <html lang="en">
        <head>
            {bscss}
            
            <title>{nb_title}</title>
            {favicon}
            {des_cont}
            {header}
    </head>
    <body>
        {inputtext}
        {bsscript}
    </body>
    </html>
    """
    with open(fn,'w',encoding='utf-8') as f:
        f.write(s)


def clr_cell(txt='Cell Completed', color = '#669999'):
    import datetime    
    from IPython.display import display
    from IPython.display import Markdown as md

    t = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    s = f"""<div style="background-color: {color}; padding: 10px; border: 1px solid green;">"""
    s+= f'<h3> {txt} </h3> {t}'
    s+= "</div>"
    display(md(s))

def completed(status=True,txt=''):
    if txt =='':
        if status:
            txt = 'This step completed normally.'
        else:
            txt ='Problems encountered in this cell! Resolve before continuing.' 
    if status:
        clr_cell(txt)
    else:
        clr_cell(txt,color='#ff6666')


def displaySource():
    source = f"""This file generated on {cat_creation_date:%B %d, %Y} from data repository: {repo_name}."""
    display(HTML(source))

##################### collapsibles  #######################
# def setup_collapsibles():
#     display(HTML("""<style>
# .collapsible {
#   background-color: #777;
#   color: white;
#   cursor: pointer;
#   padding: 18px;
#   width: 80%;
#   border: none;
#   text-align: left;
#   outline: none;
#   font-size: 15px;
# }

# .active, .collapsible:hover {
#   background-color: #555;
# }

# .content {
#   padding: 0 18px;
#   display: none;
#   overflow: hidden;
#   background-color: #f1f1f1;
# }
# </style>

# """))
    
# def addCollapJS():
#     display(HTML("""<script>
# var coll = document.getElementsByClassName("collapsible");
# var i;

# for (i = 0; i < coll.length; i++) {
#   coll[i].addEventListener("click", function() {
#     this.classList.toggle("active");
#     var content = this.nextElementSibling;
#     if (content.style.display === "block") {
#       content.style.display = "none";
#     } else {
#       content.style.display = "block";
#     }
#   });
# }
# </script>"""))
    
    
# def insert_collapsible(displayed='Read More...', content='stuff'):
#     display(HTML(f"""<button type="button" class="collapsible">{displayed}</button>
# <div class="content">
#   <p>{content}</p>
# </div>
# """))
#     addCollapJS()

# # def show_mod_footer(filepath,repo=repo_name):
# #     display(md(f"""The code for this webpage was last revised **{time.ctime(os.path.getmtime(filepath))}** and the data were compiled from the **{repo}** repository."""))
    