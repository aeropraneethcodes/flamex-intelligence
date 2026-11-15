"""Non-browser mocked Streamlit rendering smoke: exercises branch/Plotly compatibility.
This DOES NOT replace real browser testing with Streamlit installed.
"""
import os,sys,runpy,types
from pathlib import Path
PROJECT=Path(__file__).resolve().parents[1]
os.chdir(PROJECT)

class Dummy(types.ModuleType):
    page='Mission overview'
    session_state={}
    secrets={}
    def __init__(self):
        super().__init__('streamlit')
        self.sidebar=self
        self.column_config=types.SimpleNamespace(NumberColumn=lambda *a,**k:None,LinkColumn=lambda *a,**k:None)
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def cache_data(self,*a,**k):return lambda f:f
    def set_page_config(self,**kw):pass
    def markdown(self,*a,**k):pass
    def caption(self,*a,**k):pass
    def write(self,*a,**k):pass
    def subheader(self,*a,**k):pass
    def divider(self,*a,**k):pass
    def data_editor(self,frame,*a,**k):return frame
    def dataframe(self,*a,**k):pass
    def plotly_chart(self,fig,*a,**k):fig.to_plotly_json()
    def expander(self,*a,**k):return self
    def spinner(self,*a,**k):return self
    def chat_message(self,*a,**k):return self
    def columns(self,n,*a,**k):return [self]*int(n)
    def button(self,*a,**k):return False
    def download_button(self,*a,**k):return False
    def text_input(self,*a,**k):return ''
    def chat_input(self,*a,**k):return None
    def file_uploader(self,*a,**k):return None
    def radio(self,*a,**k):return self.page
    def multiselect(self,label,options,default=None,**k):return default if default is not None else list(options)
    def selectbox(self,label,options,index=0,**k):return options[index]
    def number_input(self,*a,**k):return k.get('value',0)
    def slider(self,*a,**k):return k.get('value',a[3] if len(a)>3 else a[2] if len(a)>2 else 0)
    def metric(self,*a,**k):pass
    def warning(self,*a,**k):pass
    def error(self,msg,*a,**k):raise RuntimeError(msg)
    def info(self,*a,**k):pass
    def code(self,*a,**k):pass
    def toggle(self,*a,**k):return False
    def rerun(self):pass

fake=Dummy();sys.modules['streamlit']=fake
PAGES=['Mission overview','Investigation explorer','Combustion explorer','Fuel comparison lab','Stability & uncertainty',
       'Predictive intelligence','Artemis scenario explorer','FlameIQ research assistant','Research brief & sources']
for page in PAGES:
    fake.page=page
    try:
        runpy.run_path(str(PROJECT/'app.py'),run_name='__main__')
        print('PASS',page)
    except Exception as ex:
        print('FAIL',page,type(ex).__name__,str(ex))
        raise
