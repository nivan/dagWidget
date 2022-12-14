import ipywidgets as widgets
from traitlets import Unicode, Bool, HasTraits
from ._version import NPM_PACKAGE_RANGE
import json

# See js/lib/example.js for the frontend counterpart to this file.

@widgets.register
class DagWidgetController(widgets.DOMWidget):
    """An example widget."""

    # Name of the widget view class in front-end
    _view_name = Unicode('DagWidgetView').tag(sync=True)

    # Name of the widget model class in front-end
    _model_name = Unicode('DagWidgetModel').tag(sync=True)

    # Name of the front-end module containing widget view
    _view_module = Unicode('dagWidget').tag(sync=True)

    # Name of the front-end module containing widget model
    _model_module = Unicode('dagWidget').tag(sync=True)

    # Version of the front-end module containing widget view
    _view_module_version = Unicode('0.1.0').tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = Unicode('0.1.0').tag(sync=True)

    # Widget specific property.
    # Widget properties are defined as traitlets. Any property tagged with `sync=True`
    # is automatically synced to the frontend *any* time it changes in Python.
    # It is synced back to Python from the frontend *any* time the model is touched.        
    dag = Unicode('[]').tag(sync=True)
    attention_requests = Unicode('{}').tag(sync=True)
    summaries = Unicode('{}').tag(sync=True)

    def __init__(self):
        super().__init__()
        self._widgets = {}
        self._summaries = {}
        self._children = {}
        self._attRqs = {}

    def register_widget(self,widget,label,internal_id,reference_div_id,parents,summary_variables=['progress']):        
        #
        self._widgets[internal_id] = {'widget':widget,'referenceDiv':reference_div_id,'parents':parents,'label':label,'summaryVariables':summary_variables}
        #add to children list        
        if internal_id not in self._children:
            self._children[internal_id] = []
        #
        for pr in parents:    
            if pr not in self._children:
                self._children[pr] = []
            self._children[pr].append(internal_id)        
        #
        self.update_dag()

    def add_parent(self,widgetID,parentID):
        if (widgetID not in self._widgets) or (parentID not in self._widgets):
            print(f'ERROR: widget {widgetID} is registered {widgetID in self._widgets} widget {parentID} is registered {parentID in self._widgets}')
        else:
            self._widgets[widgetID]['parents'].append(parentID)
            self._children[parentID].append(widgetID)
            self.update_dag()

    def remove_parent(self,widgetID,parentID):
        if (widgetID not in self._widgets) or (parentID not in self._widgets):
            print('ERROR: node all nodes are registered')
        else:
            if parentID in self._widgets[widgetID]['parents']:
                self._widgets[widgetID]['parents'].remove(parentID)
            if widgetID in self._children[parentID]:
                self._children[parentID].remove(widgetID)
            self.update_dag()

    def _remove_node(self,_id):        
        if _id in self._widgets:            
            #children                    
            for key in self._widgets[_id]['parents']:
                index = self._children[key].index(_id)
                #it should be always >= 0                
                self._children[key].pop(index)                
            
            #widgets            
            while len(self._children[_id]) > 0:                
                self.remove_node(self._children[_id][0])
            #summaries
            if _id in self._summaries:
                self._summaries.pop(_id)
            if _id in self._children:
                self._children.pop(_id)
            self._widgets.pop(_id)

    def remove_node(self,_id):        
        self._remove_node(_id)        
        self.update_dag()

    def clear(self):
        self._widgets = {}
        self._summaries = {}
        self._children = {}  
        self._attRqs = {}
        #
        self.update_dag()

    def update_summary(self, internal_id, summaryValues):            
        self._summaries[internal_id] = summaryValues  
        self.summaries = json.dumps(self._summaries)          

    def request_attention(self, internal_id, entityType, eventType, description=""):                
        self.attention_requests = json.dumps({'op':'add','entityType':entityType,'widgetID':internal_id,'type':eventType,'description':description})
 
    def remove_request_attention(self, internal_id, entityType, eventType):
        self.attention_requests = json.dumps({'op':'remove','entityType':entityType,'widgetID':internal_id,'type':eventType})        

    def update_dag(self):
        obj = []        
        summaryVariables = {}
        for _id in self._widgets:
            obj.append({'id':_id,'divID':self._widgets[_id]['referenceDiv'],'label':self._widgets[_id]['label'],'parentIds':self._widgets[_id]['parents']})
            summaryVariables[_id] = self._widgets[_id]['summaryVariables']

        #
        self.dag = json.dumps({'dag':obj,'summaries':self._summaries,'summaryVariables':summaryVariables})