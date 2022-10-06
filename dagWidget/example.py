import ipywidgets as widgets
from traitlets import Unicode, Bool, HasTraits
from ._version import NPM_PACKAGE_RANGE
import json

# See js/lib/example.js for the frontend counterpart to this file.

@widgets.register
class HelloWorld(widgets.DOMWidget):
    """An example widget."""

    # Name of the widget view class in front-end
    _view_name = Unicode('HelloView').tag(sync=True)

    # Name of the widget model class in front-end
    _model_name = Unicode('HelloModel').tag(sync=True)

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
    attentionRequests = Unicode('{}').tag(sync=True)
    summaries = Unicode('{}').tag(sync=True)

    def __init__(self):
        super().__init__()
        self._widgets = {}
        self._summaries = {}
        self._children = {}
        self._attRqs = {}

    def registerWidget(self,widget,label,internalID,referenceDivID,parents,summaryVariables=['progress']):        
        #
        self._widgets[internalID] = {'widget':widget,'referenceDiv':referenceDivID,'parents':parents,'label':label,'summaryVariables':summaryVariables}
        #add to children list        
        if internalID not in self._children:
            self._children[internalID] = []
        #
        for pr in parents:    
            if pr not in self._children:
                self._children[pr] = []
            self._children[pr].append(internalID)        
        #
        self.updateDag()

    def addParent(self,widgetID,parentID):
        if (widgetID not in self._widgets) or (parentID not in self._widgets):
            print('ERROR: node all nodes are registered')
        else:
            self._widgets[widgetID]['parents'].append(parentID)
            self._children[parentID].append(widgetID)
            self.updateDag()

    def removeParent(self,widgetID,parentID):
        if (widgetID not in self._widgets) or (parentID not in self._widgets):
            print('ERROR: node all nodes are registered')
        else:
            if parentID in self._widgets[widgetID]['parents']:
                self._widgets[widgetID]['parents'].remove(parentID)
            if widgetID in self._children[parentID]:
                self._children[parentID].remove(widgetID)
            self.updateDag()

    def _removeNode(self,_id):        
        if _id in self._widgets:            
            #children                    
            for key in self._widgets[_id]['parents']:
                index = self._children[key].index(_id)
                #it should be always >= 0                
                self._children[key].pop(index)                
            
            #widgets            
            while len(self._children[_id]) > 0:                
                self.removeNode(self._children[_id][0])
            #summaries
            if _id in self._summaries:
                self._summaries.pop(_id)
            if _id in self._children:
                self._children.pop(_id)
            self._widgets.pop(_id)

    def removeNode(self,_id):        
        self._removeNode(_id)        
        self.updateDag()

    def clear(self):
        self._widgets = {}
        self._summaries = {}
        self._children = {}  
        self._attRqs = {}
        #
        self.updateDag()

    def updateSummary(self, internalID, summaryValues):            
        self._summaries[internalID] = summaryValues  
        self.summaries = json.dumps(self._summaries)          

    def requestAttention(self, internalID, entityType, eventType, description=""):                
        # if internalID not in self._attRqs:
        #     self._attRqs[internalID] = {}
        # #
        # self._attRqs[internalID][eventType] = {'entityType':entityType,'widgetID':internalID,'type':eventType,'description':description}        
        # self.attentionRequests = json.dumps(self._attRqs)
        #        
        self.attentionRequests = json.dumps({'op':'add','entityType':entityType,'widgetID':internalID,'type':eventType,'description':description})
 
    def removeRequestAttention(self, internalID, entityType, eventType):
        # #
        # if (internalID in self._attRqs) and (eventType in self._attRqs[internalID]):
        #     self._attRqs[internalID].pop(eventType, None)    
        # #
        # if (internalID in self._attRqs) and (len(self._attRqs[internalID]) == 0):
        #     self._attRqs.pop(internalID, None)
        # #
        # self.attentionRequests = json.dumps(self._attRqs)
        #
        self.attentionRequests = json.dumps({'op':'remove','entityType':entityType,'widgetID':internalID,'type':eventType})
        

    def updateDag(self):
        obj = []        
        summaryVariables = {}
        for _id in self._widgets:
            obj.append({'id':_id,'divID':self._widgets[_id]['referenceDiv'],'label':self._widgets[_id]['label'],'parentIds':self._widgets[_id]['parents']})
            summaryVariables[_id] = self._widgets[_id]['summaryVariables']

        #
        self.dag = json.dumps({'dag':obj,'summaries':self._summaries,'summaryVariables':summaryVariables})