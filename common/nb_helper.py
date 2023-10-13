import pandas as pd
import os

#################### utils used to compile or run notebooks  ############


#################### utils used within notebooks ########################

# def show_done(txt='Completed'):
#     print(txt)

def make_sandbox(name='sandbox'):
    # make output location
    try:
        os.mkdir(name)
    except:
        print(f'{name} already exists')

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

def ID_header(title = '',line2 ='', subtitle = '',imagelink='',
              incl_links=True,link_up_level=False,
              show_source=True):

    data_banner()
    local_prefix = ''
    if link_up_level:
        local_prefix= '../'
        
    logo = """<a href="https://frackingchemicaldisclosure.wordpress.com/" title="Open-FF home page, tour and blog"><img src="https://storage.googleapis.com/open-ff-common/openFF_logo.png" alt="openFF logo" width="100" height="100"></a>"""
    logoFT = """<center><a href="https://www.fractracker.org/" title="FracTracker Alliance"><img src="https://storage.googleapis.com/open-ff-common/2021_FT_logo_icon.png" alt="FracTracker logo" width="100" height="100"><br>Sponsored by FracTracker Alliance</a></center>"""

    if show_source:
        source = f"""This file generated on {cat_creation_date:%B %d, %Y} from data repository: {repo_name}."""
    else:
        source = ''
    # cat_links = f"""<td width=20%>
    #                 <p style="text-align: center; font-size:120%"> 
    #                   <a href="{local_prefix}Open-FF_Catalog.html" title="Local Navigator"> Navigator Page </a>|
    #                   <a href="{local_prefix}Open-FF_Chemicals.html" title="OpenFF Chemical index"> Chemical Index </a>|
    #                   <a href="{local_prefix}Open-FF_States_and_Counties.html" title="OpenFF States index"> State Index </a>|
    #                   <a href="{local_prefix}Open-FF_Operator_Index.html" title="OpenFF Operator index"> Operator Index </a>
    #                   <a href="https://frackingchemicaldisclosure.wordpress.com/" title="Open-FF home page, tour and blog"> Open-FF Home </a><br>
    #                 </p>
    #                 </td>
    #             """
    cat_links = f"""<p style="text-align: center; font-size:100%"> Links: 
                      <a href="{local_prefix}Open-FF_Catalog.html" title="Local Navigator"> Navigator Page </a>|
                      <a href="{local_prefix}Open-FF_Chemicals.html" title="OpenFF Chemical index"> Chemical Index </a>|
                      <a href="{local_prefix}Open-FF_States_and_Counties.html" title="OpenFF States index"> State Index </a>|
                      <a href="{local_prefix}Open-FF_Operator_Index.html" title="OpenFF Operator index"> Operator Index </a>
                    </p>
                """
    #                       <a href="https://frackingchemicaldisclosure.wordpress.com/"> Blog </a><br>
    #                <p style="text-align: left; font-size:120%"> Links: </p>

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
                <td><p style="text-align: center; font-size:300%">{title}</p><br> {line2_alt} {subtitle_alt} {image_alt}
                    <p style="text-align: center; font-size:100%">{source}
                </td>
                <td width=15%>{logoFT}</td>
                </tr>
            </table><hr>"""
    display(HTML(table))

def displaySource():
    source = f"""This file generated on {cat_creation_date:%B %d, %Y} from data repository: {repo_name}."""
    display(HTML(source))

##################### collapsibles  #######################
def setup_collapsibles():
    display(HTML("""<style>
.collapsible {
  background-color: #777;
  color: white;
  cursor: pointer;
  padding: 18px;
  width: 80%;
  border: none;
  text-align: left;
  outline: none;
  font-size: 15px;
}

.active, .collapsible:hover {
  background-color: #555;
}

.content {
  padding: 0 18px;
  display: none;
  overflow: hidden;
  background-color: #f1f1f1;
}
</style>

"""))
    
def addCollapJS():
    display(HTML("""<script>
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}
</script>"""))
    
    
def insert_collapsible(displayed='Read More...', content='stuff'):
    display(HTML(f"""<button type="button" class="collapsible">{displayed}</button>
<div class="content">
  <p>{content}</p>
</div>
"""))
    addCollapJS()

# def show_mod_footer(filepath,repo=repo_name):
#     display(md(f"""The code for this webpage was last revised **{time.ctime(os.path.getmtime(filepath))}** and the data were compiled from the **{repo}** repository."""))
    